import os
import sys
import subprocess
import shutil

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    os.chdir(BASE_DIR)
    
    print("=" * 65)
    print(" [*] Building Standalone Package for ApkRenamer Studio GUI")
    print("=" * 65)
    
    dist_dir = os.path.join(BASE_DIR, "dist")
    output_app_dir = os.path.join(dist_dir, "ApkRenamerGUI")
    core_src = os.path.join(BASE_DIR, "core")
    
    # 1. Run PyInstaller
    assets_src = os.path.join(BASE_DIR, "assets")
    sep = ";" if sys.platform == "win32" else ":"
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=ApkRenamerGUI",
        "--noconsole",
        "--clean",
        "--noconfirm",
        f"--add-data={assets_src}{sep}assets",
        "--collect-all=customtkinter",
        "--collect-all=PIL",
        os.path.join(BASE_DIR, "main.py")
    ]
    
    print("[*] Compiling Python GUI with PyInstaller...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"\n[-] PyInstaller compilation failed with code {res.returncode}")
        sys.exit(res.returncode)

    # 2. Ensure core engine dependencies (Java tools, binaries, keys) are copied cleanly into the dist app folder
    print("\n[*] Bundling core engine dependencies (Java tools, binaries, keys)...")
    core_dest = os.path.join(output_app_dir, "core")
    os.makedirs(core_dest, exist_ok=True)

    # Copy only necessary runtime components (ignore temp and cache)
    jar_src = os.path.join(core_src, "renamer.jar")
    if os.path.exists(jar_src):
        shutil.copy2(jar_src, os.path.join(core_dest, "renamer.jar"))

    for sub in ["bin", "keys"]:
        sub_src = os.path.join(core_src, sub)
        sub_dest = os.path.join(core_dest, sub)
        if os.path.exists(sub_dest):
            shutil.rmtree(sub_dest)
        if os.path.exists(sub_src):
            shutil.copytree(sub_src, sub_dest)

    for empty_folder in ["in", "out", "icon"]:
        os.makedirs(os.path.join(core_dest, empty_folder), exist_ok=True)

    # 3. Copy bundled assets (Fonts: Tajawal, etc.)
    print("[*] Bundling UI assets and Tajawal fonts...")
    assets_dest = os.path.join(output_app_dir, "assets")
    if os.path.exists(assets_dest):
        shutil.rmtree(assets_dest)
    if os.path.exists(assets_src):
        shutil.copytree(assets_src, assets_dest)

    # 4. Create a quick launcher batch file inside dist
    quick_run_bat = os.path.join(output_app_dir, "Start_ApkRenamer.bat")
    with open(quick_run_bat, "w", encoding="utf-8") as f:
        f.write('@echo off\ncd /d "%~dp0"\nstart ApkRenamerGUI.exe\n')

    # 4. Copy README into dist
    readme_src = os.path.join(BASE_DIR, "README.md")
    if os.path.exists(readme_src):
        shutil.copy(readme_src, os.path.join(output_app_dir, "README.txt"))

    print("\n" + "=" * 65)
    print("[+] Build Completed Successfully!")
    print(f"[*] Package Directory: {output_app_dir}")
    print(f"[*] Executable:        {os.path.join(output_app_dir, 'ApkRenamerGUI.exe')}")
    print("=" * 65)

if __name__ == "__main__":
    build()
