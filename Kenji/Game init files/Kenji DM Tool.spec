# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('ttrpg_game_engine.py', '.'), ('gamemode.py', '.'), ('_dm_turn.py', '.'), ('continuity_engine.py', '.'), ('trigger_engine.py', '.'), ('chapter_close.py', '.'), ('generate_starter_campaign.py', '.'), ('engine_v2.py', '.'), ('run_arc_pointer.py', '.'), ('_strip_dm_notes.py', '.'), ('prose_state_extractor.py', '.'), ('play_engine.py', '.'), ('character_compute.py', '.'), ('character_tracker.md', '.'), ('dm_rules_tracking.md', '.'), ('DM_TURN_PROTOCOL.md', '.'), ('SESSION_MEMORY.md', '.'), ('tracking_rules.md', '.'), ('npc_name_bank.md', '.'), ('world_calendar_lore.md', '.'), ('AI_CONTEXT.md', '.'), ('manifests', 'manifests')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('anthropic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['kenji_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Kenji DM Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
