@echo off
chcp 65001 >nul
title Tesseract 資料夾精簡工具

echo.
echo ═══════════════════════════════════════════════════════
echo   Tesseract 資料夾精簡工具
echo   移除不需要的檔案，縮小容量到原本的 1/8
echo ═══════════════════════════════════════════════════════
echo.
echo ⚠️  此操作會刪除以下內容：
echo    • 中文、日文、韓文語言包（保留英文）
echo    • 訓練工具（只保留 OCR 執行檔）
echo    • 文檔和說明檔案
echo.
echo ✅ 保留內容：
echo    • tesseract.exe（OCR 引擎）
echo    • 所有 DLL 檔案（必要）
echo    • eng.traineddata（英文語言包）
echo.
echo 預計可節省約 350 MB 空間
echo.
pause
echo.

python 精簡_tesseract.py

if errorlevel 1 (
    echo.
    echo ❌ 精簡過程發生錯誤
    echo.
    pause
    exit /b 1
)

echo.
echo 完成！
pause
