@echo off
chcp 65001 > nul
echo ================================================
echo           CL_Scan 簡化打包工具
echo           (英文辨識專用版)
echo ================================================
echo.
echo 正在打包程式...
echo.

python simple_build.py
if errorlevel 1 (
    echo.
    echo ❌ 打包失敗
    pause
    exit /b 1
)

echo.
echo 🎉 打包完成！
echo.
echo 程式已準備完成，可以分享給其他人使用
pause
exit /b 0