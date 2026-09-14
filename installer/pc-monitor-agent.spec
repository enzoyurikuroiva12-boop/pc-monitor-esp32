from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('psutil')
a = Analysis(['../agent/pc_monitor_agent.py'], pathex=['../agent'], hiddenimports=hiddenimports, datas=[('../web','web')], excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='PCMonitorAgent', console=False, icon=None)
