@echo off
cd /d "%~dp0"
if exist PCMonitorAgent.exe (start "PC Monitor" PCMonitorAgent.exe) else (py -3 ..\agent\pc_monitor_agent.py)
start http://127.0.0.1:8765
