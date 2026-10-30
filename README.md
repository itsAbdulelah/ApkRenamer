# ApkRenamer Studio (GUI & CLI)

A modern Android APK customizer, cloner, and renamer. Supports changing app names, package IDs, and app icons with deep renaming for dual/side-by-side installations.

Includes both the original command-line core and the new **Crystal Glass Bilingual GUI** with Google Font **Tajawal**.

---

## 📸 Screenshots (معاينة الواجهة)

### Arabic Interface - Dark Theme (الواجهة العربية - النمط الداكن)
![Arabic Dark Interface](assets/screenshots/preview_ar_dark.png)

### Light Theme (النمط الفاتح البلوري)
![Arabic Light Interface](assets/screenshots/preview_ar_light.png)

### English Interface - LTR (الواجهة الإنجليزية)
![English Interface](assets/screenshots/preview_en_dark.png)

---

## 🌟 New Features in this Fork (GUI Edition)
- **Crystal Glass Interface:** Modern frosted glass design with dark/light themes.
- **Bilingual with Native RTL & LTR:** Toggle between Arabic and English with full right-to-left and left-to-right adaptive layout.
- **Random Package ID Generator (🎲):** Generate valid Android package IDs with one click.
- **Keep Original Icon:** Toggle to keep the original APK icon or provide a new PNG with live preview.
- **Windows Unicode Fix:** Native 8.3 short-path resolution preventing `aapt2` path errors on non-ASCII paths.
- **Standalone One-Click Export:** Compile directly to standalone `.exe` with `build_exe.py`.

---

## 🚀 Running the GUI

### Option 1: Quick Launch (Windows)
Double-click:
```bat
run.bat
```

### Option 2: Python Command
```bash
pip install -r requirements.txt
python main.py
```

### Option 3: Build Standalone Executable (.EXE)
```bash
python build_exe.py
```
Executable will be placed in `dist/ApkRenamerGUI/ApkRenamerGUI.exe`.

---

## 💻 CLI Usage (Original Engine)
```bash
java -jar core/renamer.jar [-a] <path/to/app.apk> [-o] <path/to/renamed.apk> [-n] <new_name> [-p] <new.package.name> [-i] <new_icon.png>
```

- `[-d]`: Deep renaming (search and replace old package in smali to allow side-by-side install).
- `[-t]`: Extract all apk resources to temp folder for manual changes.
- `[-m]`: Skip resource modification.
- `[-da]`: Decode arguments for Apktool (e.g. `-da "--keep-broken-res"`).
- `[-ba]`: Build arguments for Apktool (e.g. `-ba "--use-aapt2"`).
- `[-r] <path/to/dict.txt>`: Dictionary replacement.

---

## 📋 Requirements
- **Java (JRE 8 or newer)** in system PATH.
- **Python 3.8+** (for running from source or building the executable).

---

## 📜 Credits & Third-Party Components
- Original Core: [dvaoru/ApkRenamer](https://github.com/dvaoru/ApkRenamer)
- [Apktool](https://github.com/iBotPeaches/Apktool)
- [Apk Sign](https://github.com/appium/sign)
- [Thumbnailator](https://github.com/coobird/thumbnailator)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
