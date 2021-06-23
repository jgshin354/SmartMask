# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['DGMIF_PPG_v0.py'],
             pathex=['C:\\Users\\jgshi\\Documents\\GitHub\\SmartMask\\Python_BLE_Pycharm_QT5_pyinstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='DGMIF_PPG_v0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='DGMIF_PPG_v0')
