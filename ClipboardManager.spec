# -*- mode: python ; coding: utf-8 -*-
# 优化版打包配置：
#  - 只保留 QtCore / QtGui / QtWidgets，剔除 Qml/Quick/Pdf/Svg/Network 等未使用模块
#  - 过滤掉随之被收集的 Qt DLL、无用插件和 opengl32sw.dll（软件 OpenGL 回退，19MB）
#  - optimize=2 编译字节码（去掉 assert 和 docstring）
#  - UPX 压缩所有 DLL/pyd（体积可再降约 50-60%）

# 未使用的 PySide6 子模块（Python 绑定层面剔除）
EXCLUDED_MODULES = [
    'pynput',
    # 程序无网络功能，剔除 ssl/hashlib（可连带去掉 libssl/libcrypto，约 1.8MB）
    'ssl', '_ssl', 'hashlib', '_hashlib',
    'PySide6.Qt3DAnimation', 'PySide6.Qt3DCore', 'PySide6.Qt3DExtras',
    'PySide6.Qt3DInput', 'PySide6.Qt3DLogic', 'PySide6.Qt3DQuick',
    'PySide6.Qt3DRender', 'PySide6.QtBluetooth', 'PySide6.QtCharts',
    'PySide6.QtConcurrent', 'PySide6.QtDataVisualization', 'PySide6.QtDBus',
    'PySide6.QtDesigner', 'PySide6.QtGraphs', 'PySide6.QtGraphsWidgets',
    'PySide6.QtHelp', 'PySide6.QtHttpServer', 'PySide6.QtLocation',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtNetwork',
    'PySide6.QtNetworkAuth', 'PySide6.QtNfc', 'PySide6.QtOpenGL',
    'PySide6.QtOpenGLWidgets', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
    'PySide6.QtPositioning', 'PySide6.QtPrintSupport', 'PySide6.QtQml',
    'PySide6.QtQuick', 'PySide6.QtQuick3D', 'PySide6.QtQuickControls2',
    'PySide6.QtQuickTest', 'PySide6.QtQuickWidgets', 'PySide6.QtRemoteObjects',
    'PySide6.QtScxml', 'PySide6.QtSensors', 'PySide6.QtSerialBus',
    'PySide6.QtSerialPort', 'PySide6.QtSpatialAudio', 'PySide6.QtSql',
    'PySide6.QtStateMachine', 'PySide6.QtSvg', 'PySide6.QtSvgWidgets',
    'PySide6.QtTest', 'PySide6.QtTextToSpeech', 'PySide6.QtUiTools',
    'PySide6.QtVirtualKeyboard', 'PySide6.QtWebChannel',
    'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineQuick',
    'PySide6.QtWebEngineWidgets', 'PySide6.QtWebSockets', 'PySide6.QtWebView',
    'PySide6.QtXml',
]

# 二进制文件名称/路径关键词（命中即剔除，大小写不敏感）
DROP_KEYWORDS = [
    'opengl32sw',           # 软件 OpenGL 回退，约 19MB，本程序不用 OpenGL
    'qt6qml', 'qt6quick', 'qt6pdf', 'qt6svg', 'qt6network',
    'qt6virtualkeyboard', 'qt6opengl', 'qt6multimedia', 'qt6webengine',
    'qt6webchannel', 'qt6websockets', 'qt6webview', 'qt6positioning',
    'qt6sensors', 'qt6serial', 'qt6bluetooth', 'qt6sql', 'qt6test',
    'qt6xml', 'qt6dbus', 'qt6designer', 'qt6help', 'qt6charts',
    'qt6datavisualization', 'qt63d', 'qt6printsupport', 'qt6texttospeech',
    'qt6uitools', 'qt6statemachine', 'qt6scxml', 'qt6remoteobjects',
    'qt6concurrent', 'qt6spatialaudio', 'qt6graphs', 'qt6httpserver',
    'qt6location', 'qt6nfc', 'qt6shadertools', 'qt6labs',
    'avcodec', 'avformat', 'avutil', 'swscale', 'swresample',
    'libcrypto', 'libssl',
    'platforminputcontexts',          # 虚拟键盘插件（依赖 Qml）
    'plugins/tls', 'plugins/networkinformation', 'plugins/bearer',
    'plugins/imageformats',           # 历史图片仅 PNG（Qt6Gui 内置），无需插件
    'qdirect2d', 'qminimal', 'qoffscreen',  # 只保留 qwindows 平台插件
]

# 只保留中文/英文翻译（界面文案均为代码内中文，Qt 自带翻译几乎用不到）
KEEP_QM = ('qtbase_zh_cn', 'qt_zh_cn', 'qtbase_en', 'qt_en')


def _keep(entry):
    name = entry[0].lower().replace('\\', '/')
    if 'translations/' in name and name.endswith('.qm'):
        base = name.rsplit('/', 1)[-1][:-3]
        return base in KEEP_QM
    return not any(k in name for k in DROP_KEYWORDS)


a = Analysis(
    ['clipboard_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('history_store.py', '.'), ('clipboard_watcher.py', '.'), ('search_window.py', '.'), ('global_hotkey.py', '.'), ('autostart.py', '.'), ('config.py', '.'), ('settings_dialog.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDED_MODULES,
    noarchive=False,
    optimize=2,
)

a.binaries = [b for b in a.binaries if _keep(b)]
a.datas = [d for d in a.datas if _keep(d)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ClipboardManager',
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
    icon=['clipboard_icon.ico'],
)
