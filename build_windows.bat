@echo off
setlocal

REM clean old builds
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q RDPPatcher.spec 2>nul

REM build the EXE
pyinstaller ^
  --onefile ^
  --manifest resources/admin.manifest ^
  --paths src ^
  --add-data "resources/*;resources" ^
  --add-binary "bin/*;bin" ^
  --name RDPPatcher ^
  src/rdppatcher/__main__.py 

echo.
echo Build complete!
echo.

endlocal
pause
