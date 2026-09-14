@echo off
setlocal
cd /d "%~dp0.."
py -3 -m venv agent\.venv
call agent\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r agent\requirements.txt
start "PC Monitor Agent" /min python agent\pc_monitor_agent.py
start http://127.0.0.1:8765
echo Agente iniciado. Para iniciar com o Windows, crie um atalho deste arquivo na pasta shell:startup.
pause
