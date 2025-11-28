"""
CL_Scan 一鍵打包腳本 - 完整版
適用於完全全新的電腦，不需要安裝任何額外軟體
"""
import os
import sys
import shutil
import subprocess

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_file_exists(path, name):
    if os.path.exists(path):
        print(f"✓ {name}: {path}")
        return True
    else:
        print(f"✗ {name}: 找不到 {path}")
        return False

# 切換到腳本目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print_section("CL_Scan 一鍵打包工具 (適用於全新電腦)")

# 0. 詢問是否精簡 Tesseract（可選）
print("\n[步驟 0/6] Tesseract 資料夾精簡（可選）")
print("目前 tesseract 資料夾約 415 MB")
print("可以精簡到約 50-60 MB（移除多餘語言包和訓練工具）")
print("\n精簡內容：")
print("  • 移除: 中文、日文、韓文語言包")
print("  • 移除: 訓練工具（mftraining, lstmtraining 等）")
print("  • 移除: 文檔和說明檔案")
print("  • 保留: tesseract.exe + 所有 DLL + 英文語言包")
print("\n是否精簡 tesseract 資料夾? (y/n): ", end="")

user_input = input().strip().lower()
if user_input == 'y' or user_input == 'yes':
    print("\n正在精簡 tesseract 資料夾...")
    try:
        subprocess.run([sys.executable, "精簡_tesseract.py"], check=True, input=b'\n')
        print("✓ Tesseract 精簡完成")
    except Exception as e:
        print(f"⚠️ 精簡失敗: {e}")
        print("繼續使用原始 tesseract 資料夾")
else:
    print("✓ 跳過精簡，使用完整 tesseract 資料夾")

# 1. 檢查必要檔案
print("\n[步驟 1/6] 檢查必要檔案...")
all_ok = True
all_ok &= check_file_exists("ocr_tool.py", "主程式")
all_ok &= check_file_exists("CL_Scan.ico", "圖示檔案")
all_ok &= check_file_exists("tesseract/tesseract.exe", "Tesseract OCR")
all_ok &= check_file_exists("tesseract/tessdata/eng.traineddata", "英文語言包")

if not all_ok:
    print("\n❌ 缺少必要檔案，無法繼續打包")
    input("按 Enter 退出...")
    sys.exit(1)

# 2. 安裝/檢查 PyInstaller
print("\n[步驟 2/6] 檢查 PyInstaller...")
try:
    import PyInstaller
    print(f"✓ PyInstaller 已安裝 (版本: {PyInstaller.__version__})")
except ImportError:
    print("⚠️ PyInstaller 未安裝，正在安裝...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("✓ PyInstaller 安裝完成")

# 3. 執行 PyInstaller 打包
print("\n[步驟 3/6] 執行 PyInstaller 打包...")
icon_path = os.path.abspath('CL_Scan.ico')

# 清理舊的建置
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# 使用 subprocess 執行 PyInstaller
# 使用 subprocess 執行 PyInstaller
pyinstaller_args = [
    sys.executable, '-m', 'PyInstaller',
    'ocr_tool.py',
    '--onedir',                    # 打包成資料夾模式
    '--windowed',                  # 視窗模式（不顯示 console）
    '--name=CL_Scan',              # 程式名稱
    f'--icon={icon_path}',         # 程式圖示
    f'--add-data={icon_path};.',   # 將圖示打包進去
    '--clean',                     # 清理暫存
    '--noconfirm',                 # 不詢問覆蓋
    # 隱藏匯入（確保這些模組被打包）
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    '--hidden-import=PIL.ImageGrab',
    '--hidden-import=PIL.ImageEnhance',
    '--hidden-import=PIL.ImageFilter',
    '--hidden-import=pytesseract',
    '--hidden-import=pyperclip',
    '--hidden-import=customtkinter',
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    # 排除不需要的大型模組（減小檔案大小）
    '--exclude-module=numpy',
    '--exclude-module=pandas',
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    '--exclude-module=pytest',
    '--exclude-module=setuptools',
    '--noupx',                     # 不使用 UPX 壓縮（避免防毒誤判）
]

result = subprocess.run(pyinstaller_args, capture_output=True, text=True)
if result.returncode != 0:
    print("❌ PyInstaller 執行失敗:")
    print(result.stderr)
    input("按 Enter 退出...")
    sys.exit(1)

print("✓ PyInstaller 打包完成")

# 4. 複製 Tesseract 到發布資料夾
print("\n[步驟 4/6] 整合 Tesseract OCR...")
dist_exe_folder = os.path.join(script_dir, "dist", "CL_Scan")

if not os.path.exists(dist_exe_folder):
    print(f"❌ 找不到打包資料夾: {dist_exe_folder}")
    input("按 Enter 退出...")
    sys.exit(1)

# 複製整個 tesseract 資料夾到發布目錄
tesseract_src = os.path.join(script_dir, "tesseract")
tesseract_dest = os.path.join(dist_exe_folder, "tesseract")

if os.path.exists(tesseract_dest):
    shutil.rmtree(tesseract_dest)

print("正在複製 Tesseract 檔案...")
shutil.copytree(tesseract_src, tesseract_dest)

# 確認關鍵檔案
check_file_exists(os.path.join(tesseract_dest, "tesseract.exe"), "Tesseract 執行檔")
check_file_exists(os.path.join(tesseract_dest, "tessdata", "eng.traineddata"), "英文語言包")

# 確保圖示在正確位置
icon_dest = os.path.join(dist_exe_folder, "CL_Scan.ico")
if not os.path.exists(icon_dest):
    shutil.copy2(icon_path, icon_dest)
    print(f"✓ 圖示已複製")

print("✓ Tesseract 整合完成")

# 5. 建立最終發布版本
print("\n[步驟 5/6] 建立發布版本...")
release_folder = os.path.join(script_dir, "release")

if os.path.exists(release_folder):
    shutil.rmtree(release_folder)
os.makedirs(release_folder)

# 移動到 release 資料夾
final_folder = os.path.join(release_folder, "CL_Scan")
shutil.move(dist_exe_folder, final_folder)

# 建立使用說明
readme_path = os.path.join(final_folder, "使用說明.txt")
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("""═══════════════════════════════════════════════════════
  CL_Scan - 螢幕文字辨識工具
═══════════════════════════════════════════════════════

【功能說明】
• 截圖並自動辨識螢幕上的文字
• 支援英文、數字、符號辨識
• 一鍵複製辨識結果到剪貼簿

【使用方法】
1. 雙擊「CL_Scan.exe」啟動程式
2. 點擊「截圖辨識」按鈕
3. 用滑鼠拖曳選取要辨識的文字區域
4. 等待辨識完成（約 1-3 秒）
5. 點擊結果文字框即可複製到剪貼簿

【快捷鍵】
• ESC 鍵：取消截圖選取
• 滑鼠右鍵：取消截圖選取
• 滑鼠左鍵拖曳：選取辨識區域

【注意事項】
✓ 本程式為獨立版本，不需要安裝任何額外軟體
✓ 請確保截圖區域的文字清晰可見
✓ 文字越大、對比度越高，辨識率越好
✓ 建議在亮色背景上辨識深色文字

【系統需求】
• 作業系統：Windows 10/11
• 不需要網路連線
• 不需要安裝 Python 或其他軟體

【問題排除】
Q: 程式無法啟動？
A: 請確認 Windows 防毒軟體沒有阻擋程式執行

Q: 無法辨識任何文字？
A: 1. 確認 tesseract 資料夾在程式目錄中
   2. 確認 tessdata/eng.traineddata 檔案存在
   3. 嘗試截取更清晰的文字區域

Q: 辨識結果不準確？
A: 1. 確保文字夠大（建議至少 12pt 以上）
   2. 提高文字與背景的對比度
   3. 避免截取有複雜背景的區域

【資料夾結構】
CL_Scan/
├── CL_Scan.exe          (主程式，雙擊執行)
├── CL_Scan.ico          (程式圖示)
├── 使用說明.txt         (本檔案)
├── tesseract/           (OCR 辨識引擎)
│   ├── tesseract.exe
│   └── tessdata/
│       └── eng.traineddata
└── _internal/           (程式庫檔案)

【版權資訊】
本程式使用 Tesseract OCR 引擎
Tesseract 是由 Google 維護的開源 OCR 專案

═══════════════════════════════════════════════════════
""")

# 建立快速啟動批次檔（可選）
bat_path = os.path.join(final_folder, "啟動 CL_Scan.bat")
with open(bat_path, 'w', encoding='utf-8') as f:
    f.write('@echo off\n')
    f.write('start "" "CL_Scan.exe"\n')

print("✓ 使用說明已建立")

# 6. 最終統計
print("\n[步驟 6/6] 計算最終大小...")

# 顯示結果
print_section("打包完成！")
print(f"\n📁 發布位置: {final_folder}")
print("\n📂 資料夾結構:")
print("   CL_Scan/")
print("   ├── CL_Scan.exe         (主程式)")
print("   ├── CL_Scan.ico         (圖示)")
print("   ├── 使用說明.txt         (說明文件)")
print("   ├── 啟動 CL_Scan.bat    (快速啟動)")
print("   ├── tesseract/          (OCR 引擎，已整合)")
print("   └── _internal/          (程式庫)")

# 計算資料夾大小
total_size = 0
for dirpath, dirnames, filenames in os.walk(final_folder):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        total_size += os.path.getsize(filepath)

size_mb = total_size / (1024 * 1024)
print(f"\n📦 總大小: {size_mb:.1f} MB")

print("\n✅ 此版本可在完全全新的 Windows 電腦上直接執行")
print("   無需安裝 Python、Tesseract 或任何其他軟體")

# 測試檔案完整性
print("\n🔍 驗證關鍵檔案...")
critical_files = [
    ("CL_Scan.exe", "主程式"),
    ("tesseract/tesseract.exe", "OCR 引擎"),
    ("tesseract/tessdata/eng.traineddata", "英文語言包"),
    ("CL_Scan.ico", "圖示檔案"),
]

all_verified = True
for file_rel_path, file_desc in critical_files:
    file_path = os.path.join(final_folder, file_rel_path)
    if os.path.exists(file_path):
        size = os.path.getsize(file_path) / 1024
        print(f"   ✓ {file_desc}: {size:.1f} KB")
    else:
        print(f"   ✗ {file_desc}: 遺失！")
        all_verified = False

if all_verified:
    print("\n✅ 所有關鍵檔案驗證通過！")
else:
    print("\n⚠️ 部分檔案遺失，請檢查")

print("\n" + "=" * 70)
print("按 Enter 開啟發布資料夾...")
input()

# 開啟資料夾
os.startfile(final_folder)
