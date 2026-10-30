import os
import sys
import shutil
import ctypes
import subprocess
import threading
from typing import Callable, Optional, Dict, Any


def to_short_path(path: str) -> str:
    """Convert any Windows path to 8.3 short path (pure ASCII).
    Critical on Windows when username or path contains Arabic/Unicode characters,
    as native C++ tools like aapt2.exe fail to open non-ASCII directories.
    """
    if sys.platform != "win32" or not path:
        return path
    try:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            buf = ctypes.create_unicode_buffer(500)
            res = ctypes.windll.kernel32.GetShortPathNameW(abs_path, buf, 500)
            if res > 0:
                return buf.value
        else:
            parent = os.path.dirname(abs_path)
            base = os.path.basename(abs_path)
            if os.path.exists(parent):
                buf = ctypes.create_unicode_buffer(500)
                res = ctypes.windll.kernel32.GetShortPathNameW(parent, buf, 500)
                if res > 0:
                    return os.path.join(buf.value, base)
    except Exception:
        pass
    return os.path.abspath(path)


def get_core_dir() -> str:
    """Return the absolute path to core directory containing renamer.jar, bin, and keys.
    Robustly handles running from source, PyInstaller onedir, or PyInstaller onefile.
    """
    candidates = []

    # 1. Next to the executable (standard portable distribution)
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "core"))
        candidates.append(exe_dir)
        # Check _internal or _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "core"))
            candidates.append(meipass)

    # 2. When running from Python script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, ".."))
    candidates.append(os.path.join(parent_dir, "core"))
    candidates.append(parent_dir)

    for c in candidates:
        if os.path.exists(os.path.join(c, "renamer.jar")):
            return c

    # Fallback to parent core if nothing matched
    return os.path.join(parent_dir, "core")


def check_java() -> tuple[bool, str]:
    """Check if Java is installed and accessible in system PATH."""
    try:
        proc = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        version_output = proc.stderr or proc.stdout
        first_line = version_output.strip().splitlines()[0] if version_output else "Java installed"
        return True, first_line
    except Exception as e:
        return False, str(e)


class ApkRenamerRunner:
    def __init__(
        self,
        on_log: Callable[[str, str], None],
        on_finish: Callable[[bool, str], None],
        on_status: Callable[[str], None]
    ):
        self.on_log = on_log
        self.on_finish = on_finish
        self.on_status = on_status
        self.process: Optional[subprocess.Popen] = None
        self._is_cancelled = False
        self._thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def run(self, params: Dict[str, Any]):
        if self.is_running():
            self.on_log("Process is already running!\n", "warning")
            return

        self._is_cancelled = False
        self._thread = threading.Thread(target=self._worker, args=(params,), daemon=True)
        self._thread.start()

    def cancel(self):
        self._is_cancelled = True
        if self.process and self.process.poll() is None:
            self.on_log("\n⚠️ Cancelling process...\n", "warning")
            try:
                self.process.terminate()
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def _worker(self, params: Dict[str, Any]):
        raw_core_dir = get_core_dir()
        core_dir = to_short_path(raw_core_dir)
        jar_path = to_short_path(os.path.join(raw_core_dir, "renamer.jar"))

        if not os.path.exists(jar_path):
            self.on_log(f"Error: renamer.jar not found at {jar_path}\n", "error")
            self.on_finish(False, "Missing renamer.jar")
            return

        # Clean old temp directory from previous runs to prevent stale build conflicts
        temp_dir = os.path.join(raw_core_dir, "temp")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

        home_dir = to_short_path(os.path.expanduser("~"))

        # Build command arguments with ASCII-safe paths
        cmd = [
            "java",
            f"-Duser.dir={core_dir}",
            f"-Duser.home={home_dir}",
            "-Dfile.encoding=UTF-8",
            "-jar",
            jar_path
        ]

        apk_in = params.get("apk_in")
        if apk_in:
            cmd.extend(["-a", to_short_path(apk_in)])

        apk_out = params.get("apk_out")
        if apk_out:
            cmd.extend(["-o", to_short_path(apk_out)])

        name = params.get("app_name")
        if name:
            cmd.extend(["-n", name])

        pack = params.get("package_name")
        if pack:
            cmd.extend(["-p", pack])

        keep_orig_icon = params.get("keep_original_icon", False)
        icon = params.get("icon_path")

        # Clean fallback icon directory to prevent accidental overwrite if keeping original
        icon_dir = os.path.join(raw_core_dir, "icon")
        if os.path.exists(icon_dir):
            for f in os.listdir(icon_dir):
                if f.lower().endswith((".png", ".jpg", ".jpeg")):
                    try:
                        os.remove(os.path.join(icon_dir, f))
                    except Exception:
                        pass

        if not keep_orig_icon and icon and os.path.exists(icon):
            cmd.extend(["-i", to_short_path(icon)])

        dictionary = params.get("dictionary_path")
        if dictionary:
            cmd.extend(["-r", to_short_path(dictionary)])

        if params.get("is_deep_rename"):
            cmd.append("-d")

        if params.get("decode_args"):
            cmd.extend(["-da", params["decode_args"]])

        if params.get("build_args"):
            cmd.extend(["-ba", params["build_args"]])

        self.on_status("Running...")
        self.on_log(f"Starting ApkRenamer engine...\n", "info")
        self.on_log(f"Working Directory: {core_dir}\n", "dim")
        self.on_log(f"Executing: {' '.join(cmd)}\n\n", "dim")

        startupinfo = None
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        # ASCII-safe environment for native aapt2/zipalign binaries
        env = os.environ.copy()
        if sys.platform == "win32":
            for var in ["TEMP", "TMP", "LOCALAPPDATA", "USERPROFILE", "APPDATA"]:
                val = env.get(var)
                if val:
                    env[var] = to_short_path(val)

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=core_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            # Stream output
            for line in iter(self.process.stdout.readline, ""):
                if self._is_cancelled:
                    break
                line_type = "normal"
                l_lower = line.lower()
                if "error" in l_lower or "exception" in l_lower or "fail" in l_lower:
                    line_type = "error"
                elif "success" in l_lower or "renamed" in l_lower or "signed" in l_lower or "done" in l_lower:
                    line_type = "success"
                elif "decod" in l_lower or "build" in l_lower or "align" in l_lower or "cop" in l_lower:
                    line_type = "info"

                self.on_log(line, line_type)

            self.process.stdout.close()
            return_code = self.process.wait()

            if self._is_cancelled:
                self.on_status("Cancelled")
                self.on_finish(False, "Process cancelled by user.")
                self.on_log("\n🛑 Process stopped by user.\n", "warning")
            elif return_code == 0:
                self.on_status("Finished Successfully")
                self.on_finish(True, "All operations completed successfully!")
                self.on_log("\n🎉 Process completed successfully!\n", "success")
            else:
                self.on_status(f"Exited with code {return_code}")
                self.on_finish(False, f"Process exited with error code {return_code}")
                self.on_log(f"\n❌ Process failed with return code {return_code}\n", "error")

        except Exception as ex:
            self.on_status("Error")
            self.on_finish(False, str(ex))
            self.on_log(f"\n❌ Unexpected error: {ex}\n", "error")
        finally:
            self.process = None
