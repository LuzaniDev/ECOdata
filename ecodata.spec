# -*- mode: python ; coding: utf-8 -*-

import os
import sys

# Spec runs from project root via pyinstaller ecodata.spec
project_root = os.path.abspath(".")
sys.path.insert(0, project_root)

block_cipher = None

a = Analysis(
    ['run_exe.py'],
    pathex=[str(project_root)],
    binaries=[
        ('firebird_dll\\*.dll', '.'),
    ],
    datas=[
        ('server/static', 'server/static'),
    ],
    hiddenimports=[
        # fdb – pure-python Firebird driver (no DLL needed)
        'fdb',
        # paramiko – SFTP client
        'paramiko',
        # uvicorn & sub-modules
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.middleware',
        'uvicorn.middleware.proxy_headers',
        'uvicorn.middleware.wsgi',
        # FastAPI & friends
        'fastapi',
        'fastapi.routing',
        'fastapi.openapi',
        'starlette',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.staticfiles',
        'pydantic',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext',
        'sqlalchemy.ext.declarative',
        # python-multipart
        'multipart',
        # Application packages
        'src',
        'src.db',
        'src.config',
        'src.generators',
        'src.generators.base',
        'src.generators.estoque',
        'src.generators.sellout',
        'src.generators.painel',
        'src.utils',
        'src.utils.file_utils',
        'src.sftp',
        'server',
        'server.api',
        'server.api.auditoria',
        'server.api.backup_api',
        'server.api.config',
        'server.api.debug_api',
        'server.api.files',
        'server.api.health',
        'server.api.logs_api',
        'server.api.scheduler',
        'server.core',
        'server.core.audit',
        'server.core.auditoria',

        'server.core.cleanup',
        'server.core.database',
        'server.core.debug_events',
        'server.core.executor',
        'server.core.log_core',
        'server.core.scheduler_core',
    ],
    hookspath=[],
    hooksconfig={},
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PIL.Image',
        'cryptography',
        'bcrypt',
        'nacl',
        'setuptools',
        'pip',
        'distutils',
        'wheel',
        '_tkinter',
        'test',
        'unittest',
        'http.server',
        'asyncio.__main__',
        'xmlrpc',
        'venv',
    ],
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ecodata',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
