@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python -m pip install -r requirements-build.txt
if errorlevel 1 goto fail
.venv\Scripts\python -m unittest discover -s tests -v
if errorlevel 1 goto fail
.venv\Scripts\python -m PyInstaller --clean --noconfirm --onefile --windowed --name TetrisWin11 main.py
if errorlevel 1 goto fail
echo Built: dist\TetrisWin11.exe
pause
exit /b 0
:fail
echo Build failed. See the error above.
pause
exit /b 1
