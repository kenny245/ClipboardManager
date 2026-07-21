#!/bin/bash
# ========================================
#   剪贴板管理器 - macOS 打包脚本
# ========================================
set -e

echo "========================================"
echo "  剪贴板管理器 - macOS 打包脚本"
echo "========================================"
echo ""

echo "[1/5] 安装依赖..."
pip3 install PySide6 pynput pyinstaller --quiet

echo "[2/5] 清理旧构建..."
rm -rf build dist ClipboardManager.spec

echo "[3/5] 创建 Info.plist..."
cat > Info.plist << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>ClipboardManager</string>
    <key>CFBundleDisplayName</key>
    <string>剪贴板管理器</string>
    <key>CFBundleIdentifier</key>
    <string>com.clipboardmanager.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <true/>
</dict>
</plist>
PLIST

echo "[4/5] 开始打包..."
pyinstaller --noconsole --onefile --windowed \
    --name "ClipboardManager" \
    --add-data "history_store.py:." \
    --add-data "clipboard_watcher.py:." \
    --add-data "search_window.py:." \
    --add-data "global_hotkey.py:." \
    --add-data "autostart.py:." \
    --hidden-import PySide6 \
    --hidden-import pynput \
    --osx-bundle-identifier "com.clipboardmanager.app" \
    clipboard_manager.py

echo "[5/5] 完成！"
echo ""
echo "输出文件: dist/ClipboardManager.app"
echo ""
echo "分享方式:"
echo "  1. 将 dist/ClipboardManager.app 压缩为 zip/dmg"
echo "  2. 发送给 macOS 用户"
echo "  3. 用户首次运行需在 系统偏好设置 > 安全性与隐私 中允许运行"
echo ""
echo "注意: macOS 上全局快捷键需要授予「辅助功能」权限"
echo "  系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能"
echo ""
