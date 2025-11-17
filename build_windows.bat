@echo off
setlocal

REM create venv if needed
if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
)

REM active venv
call venv\Scripts\activate.bat

REM install dependencies
echo Installing requirements...
pip install --upgrade pip >nul
pip install -r requirements.txt

REM clean old builds
echo Cleaning environment...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q RDPPatcher.spec 2>nul

REM build the EXE
echo Building RDPPatcher...
pyinstaller ^
  --onefile ^
  --manifest resources/admin.manifest ^
  --paths src ^
  --add-data "resources;resources" ^
  --add-data "bin;bin" ^
  --name RDPPatcher ^
  --uac-admin ^
  --windowed ^
  src/rdppatcher/__main__.py 

echo.
echo Build complete!
echo.

endlocal
pause
