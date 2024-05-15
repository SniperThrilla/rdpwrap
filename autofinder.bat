@ECHO OFF
ECHO [33mThis program automatically uses RDPWrapOffsetFinder by llccd for the default location of termsrv.dll. If termsrv.dll is not in C:\Windows\System32\termsrv.dll this will not work.[0m
ECHO: 
ECHO [33mAttempting to run RDPWrapOffsetFinder...[0m
cd %~dp0\OffsetFinder\
start /B /wait RDPWrapOffsetFinder.exe C:\Windows\System32\termsrv.dll > %~dp0\offsets.txt
ECHO:
ECHO [32mWritten to %~dp0offsets.txt![0m
PAUSE