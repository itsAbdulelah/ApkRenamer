@echo off
cd /d "%~dp0"
echo Starting ApkRenamer GUI...
start pythonw main.py
if %ERRORLEVEL% NEQ 0 (
    python main.py
)
