@echo off
REM Builds dist\CodeAgent.exe (single file, no Python needed on the target PC).
REM Run this on Windows with Python 3.10+ installed (only the BUILD machine needs Python).
setlocal
cd /d "%~dp0"
python -m venv .venv || goto :err
call .venv\Scripts\activate.bat || goto :err
python -m pip install --upgrade pip || goto :err
pip install -r requirements-dev.txt || goto :err
python -m pytest -q || goto :err
pyinstaller --noconfirm --clean --onefile --windowed --name CodeAgent --collect-all certifi main.py || goto :err
echo.
echo BUILD OK  ->  %cd%\dist\CodeAgent.exe
exit /b 0
:err
echo BUILD FAILED
exit /b 1
