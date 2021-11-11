# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['C:\\Users\\wilso\\PycharmProjects\\Financial_Flask\\calculations\\logic\\FunctionBollingBand.py'],
             pathex=['C:\\Users\\wilso\\PycharmProjects\\Financial_Flask\\app_file\\FunctionBollingBand'],
             binaries=[],
             datas=[],
             hiddenimports=['talib.stream', 'logging.handlers', 'cx_Oracle', 'joblib'],
             hookspath=[],
             hooksconfig={},
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
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='FunctionBollingBand',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
