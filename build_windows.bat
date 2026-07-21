@echo off
chcp 65001 >nul
echo ========================================
echo   剪贴板管理器 - Windows 打包脚本
echo ========================================
echo.

echo [1/3] 安装打包依赖...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo 安装 pyinstaller 失败！
    pause
    exit /b 1
)

echo [2/3] 清理旧构建...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/3] 开始打包（使用优化版 spec + UPX 压缩）...
pyinstaller --noconfirm --clean --upx-dir tools\upx ClipboardManager.spec

if errorlevel 1 (
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo 完成！输出文件: dist\ClipboardManager.exe
echo.
echo 你可以将 ClipboardManager.exe 分享给其他 Windows 10/11 用户。
echo 用户运行后会自动设置开机自启动。
echo.
pause
