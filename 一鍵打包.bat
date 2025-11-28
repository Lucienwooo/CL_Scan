@echo off
chcp 65001 >nul
title CL_Scan 一鍵打包工具

echo.
echo ═══════════════════════════════════════════════════════
echo   CL_Scan 一鍵打包工具
echo   適用於完全全新的電腦（無需安裝任何軟體）
echo ═══════════════════════════════════════════════════════
echo.
echo 正在啟動打包程式...
echo.

python 一鍵打包_完整版.py

if errorlevel 1 (
    echo.
    echo ❌ 打包過程發生錯誤
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 打包完成！
echo.
pause
