@ECHO OFF
call autofinder.bat
cd %~dp0\dist\
start /B /wait ini-changer.exe