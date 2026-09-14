@echo off
setlocal
cd /d "%~dp0.."
py -3 -m pip install -r agent\requirements.txt
py -3 -m PyInstaller --clean installer\pc-monitor-agent.spec
mkdir dist\PCMonitorPortable 2>nul
copy dist\PCMonitorAgent.exe dist\PCMonitorPortable\
copy installer\run_portable.bat dist\PCMonitorPortable\
copy README.md dist\PCMonitorPortable\
echo Pacote pronto em dist\PCMonitorPortable
pause
