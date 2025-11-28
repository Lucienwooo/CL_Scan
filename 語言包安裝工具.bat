@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM ====================================
REM CL_Scan 語言包自動安裝工具
REM ====================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║      CL_Scan 語言包自動安裝工具                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM 取得當前目錄
set "CURRENT_DIR=%~dp0"
set "TESSDATA_DIR=%CURRENT_DIR%tessdata"
set "TEMP_DIR=%TEMP%\CL_Scan_LangPack"

REM GitHub Release URL
set "RELEASE_URL=https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0"

echo 語言包安裝路徑: %TESSDATA_DIR%
echo.

REM 檢查 tessdata 資料夾
if not exist "%TESSDATA_DIR%" (
    echo ❌ 錯誤：找不到 tessdata 資料夾
    echo    請確認本工具與 CL_Scan.exe 在同一資料夾中
    pause
    exit /b 1
)

REM 檢查已安裝的語言包
echo ════════════════════════════════════════════════════════
echo 檢查已安裝的語言包...
echo ════════════════════════════════════════════════════════
echo.

set "ENG_INSTALLED=false"
set "CHI_INSTALLED=false"
set "JPN_INSTALLED=false"
set "KOR_INSTALLED=false"

if exist "%TESSDATA_DIR%\eng.traineddata" (
    echo ✓ 英文 ^(eng^) - 已安裝
    set "ENG_INSTALLED=true"
) else (
    echo ✗ 英文 ^(eng^) - 未安裝
)

if exist "%TESSDATA_DIR%\chi_tra.traineddata" (
    echo ✓ 繁體中文 ^(chi_tra^) - 已安裝
    set "CHI_INSTALLED=true"
) else (
    echo ✗ 繁體中文 ^(chi_tra^) - 未安裝
)

if exist "%TESSDATA_DIR%\jpn.traineddata" (
    echo ✓ 日文 ^(jpn^) - 已安裝
    set "JPN_INSTALLED=true"
) else (
    echo ✗ 日文 ^(jpn^) - 未安裝
)

if exist "%TESSDATA_DIR%\kor.traineddata" (
    echo ✓ 韓文 ^(kor^) - 已安裝
    set "KOR_INSTALLED=true"
) else (
    echo ✗ 韓文 ^(kor^) - 未安裝
)

echo.
echo ════════════════════════════════════════════════════════
echo 請選擇要安裝的語言包：
echo ════════════════════════════════════════════════════════
echo.
echo    [1] 繁體中文 ^(chi_tra^) - 約 12 MB
echo    [2] 日文 ^(jpn^)          - 約 16 MB
echo    [3] 韓文 ^(kor^)          - 約 9 MB
echo    [4] 全部安裝              - 約 37 MB
echo    [0] 退出
echo.
set /p "choice=請輸入選項 (0-4): "

if "%choice%"=="0" goto END
if "%choice%"=="1" goto INSTALL_CHI
if "%choice%"=="2" goto INSTALL_JPN
if "%choice%"=="3" goto INSTALL_KOR
if "%choice%"=="4" goto INSTALL_ALL

echo.
echo ❌ 無效的選項，請重新執行
pause
exit /b 1

:INSTALL_CHI
echo.
echo ════════════════════════════════════════════════════════
echo 正在安裝繁體中文語言包...
echo ════════════════════════════════════════════════════════
call :DOWNLOAD_LANG "chi_tra"
if errorlevel 1 goto ERROR
goto SUCCESS

:INSTALL_JPN
echo.
echo ════════════════════════════════════════════════════════
echo 正在安裝日文語言包...
echo ════════════════════════════════════════════════════════
call :DOWNLOAD_LANG "jpn"
if errorlevel 1 goto ERROR
goto SUCCESS

:INSTALL_KOR
echo.
echo ════════════════════════════════════════════════════════
echo 正在安裝韓文語言包...
echo ════════════════════════════════════════════════════════
call :DOWNLOAD_LANG "kor"
if errorlevel 1 goto ERROR
goto SUCCESS

:INSTALL_ALL
echo.
echo ════════════════════════════════════════════════════════
echo 正在安裝所有語言包...
echo ════════════════════════════════════════════════════════
call :DOWNLOAD_LANG "chi_tra"
if errorlevel 1 goto ERROR
call :DOWNLOAD_LANG "jpn"
if errorlevel 1 goto ERROR
call :DOWNLOAD_LANG "kor"
if errorlevel 1 goto ERROR
goto SUCCESS

REM ====================================
REM 下載並安裝語言包函式
REM ====================================
:DOWNLOAD_LANG
set "LANG_CODE=%~1"
set "LANG_ZIP=CL_Scan_Lang_%LANG_CODE%.zip"
set "DOWNLOAD_URL=%RELEASE_URL%/%LANG_ZIP%"
set "ZIP_PATH=%TEMP_DIR%\%LANG_ZIP%"

REM 檢查是否已安裝
if exist "%TESSDATA_DIR%\%LANG_CODE%.traineddata" (
    echo.
    echo ⚠️  %LANG_CODE% 語言包已安裝
    set /p "OVERWRITE=是否要重新安裝？ (Y/N): "
    if /i not "!OVERWRITE!"=="Y" (
        echo    跳過 %LANG_CODE%
        exit /b 0
    )
)

echo.
echo [1/3] 準備下載...
REM 創建暫存資料夾
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo [2/3] 正在下載 %LANG_ZIP%...
echo       URL: %DOWNLOAD_URL%

REM 使用 PowerShell 下載檔案
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { $ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_PATH%' -UseBasicParsing; exit 0 } catch { Write-Host \"下載失敗: $_\"; exit 1 }}"

if errorlevel 1 (
    echo.
    echo ❌ 下載失敗
    echo    請檢查網路連線或確認 Release 是否存在
    exit /b 1
)

if not exist "%ZIP_PATH%" (
    echo.
    echo ❌ 下載的檔案不存在
    exit /b 1
)

echo       ✓ 下載完成

echo [3/3] 正在解壓縮並安裝...

REM 使用 PowerShell 解壓縮
powershell -Command "& {try { Expand-Archive -Path '%ZIP_PATH%' -DestinationPath '%TEMP_DIR%\extract_%LANG_CODE%' -Force; exit 0 } catch { Write-Host \"解壓縮失敗: $_\"; exit 1 }}"

if errorlevel 1 (
    echo.
    echo ❌ 解壓縮失敗
    exit /b 1
)

REM 複製語言包到 tessdata 資料夾
if exist "%TEMP_DIR%\extract_%LANG_CODE%\tessdata\%LANG_CODE%.traineddata" (
    copy /Y "%TEMP_DIR%\extract_%LANG_CODE%\tessdata\%LANG_CODE%.traineddata" "%TESSDATA_DIR%\" > nul
    if errorlevel 1 (
        echo.
        echo ❌ 安裝失敗：無法複製檔案
        exit /b 1
    )
    echo       ✓ 安裝完成
) else (
    echo.
    echo ❌ 語言包檔案格式錯誤
    exit /b 1
)

REM 清理暫存檔案
if exist "%ZIP_PATH%" del /F /Q "%ZIP_PATH%" > nul
if exist "%TEMP_DIR%\extract_%LANG_CODE%" rmdir /S /Q "%TEMP_DIR%\extract_%LANG_CODE%" > nul

exit /b 0

:SUCCESS
echo.
echo ════════════════════════════════════════════════════════
echo ✅ 語言包安裝完成！
echo ════════════════════════════════════════════════════════
echo.
echo 已安裝的語言包：
if exist "%TESSDATA_DIR%\eng.traineddata" echo   ✓ 英文
if exist "%TESSDATA_DIR%\chi_tra.traineddata" echo   ✓ 繁體中文
if exist "%TESSDATA_DIR%\jpn.traineddata" echo   ✓ 日文
if exist "%TESSDATA_DIR%\kor.traineddata" echo   ✓ 韓文
echo.
echo 💡 提示：
echo    - CL_Scan 會自動偵測已安裝的語言包
echo    - 重新啟動 CL_Scan 即可辨識對應語言的文字
echo    - 支援混合語言辨識（例如：中英混合）
echo.

REM 清理暫存資料夾
:CLEANUP
if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%" > nul

echo 按任意鍵啟動 CL_Scan...
pause > nul

REM 啟動 CL_Scan
if exist "%CURRENT_DIR%CL_Scan.exe" (
    start "" "%CURRENT_DIR%CL_Scan.exe"
) else (
    echo ⚠️  找不到 CL_Scan.exe
)
exit /b 0

:ERROR
echo.
echo ════════════════════════════════════════════════════════
echo ❌ 安裝失敗
echo ════════════════════════════════════════════════════════
echo.
echo 可能的原因：
echo   1. 網路連線問題
echo   2. GitHub Release 不存在或被移除
echo   3. 檔案權限問題
echo.
echo 請檢查後重試，或手動下載語言包：
echo %RELEASE_URL%
echo.
goto CLEANUP

:END
echo.
echo 已取消安裝
pause
exit /b 0
