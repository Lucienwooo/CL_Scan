"""
CL_Scan 打包腳本（模組化版本）
- 基礎版：onedir + Tesseract + 英文語言包
- 額外語言包：獨立 ZIP 檔，使用者可選擇性下載安裝
"""
import PyInstaller.__main__
import os
import shutil
import zipfile
from datetime import datetime

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
print("開始打包 CL_Scan（基礎版 + 模組化語言包）")
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
    '--icon=NONE',               # 如果有 icon 可以指定
    '--clean',                   # 清理暫存檔
    '--noconfirm',               # 不詢問覆蓋
    # 打包 Tesseract 執行檔
    f'--add-binary={tesseract_exe};tesseract',
    # 添加所需的隱藏導入
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=pytesseract',
    '--hidden-import=pyperclip',
    '--hidden-import=customtkinter',
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
    
    # 檢查 Tesseract 是否成功打包
    tesseract_check = os.path.join(release_app_folder, "tesseract", "tesseract.exe")
    
    if os.path.exists(tesseract_check):
        print("✓ Tesseract 引擎已打包")
    else:
        print("⚠️ 警告：找不到 Tesseract 執行檔")
    
    # 創建 tessdata 資料夾並複製英文語言包
    tessdata_dest = os.path.join(release_app_folder, "tessdata")
    os.makedirs(tessdata_dest, exist_ok=True)
    
    # 複製英文語言包（基礎必備）
    eng_src = available_langs['eng.traineddata']['path']
    eng_dest = os.path.join(tessdata_dest, 'eng.traineddata')
    shutil.copy(eng_src, eng_dest)
    print(f"✓ 已安裝英文語言包（基礎版）")
    
else:
    print(f"\n✗ 找不到打包資料夾: {exe_folder}")
    exit(1)

# 創建獨立語言包 ZIP 檔
lang_packs_folder = os.path.join(release_folder, "language_packs")
os.makedirs(lang_packs_folder, exist_ok=True)

print("\n創建獨立語言包...")
for lang_file, lang_info in available_langs.items():
    if lang_file == 'eng.traineddata':  # 英文已包含在基礎版
        continue
    
    lang_code = lang_file.replace('.traineddata', '')
    lang_name = lang_info['name']
    lang_zip_name = f"CL_Scan_Lang_{lang_code}.zip"
    lang_zip_path = os.path.join(lang_packs_folder, lang_zip_name)
    
    # 創建語言包 ZIP
    with zipfile.ZipFile(lang_zip_path, 'w', zipfile.ZIP_DEFLATED) as lang_zip:
        # 添加語言包檔案
        lang_zip.write(lang_info['path'], f"tessdata/{lang_file}")
        
        # 創建安裝說明
        install_txt = f"""═══════════════════════════════════════
  CL_Scan - {lang_name}語言包安裝說明
═══════════════════════════════════════

【安裝步驟】
1. 解壓縮此 ZIP 檔案
2. 將 tessdata 資料夾內的 {lang_file} 複製到：
   CL_Scan\\tessdata\\ 資料夾內
   
3. 重新啟動 CL_Scan

【完整路徑範例】
CL_Scan\\
├── CL_Scan.exe
├── tesseract\\
└── tessdata\\
    ├── eng.traineddata      ← 已內建
    └── {lang_file}  ← 放這裡

【驗證安裝】
啟動 CL_Scan 後，程式會自動偵測可用語言。

【檔案大小】
{lang_info['size']:.1f} MB

【支援語言】
{lang_name}

═══════════════════════════════════════
"""
        lang_zip.writestr("安裝說明.txt", install_txt.encode('utf-8'))
    
    print(f"  ✓ {lang_name}: {lang_zip_name} ({lang_info['size']:.1f} MB)")

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

【系統需求】
✓ Windows 10/11 (64位元)
✓ 無需安裝任何額外軟體
✓ 基礎版：約 70 MB 硬碟空間
✓ 每個語言包：約 15-25 MB

【快捷鍵】
• ESC: 取消截圖
• 滑鼠右鍵: 取消截圖
• 點擊文字框: 複製內容到剪貼簿

【內建語言】
英文（English）

【可選語言包】
請前往 language_packs 資料夾下載：

【安裝額外語言包】
1. 前往 language_packs 資料夾
2. 選擇需要的語言包 ZIP 檔案
3. 解壓縮後將 .traineddata 檔案複製到：
   CL_Scan\\tessdata\\ 資料夾內
4. 重新啟動 CL_Scan 即可

【資料夾結構】
CL_Scan\\
├── CL_Scan.exe           ← 主程式
├── tesseract\\            ← OCR 引擎
└── tessdata\\             ← 語言包資料夾
    ├── eng.traineddata   ← 英文（已內建）
    ├── chi_tra.traineddata  ← 繁中（需自行安裝）
    ├── jpn.traineddata      ← 日文（需自行安裝）
    └── kor.traineddata      ← 韓文（需自行安裝）

【常見問題】
Q: 基礎版可以辨識中文嗎？
A: 基礎版僅含英文。若需辨識中文，請安裝繁體中文語言包。

Q: 如何安裝語言包？
A: 1. 解壓縮語言包 ZIP
   2. 將 .traineddata 檔案放到 CL_Scan\\tessdata\\
   3. 重啟程式即可

Q: 辨識不準確怎麼辦？
A: 建議截取較清晰的圖片，避免模糊或過小的文字。
   文字至少 12pt 以上效果較好。

Q: 可以移動到其他電腦嗎？
A: 可以！整個 CL_Scan 資料夾（含已安裝的語言包）
   複製到其他 Windows 電腦就能直接使用。

Q: 為什麼要分開語言包？
A: • 基礎版更小（70 MB vs 150 MB）
   • 使用者按需下載，節省空間和時間
   • 方便日後新增更多語言

【版本資訊】
版本: 1.0 (Modular Edition)
打包日期: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
內建語言: 英文
可選語言: """ + str(len(available_langs) - 1) + """ 種（獨立下載）

【技術資訊】
• OCR 引擎: Tesseract-OCR 5.x
• GUI 框架: CustomTkinter
• Python 版本: 3.x
• 架構: 模組化語言包設計

【檔案大小】
• 基礎版: ~70 MB
• 繁中語言包: ~25 MB
• 日文語言包: ~18 MB
• 韓文語言包: ~15 MB

================================================
""")

print(f"✓ 使用說明已創建: {readme_path}")

# 創建 ZIP 壓縮檔（包含主程式 + 語言包）
zip_name = f"CL_Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
zip_path = os.path.join(script_dir, zip_name)

print("\n正在壓縮主程式和語言包...")
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
    
    # 添加語言包資料夾
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
print(f"   - 主程式資料夾: {os.path.join(release_folder, 'CL_Scan')}")
print(f"   - 語言包資料夾: {lang_packs_folder}")
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
lang_packs_size = get_folder_size(lang_packs_folder) / 1024 / 1024
lang_packs_size = get_folder_size(lang_packs_folder) / 1024 / 1024
zip_size = os.path.getsize(zip_path) / 1024 / 1024

print(f"   - 基礎版（僅英文）: {app_folder_size:.2f} MB")
print(f"   - 語言包總計: {lang_packs_size:.2f} MB")
print(f"   - 完整 ZIP: {zip_size:.2f} MB")
print(f"\n📦 已生成的語言包:")
for lang_file, lang_info in available_langs.items():
    if lang_file != 'eng.traineddata':
        lang_code = lang_file.replace('.traineddata', '')
        print(f"   ✓ {lang_info['name']}: CL_Scan_Lang_{lang_code}.zip ({lang_info['size']:.1f} MB)")
print("\n⚨ 特點:")
print("   ✓ 無需安裝 Tesseract-OCR")
print("   ✓ 基礎版小巧（~70 MB）")
print("   ✓ 語言包按需下載安裝")
print("   ✓ 拖放安裝語言包，無需重新打包")
print("   ✓ 可攜帶到其他電腦使用")
print("\n💡 使用方式:")
print("   1. 解壓縮 ZIP 檔案")
print("   2. 進入 CL_Scan 資料夾執行 CL_Scan.exe（英文辨識）")
print("   3. 如需其他語言：")
print("      - 解壓縮 language_packs 中的語言包")
print("      - 將 .traineddata 檔案放入 CL_Scan\\tessdata\\")
print("      - 重啟程式即可")
print("=" * 60)
