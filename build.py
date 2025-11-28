#!/usr/bin/env python
"""
一鍵打包 CL_Scan
直接執行: python build.py
"""
import os
import sys
import shutil
import subprocess

def main():
    # 確保在正確的目錄
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    print("=" * 60)
    print("CL_Scan 一鍵打包工具")
    print("=" * 60)

    # 檢查必要檔案
    required_files = ['ocr_tool.py', 'CL_Scan.ico']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要檔案: {file}")
            input("按 Enter 退出...")
            sys.exit(1)

    # 檢查並取得圖示絕對路徑
    icon_path = os.path.abspath('CL_Scan.ico')
    print(f"✓ 找到圖示檔案: {icon_path}")

    # 檢查 Tesseract 安裝
    tesseract_path = r'C:\Program Files\Tesseract-OCR'
    if not os.path.exists(tesseract_path):
        print("❌ 錯誤：找不到 Tesseract-OCR")
        print(f"   請確認已安裝在: {tesseract_path}")
        print("   下載位置: https://github.com/UB-Mannheim/tesseract/wiki")
        input("按 Enter 退出...")
        sys.exit(1)

    tesseract_exe = os.path.join(tesseract_path, 'tesseract.exe')
    tessdata_path = os.path.join(tesseract_path, 'tessdata')
    eng_file = os.path.join(tessdata_path, 'eng.traineddata')

    if not os.path.exists(eng_file):
        print("❌ 錯誤：找不到英文語言包")
        print(f"   請確認存在: {eng_file}")
        print("   請重新安裝 Tesseract 並確保勾選英文語言包")
        input("按 Enter 退出...")
        sys.exit(1)

    print("✓ 找到 Tesseract 執行檔")
    print("✓ 找到英文語言包")

    # 執行 PyInstaller
    print("\n正在執行 PyInstaller...")
    cmd = [
        'pyinstaller',
        'ocr_tool.py',
        '--onedir',
        '--windowed',
        '--name=CL_Scan',
        f'--icon={icon_path}',  # 主圖示設定
        f'--add-data={icon_path};.',  # 將圖示檔案打包進程式
        '--clean',
        '--noconfirm',
        '--distpath=dist',  # 明確指定輸出路徑
        '--workpath=build',  # 明確指定工作路徑
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=PIL.Image',
        '--hidden-import=PIL.ImageTk',
        '--hidden-import=pytesseract',
        '--hidden-import=pyperclip',
        '--hidden-import=customtkinter',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=pytest',
        '--exclude-module=setuptools',
        '--noupx',
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ PyInstaller 執行成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 執行失敗: {e}")
        print(f"錯誤訊息: {e.stderr}")
        input("按 Enter 退出...")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 找不到 PyInstaller，請先安裝:")
        print("   pip install pyinstaller")
        input("按 Enter 退出...")
        sys.exit(1)

    print("\\n" + "=" * 60)
    print("設定 Tesseract 環境...")
    print("=" * 60)

    # 建立發布資料夾
    dist_folder = os.path.join(script_dir, "dist")
    release_folder = os.path.join(script_dir, "release")

    if os.path.exists(release_folder):
        shutil.rmtree(release_folder)
    os.makedirs(release_folder)

    # 複製打包好的程式
    exe_folder = os.path.join(dist_folder, "CL_Scan")
    if not os.path.exists(exe_folder):
        print(f"❌ 打包失敗：找不到 {exe_folder}")
        input("按 Enter 退出...")
        sys.exit(1)

    release_app_folder = os.path.join(release_folder, "CL_Scan")
    shutil.copytree(exe_folder, release_app_folder)
    print(f"✓ 程式已複製到: {release_app_folder}")
    
    # 確保圖示檔案在正確位置
    icon_dest = os.path.join(release_app_folder, 'CL_Scan.ico')
    if not os.path.exists(icon_dest):
        shutil.copy2(icon_path, icon_dest)
        print(f"✓ 圖示檔案已複製到: {icon_dest}")

    # 建立 tesseract 資料夾並複製必要檔案
    tesseract_dest = os.path.join(release_app_folder, "tesseract")
    os.makedirs(tesseract_dest, exist_ok=True)

    # 複製 tesseract.exe 和相關 DLL
    print("正在複製 Tesseract 執行檔...")
    copied_files = []
    for file in os.listdir(tesseract_path):
        src = os.path.join(tesseract_path, file)
        if os.path.isfile(src) and (file.endswith('.exe') or file.endswith('.dll')):
            dest = os.path.join(tesseract_dest, file)
            shutil.copy2(src, dest)
            copied_files.append(file)
            print(f"  ✓ 複製: {file}")

    if not copied_files:
        print("❌ 警告：沒有複製到任何 Tesseract 檔案")
    else:
        print(f"✓ 成功複製 {len(copied_files)} 個檔案")

    # 建立 tessdata 資料夾並只複製英文語言包
    tessdata_dest = os.path.join(tesseract_dest, "tessdata")
    os.makedirs(tessdata_dest, exist_ok=True)
    eng_dest = os.path.join(tessdata_dest, 'eng.traineddata')
    shutil.copy2(eng_file, eng_dest)
    print("✓ 英文語言包已安裝")

    # 驗證關鍵檔案是否存在
    verify_files = [
        (os.path.join(tesseract_dest, 'tesseract.exe'), 'Tesseract 執行檔'),
        (eng_dest, '英文語言包'),
        (os.path.join(release_app_folder, 'CL_Scan.ico'), '圖示檔案'),
        (os.path.join(release_app_folder, 'CL_Scan.exe'), '主程式')
    ]

    print("\\n驗證關鍵檔案...")
    for file_path, file_name in verify_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_name}: {file_path}")
        else:
            print(f"  ❌ {file_name}: {file_path} (遺失)")

    # 建立使用說明
    readme_path = os.path.join(release_app_folder, "使用說明.txt")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""
CL_Scan - 文字辨識工具
=====================

使用方法：
1. 雙擊 CL_Scan.exe 啟動程式
2. 點擊「截圖辨識」按鈕
3. 拖曳滑鼠選取要辨識的文字區域
4. 等待辨識完成
5. 點擊結果文字框可複製到剪貼簿

注意事項：
• 本程式僅支援英文、數字、符號辨識
• 請確保截圖區域文字清晰
• 按 ESC 鍵可取消截圖選取

問題排除：
如果程式無法啟動或辨識失敗，請確認：
1. tesseract 資料夾位於程式目錄中
2. tessdata 資料夾包含 eng.traineddata 檔案
3. Windows 防毒軟體未阻擋程式執行

""")

    print("\n" + "=" * 60)
    print("🎉 打包完成！")
    print("=" * 60)
    
    # 清除 Windows 圖示快取，確保顯示正確圖示
    print("\n正在清除 Windows 圖示快取...")
    try:
        # 清除圖示快取
        subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], 
                      capture_output=True, check=False)
        subprocess.run(['del', '/a', '/q', 
                       os.path.expandvars('%localappdata%\\IconCache.db')], 
                      shell=True, capture_output=True, check=False)
        subprocess.run(['del', '/a', '/f', '/q', 
                       os.path.expandvars('%localappdata%\\Microsoft\\Windows\\Explorer\\iconcache*')], 
                      shell=True, capture_output=True, check=False)
        subprocess.run(['start', 'explorer.exe'], shell=True, check=False)
        print("✓ 圖示快取已清除，重新啟動 Windows 檔案總管")
    except Exception as e:
        print(f"⚠️ 無法自動清除圖示快取: {e}")
        print("請手動重新啟動檔案總管或重開機")
    
    print(f"程式位置：{release_app_folder}")
    print("檔案結構：")
    print("  CL_Scan/")
    print("  ├── CL_Scan.exe      (主程式)")
    print("  ├── CL_Scan.ico      (圖示)")
    print("  ├── 使用說明.txt      (說明文件)")
    print("  ├── tesseract/       (OCR 引擎)")
    print("  │   ├── tesseract.exe")
    print("  │   ├── *.dll")
    print("  │   └── tessdata/")
    print("  │       └── eng.traineddata")
    print("  └── _internal/       (程式庫)")
    
    print("\n⚠️ 重要提示：")
    print("如果圖示仍無法正常顯示，請：")
    print("1. 重新啟動檔案總管 (Ctrl+Shift+Esc 開啟工作管理員，結束 explorer.exe，再執行)")
    print("2. 或者直接重開機")
    print("3. 或者手動刪除目錄並重新建立")

    print("\n按任意鍵開啟資料夾...")
    input()
    
    try:
        # 使用更安全的方式開啟資料夾
        subprocess.run(['explorer', release_app_folder], check=True)
    except:
        try:
            os.startfile(release_app_folder)
        except:
            print(f"請手動開啟資料夾: {release_app_folder}")

if __name__ == "__main__":
    main()