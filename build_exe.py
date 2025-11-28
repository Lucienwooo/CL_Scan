"""
CL_Scan 打包腳本（模組化版本）
- 基礎版：onedir + Tesseract + 英文語言包
- 額外語言包：獨立 ZIP 檔，上傳到 GitHub Releases
- Language.bat：自動下載安裝工具

使用方式：
  python build_exe.py            # 只打包基礎版
  python build_exe.py --langs    # 打包基礎版 + 語言包
"""
import sys
import PyInstaller.__main__
import os
import shutil
import zipfile
from datetime import datetime

# 配置
GITHUB_RELEASE_URL = "https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0"

# 檢查命令列參數
BUILD_LANGS = '--langs' in sys.argv

# 確保在正確的目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Tesseract 路徑檢查
tesseract_path = r'C:\Program Files\Tesseract-OCR'
if not os.path.exists(tesseract_path):
    print("❌ 錯誤：找不到 Tesseract-OCR")
    print(f"   請確認已安裝在: {tesseract_path}")
    input("按 Enter 退出...")
    exit(1)

print("=" * 60)
if BUILD_LANGS:
    print("開始打包 CL_Scan（基礎版 + 語言包）")
else:
    print("開始打包 CL_Scan（基礎版）")
print("=" * 60)

# 準備打包 Tesseract
tessdata_path = os.path.join(tesseract_path, 'tessdata')
tesseract_exe = os.path.join(tesseract_path, 'tesseract.exe')

if not os.path.exists(tessdata_path):
    print(f"❌ 找不到語言包資料夾: {tessdata_path}")
    exit(1)

print(f"✓ 找到 Tesseract 引擎")
print(f"✓ 找到語言包資料夾")

# 檢查語言包
lang_files = {
    'eng.traineddata': '英文',
    'chi_tra.traineddata': '繁體中文',
    'jpn.traineddata': '日文',
    'kor.traineddata': '韓文'
}

print("\n檢查可用語言包：")
available_langs = {}
for lang_file, lang_name in lang_files.items():
    file_path = os.path.join(tessdata_path, lang_file)
    if os.path.exists(file_path):
        size_mb = os.path.getsize(file_path) / 1024 / 1024
        print(f"  ✓ {lang_name}: {size_mb:.1f} MB")
        available_langs[lang_file] = {'name': lang_name, 'path': file_path, 'size': size_mb}
    else:
        print(f"  ✗ {lang_name}: 未安裝")

if 'eng.traineddata' not in available_langs:
    print("\n❌ 錯誤：找不到英文語言包（必需）")
    exit(1)

print(f"\n將打包基礎版（僅含英文）")
print(f"額外語言包將生成獨立 ZIP 檔")

# 打包參數（僅包含 Tesseract 執行檔，不包含語言包）
PyInstaller.__main__.run([
    'ocr_tool.py',              # 主程式
    '--onedir',                  # 打包成資料夾（可包含外部檔案）
    '--windowed',                # 不顯示命令列視窗
    '--name=CL_Scan',            # 執行檔名稱
    '--clean',                   # 清理暫存檔
    '--noconfirm',               # 不詢問覆蓋
    f'--icon=app.ico',           # 設定圖示
    f'--add-data=app.ico;.',     # 將圖示檔案放入執行目錄 (供程式執行時讀取)
    # 打包 Tesseract 執行檔 (改為手動複製完整資料夾，確保 DLL 完整)
    # f'--add-binary={tesseract_exe};tesseract',
    # 添加所需的隱藏導入
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=pytesseract',
    '--hidden-import=pyperclip',
    '--hidden-import=customtkinter',
    # 排除不必要的模組（大幅縮小體積）
    '--exclude-module=numpy',           # customtkinter 不需要
    '--exclude-module=pandas',          # 不需要
    '--exclude-module=matplotlib',      # 不需要
    '--exclude-module=scipy',           # 不需要
    '--exclude-module=psutil',          # 不需要
    '--exclude-module=pyreadline3',     # 不需要
    '--exclude-module=pytest',          # 測試模組
    '--exclude-module=setuptools',      # 打包工具
    # 優化選項
    '--noupx',                          # 不使用 UPX 壓縮（避免誤報毒）
])

print("\n" + "=" * 60)
print("打包完成！")
print("=" * 60)

# 創建發布資料夾
dist_folder = os.path.join(script_dir, "dist")
release_folder = os.path.join(script_dir, "release")

if os.path.exists(release_folder):
    shutil.rmtree(release_folder)
os.makedirs(release_folder)

# 複製整個 onedir 資料夾
exe_folder = os.path.join(dist_folder, "CL_Scan")
if os.path.exists(exe_folder):
    release_app_folder = os.path.join(release_folder, "CL_Scan")
    shutil.copytree(exe_folder, release_app_folder)
    print(f"\n✓ 程式資料夾已複製到: {release_app_folder}")
    
    # 手動複製 Tesseract 完整執行環境 (包含 DLL)
    tesseract_dest_dir = os.path.join(release_app_folder, "tesseract")
    os.makedirs(tesseract_dest_dir, exist_ok=True)
    
    print("正在複製 Tesseract 執行檔與 DLL...")
    for item in os.listdir(tesseract_path):
        s = os.path.join(tesseract_path, item)
        d = os.path.join(tesseract_dest_dir, item)
        if os.path.isfile(s):
            # 只複製檔案 (exe, dll 等)，忽略資料夾 (如 tessdata, doc)
            shutil.copy2(s, d)

    # 檢查 Tesseract 是否成功打包
    tesseract_check = os.path.join(release_app_folder, "tesseract", "tesseract.exe")
    
    if os.path.exists(tesseract_check):
        print("✓ Tesseract 引擎已打包")
    else:
        print("⚠️ 警告：找不到 Tesseract 執行檔")
    
    # 清理重複的 DLL 檔案（優化體積）
    internal_folder = os.path.join(release_app_folder, "_internal")
    duplicate_dlls = [
        "libcrypto-3.dll",  # 保留 libcrypto-3-x64.dll
    ]
    for dll in duplicate_dlls:
        dll_path = os.path.join(internal_folder, dll)
        if os.path.exists(dll_path):
            os.remove(dll_path)
            print(f"✓ 已移除重複檔案: {dll}")
    
    # 創建 tessdata 資料夾並複製英文語言包
    # 修改：將 tessdata 放入 tesseract 資料夾內，符合 ocr_tool.py 的預期
    tessdata_dest = os.path.join(release_app_folder, "tesseract", "tessdata")
    os.makedirs(tessdata_dest, exist_ok=True)
    
    # 複製英文語言包（基礎必備）
    eng_src = available_langs['eng.traineddata']['path']
    eng_dest = os.path.join(tessdata_dest, 'eng.traineddata')
    shutil.copy(eng_src, eng_dest)
    print(f"✓ 已安裝英文語言包（基礎版）")
    
    # 複製語言包安裝工具（使用獨立的批次檔）
    lang_bat_src = os.path.join(script_dir, "語言包安裝工具.bat")
    if os.path.exists(lang_bat_src):
        lang_bat_dest = os.path.join(release_app_folder, "Language.bat")
        shutil.copy(lang_bat_src, lang_bat_dest)
        print(f"✓ 已複製語言包安裝工具")
    else:
        print(f"⚠️ 警告：找不到語言包安裝工具.bat")
    
else:
    print(f"\n✗ 找不到打包資料夾: {exe_folder}")
    exit(1)

# 創建獨立語言包 ZIP 檔（用於上傳到 GitHub Release）
lang_packs_folder = os.path.join(script_dir, "language_packs_release")
if BUILD_LANGS:
    if os.path.exists(lang_packs_folder):
        shutil.rmtree(lang_packs_folder)
    os.makedirs(lang_packs_folder, exist_ok=True)

    print("\n創建語言包 ZIP（用於 GitHub Release）...")
    for lang_file, lang_info in available_langs.items():
        if lang_file == 'eng.traineddata':  # 英文已包含在基礎版
            continue
        
        lang_code = lang_file.replace('.traineddata', '')
        lang_name = lang_info['name']
        lang_zip_name = f"CL_Scan_Lang_{lang_code}.zip"
        lang_zip_path = os.path.join(lang_packs_folder, lang_zip_name)
        
        # 創建語言包 ZIP
        with zipfile.ZipFile(lang_zip_path, 'w', zipfile.ZIP_DEFLATED) as lang_zip:
            # 添加語言包檔案（保持 tesseract/tessdata 資料夾結構）
            lang_zip.write(lang_info['path'], f"tesseract/tessdata/{lang_file}")
            
            # 創建安裝說明
        
        print(f"  ✓ {lang_name}: {lang_zip_name} ({lang_info['size']:.1f} MB)")

    print(f"\n✓ 語言包已生成在: {lang_packs_folder}")
    print("  請將這些 ZIP 檔案上傳到 GitHub Release:")
    print(f"  {GITHUB_RELEASE_URL}")
else:
    print("\n⚠️ 跳過語言包打包（使用 --langs 參數來打包語言包）")

# 創建使用說明文件
readme_path = os.path.join(release_folder, "使用說明.txt")
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("""================================================
            CL_Scan - 使用說明
        快速文字辨識工具（模組化版本）
================================================

【功能說明】
快速截圖並進行 OCR 文字辨識，支援多國語言。
✓ 內建 Tesseract-OCR 引擎，無需額外安裝
✓ 基礎版內建英文辨識
✓ 可選安裝：繁體中文、日文、韓文語言包

【使用方法】
1. 進入 CL_Scan 資料夾
2. 雙擊 CL_Scan.exe 啟動程式
3. 點擊「📷 開始截圖辨識」按鈕
4. 拖曳滑鼠選取要辨識的區域
5. 等待辨識完成
6. 點擊下方文字框即可複製內容

【安裝額外語言包】
方式一（推薦）：使用自動安裝工具
1. 雙擊 Language.bat
2. 選擇要安裝的語言包
3. 工具會自動從網路下載並安裝
4. 安裝完成後自動啟動 CL_Scan

方式二：手動安裝
1. 前往 GitHub Release 下載語言包
   https://github.com/Lucienwooo/CL_Scan/releases
2. 解壓縮後將 .traineddata 檔案放入 tesseract/tessdata/ 資料夾
3. 重新啟動 CL_Scan

【系統需求】
✓ Windows 10/11 (64位元)
✓ 網路連線（安裝語言包時需要）
✓ 無需安裝任何額外軟體
✓ 基礎版：約 60 MB 硬碟空間（已優化，排除不必要模組）
✓ 每個語言包：約 2-3 MB

【快捷鍵】
• ESC: 取消截圖
• 滑鼠右鍵: 取消截圖
• 點擊文字框: 複製內容到剪貼簿

【內建語言】
英文（English）

【可安裝語言包】
• 繁體中文 (~25 MB)
• 日文 (~18 MB)
• 韓文 (~15 MB)

【資料夾結構】
CL_Scan\\
├── CL_Scan.exe           ← 主程式
├── Language.bat          ← 語言包自動安裝工具
├── tesseract\\           ← OCR 引擎
└── tessdata\\            ← 語言包資料夾
    └── eng.traineddata   ← 英文（已內建）

【常見問題】
Q: 基礎版可以辨識中文嗎？
A: 基礎版僅含英文。若需辨識中文，請執行 Language.bat 安裝繁中語言包。

Q: Language.bat 無法下載怎麼辦？
A: 請確認：
   1. 網路連線正常
   2. GitHub Release 已上傳語言包
   3. 手動前往下載：https://github.com/Lucienwooo/CL_Scan/releases

Q: Language.bat 無法下載怎麼辦？
A: 請確認：
   1. 網路連線正常
   2. GitHub Release 已上傳語言包
   3. 手動前往下載：https://github.com/Lucienwooo/CL_Scan/releases

Q: 辨識不準確怎麼辦？
A: 建議截取較清晰的圖片，避免模糊或過小的文字。
   文字至少 12pt 以上效果較好。

Q: 可以移動到其他電腦嗎？
A: 可以！整個 CL_Scan 資料夾（含已安裝的語言包）
   複製到其他 Windows 電腦就能直接使用。

【版本資訊】
版本: 1.0 (Modular Edition)
打包日期: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
內建語言: 英文
可選語言: """ + str(len(available_langs) - 1) + """ 種（線上安裝）

【技術資訊】
• OCR 引擎: Tesseract-OCR 5.x
• GUI 框架: CustomTkinter
• Python 版本: 3.x
• 架構: 模組化語言包設計

【檔案大小】
• 基礎版: ~60 MB（已優化）
• 繁中語言包: ~2.3 MB
• 日文語言包: ~2.4 MB
• 韓文語言包: ~1.6 MB

【優化說明】
✓ 已排除 numpy、pandas 等不必要模組
✓ 相比未優化版本縮小約 30%
✓ 程式功能完全不受影響

================================================
""")

print(f"✓ 使用說明已創建: {readme_path}")

# 創建 ZIP 壓縮檔（包含主程式 + 語言包）
zip_name = f"CL_Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
zip_path = os.path.join(script_dir, zip_name)

print("\n正在壓縮主程式...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 添加說明文件（放在根目錄）
    zipf.write(readme_path, "使用說明.txt")
    
    # 添加整個 CL_Scan 資料夾
    app_folder = os.path.join(release_folder, "CL_Scan")
    for root, dirs, files in os.walk(app_folder):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.join("CL_Scan", os.path.relpath(file_path, app_folder))
            zipf.write(file_path, arcname)
    
    # 添加語言包資料夾（僅在 --langs 模式）
    if BUILD_LANGS and os.path.exists(lang_packs_folder):
        for root, dirs, files in os.walk(lang_packs_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join("language_packs", os.path.relpath(file_path, lang_packs_folder))
                zipf.write(file_path, arcname)

print(f"\n✓ ZIP 壓縮檔已創建: {zip_path}")

# 清理建置資料夾（可選）
print("\n清理暫存檔...")
build_folder = os.path.join(script_dir, "build")
if os.path.exists(build_folder):
    shutil.rmtree(build_folder)
    print("✓ 已刪除 build 資料夾")

# 刪除 .spec 檔案
spec_file = os.path.join(script_dir, "CL_Scan.spec")
if os.path.exists(spec_file):
    os.remove(spec_file)
    print("✓ 已刪除 .spec 檔案")

print("\n" + "=" * 60)
print("🎉 CL_Scan 模組化版本打包完成！")
print("=" * 60)
print(f"\n📦 發布檔案位置:")
print(f"   - 主程式: {os.path.join(release_folder, 'CL_Scan')}")
print(f"   - 語言包（用於 GitHub Release）: {lang_packs_folder}")
print(f"   - 完整 ZIP: {zip_path}")
print(f"\n📊 檔案大小:")

# 計算資料夾大小
def get_folder_size(folder):
    total = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            total += os.path.getsize(os.path.join(root, file))
    return total

app_folder_size = get_folder_size(os.path.join(release_folder, "CL_Scan")) / 1024 / 1024
zip_size = os.path.getsize(zip_path) / 1024 / 1024

print(f"   - 基礎版（僅英文）: {app_folder_size:.2f} MB")
if BUILD_LANGS and os.path.exists(lang_packs_folder):
    lang_packs_size = get_folder_size(lang_packs_folder) / 1024 / 1024
    print(f"   - 語言包總計: {lang_packs_size:.2f} MB")
print(f"   - 完整 ZIP: {zip_size:.2f} MB")

if BUILD_LANGS:
    print(f"\n📦 已生成的語言包 ZIP:")
    for lang_file, lang_info in available_langs.items():
        if lang_file != 'eng.traineddata':
            lang_code = lang_file.replace('.traineddata', '')
            print(f"   ✓ {lang_info['name']}: CL_Scan_Lang_{lang_code}.zip ({lang_info['size']:.1f} MB)")

print("\n" + "=" * 60)
print("⚠️  重要：請將檔案上傳到 GitHub Release")
print("=" * 60)
print(f"\n1. 前往: https://github.com/Lucienwooo/CL_Scan/releases")
print(f"2. 創建新 Release: v1.0")
print(f"3. 上傳以下檔案:")
print(f"   - {zip_name} (主程式)")
if BUILD_LANGS:
    for lang_file, lang_info in available_langs.items():
        if lang_file != 'eng.traineddata':
            lang_code = lang_file.replace('.traineddata', '')
            print(f"   - CL_Scan_Lang_{lang_code}.zip ({lang_info['name']})")

    print(f"\n4. 語言包下載 URL 格式:")
    print(f"   {GITHUB_RELEASE_URL}/CL_Scan_Lang_[語言代碼].zip")
    print(f"\n   範例:")
    print(f"   {GITHUB_RELEASE_URL}/CL_Scan_Lang_chi_tra.zip")

print("\n" + "=" * 60)
print("✨ 使用者體驗")
print("=" * 60)
print("\n使用者只需：")
print("   1. 下載並解壓縮主程式 ZIP")
print("   2. 執行 CL_Scan.exe（可立即使用英文辨識）")
print("   3. 如需其他語言：雙擊 Language.bat")
print("      → 選擇語言")
print("      → 自動下載安裝")
print("      → 自動啟動程式")
print("\n✓ 零技術門檻，全自動化！")
print("=" * 60)
