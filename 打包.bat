@echo off
chcp 65001 > nul
echo ================================================
echo           CL_Scan 自動打包工具
echo ================================================
echo.
echo 請選擇打包模式：
echo.
echo [1] 模組化版本（推薦）- onedir 模式
echo     ✓ 內建 Tesseract-OCR 引擎
echo     ✓ 基礎版僅含英文（約 70 MB）
echo     ✓ 語言包獨立下載（繁中/日/韓）
echo     ✓ 拖放安裝，無需重新打包
echo.
echo [2] 輕量版 - onefile 模式
echo     ✓ 單一執行檔（約 25 MB）
echo     ✗ 需要使用者自行安裝 Tesseract
echo.
echo [3] 打包兩種版本
echo.
set /p choice="請輸入選項 (1/2/3): "

if "%choice%"=="1" goto BUILD_FULL
if "%choice%"=="2" goto BUILD_LITE
if "%choice%"=="3" goto BUILD_BOTH
echo 無效的選項，預設打包完整版
goto BUILD_FULL

:BUILD_FULL
echo.
echo ================================================
echo 正在打包模組化版本（基礎版 + 獨立語言包）
echo ================================================
echo.
python build_exe.py
if errorlevel 1 (
    echo.
    echo ❌ 模組化版本打包失敗
    pause
    exit /b 1
)
goto END

:BUILD_LITE
echo.
echo ================================================
echo 正在打包輕量版（onefile）
echo ================================================
echo.
python build_exe_lite.py
if errorlevel 1 (
    echo.
    echo ❌ 輕量版打包失敗
    pause
    exit /b 1
)
goto END

:BUILD_BOTH
echo.
echo ================================================
echo 正在打包模組化版本...
echo ================================================
echo.
python build_exe.py
if errorlevel 1 (
    echo ❌ 模組化版本打包失敗
    pause
    exit /b 1
)
echo.
echo ================================================
echo 正在打包輕量版...
echo ================================================
echo.
python build_exe_lite.py
if errorlevel 1 (
    echo ❌ 輕量版打包失敗
    pause
    exit /b 1
)
goto END

:END
echo.
echo ================================================
echo 🎉 所有打包完成！
echo ================================================
echo.
echo 已生成的檔案：
if "%choice%"=="1" (
    echo   ✓ release/CL_Scan/         - 主程式（基礎版）
    echo   ✓ release/language_packs/  - 語言包
    echo   ✓ CL_Scan_*.zip
)
if "%choice%"=="2" (
    echo   ✓ release_lite/     - 輕量版資料夾
    echo   ✓ CL_Scan_Lite_*.zip
)
if "%choice%"=="3" (
    echo   ✓ release/CL_Scan/         - 主程式（基礎版）
    echo   ✓ release/language_packs/  - 語言包
    echo   ✓ CL_Scan_*.zip
    echo   ✓ release_lite/     - 輕量版資料夾
    echo   ✓ CL_Scan_Lite_*.zip
)
echo.
echo 按任意鍵開啟發布資料夾...
pause > nul

REM 開啟資料夾
if "%choice%"=="1" start "" "%~dp0release"
if "%choice%"=="2" start "" "%~dp0release_lite"
if "%choice%"=="3" (
    start "" "%~dp0release"
    timeout /t 1 /nobreak > nul
    start "" "%~dp0release_lite"
)

exit /b 0
