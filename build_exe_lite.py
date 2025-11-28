"""
CL_Scan 打包腳本（輕量版）
使用 onefile 模式打包成單一執行檔
需要使用者自行安裝 Tesseract-OCR
"""
import PyInstaller.__main__
import os
import sys
import shutil
import zipfile
from datetime import datetime

# 確保在正確的目錄
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 檢查圖示檔案
# icon_path = os.path.join(script_dir, 'cl_scan_icon.ico')
# if not os.path.exists(icon_path):
#     print("⚠️ 警告：找不到圖示檔案")
#     icon_path = 'NONE'
# else:
#     print(f"✓ 找到圖示檔案: {icon_path}")
icon_path = 'NONE'

print("=" * 60)
print("開始打包 CL_Scan (輕量版 - 單一執行檔)")
print("=" * 60)
print("\n⚠️ 此版本需要使用者自行安裝 Tesseract-OCR")
print("   如需完整版，請使用 build_exe.py\n")

# 打包參數
PyInstaller.__main__.run([
    'ocr_tool.py',              # 主程式
    '--onefile',                 # 打包成單一執行檔
    '--windowed',                # 不顯示命令列視窗
    '--name=CL_Scan',            # 執行檔名稱
    # f'--icon={icon_path}',       # 使用生成的圖示
    '--clean',                   # 清理暫存檔
    '--noconfirm',               # 不詢問覆蓋
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
release_folder = os.path.join(script_dir, "release_lite")

if os.path.exists(release_folder):
    shutil.rmtree(release_folder)
os.makedirs(release_folder)

# 複製執行檔
exe_path = os.path.join(dist_folder, "CL_Scan.exe")
if os.path.exists(exe_path):
    shutil.copy(exe_path, release_folder)
    print(f"\n✓ 執行檔已複製到: {release_folder}")
else:
    print(f"\n✗ 找不到執行檔: {exe_path}")
    exit(1)

# 創建說明文件
readme_path = os.path.join(release_folder, "使用說明.txt")
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("""================================================
            CL_Scan - 使用說明
          快速文字辨識工具（輕量版）
================================================

【功能說明】
快速截圖並進行 OCR 文字辨識，支援多國語言。
此為輕量版，需要自行安裝 Tesseract-OCR。

【系統需求】
1. Windows 10/11 (64位元)
2. 需要安裝 Tesseract-OCR
   
   📥 下載位置: 
   https://github.com/UB-Mannheim/tesseract/wiki
   
   ⚠️ 重要安裝步驟：
   a. 執行安裝程式
   b. 安裝時勾選「Additional language data」
   c. 至少選擇以下語言包：
      • Chinese - Traditional (chi_tra) - 繁體中文
      • English (eng) - 英文
      • Japanese (jpn) - 日文（選用）
      • Korean (kor) - 韓文（選用）
   
   d. 預設安裝路徑: C:\\Program Files\\Tesseract-OCR
      ⚠️ 如果改變路徑，程式可能無法找到 Tesseract

【使用方法】
1. 確認已安裝 Tesseract-OCR
2. 雙擊 CL_Scan.exe 啟動程式
3. 點擊「📷 開始截圖辨識」按鈕
4. 拖曳滑鼠選取要辨識的區域
5. 等待辨識完成
6. 點擊下方文字框即可複製內容

【快捷鍵】
• ESC: 取消截圖
• 滑鼠右鍵: 取消截圖
• 點擊文字框: 複製內容到剪貼簿

【常見問題】
Q: 啟動後顯示「找不到 Tesseract」？
A: 請確認已安裝 Tesseract-OCR 到預設路徑：
   C:\\Program Files\\Tesseract-OCR\\tesseract.exe

Q: 辨識失敗或顯示亂碼？
A: 請確認安裝 Tesseract 時有勾選對應的語言包

Q: 辨識不準確怎麼辦？
A: 建議截取較清晰的圖片，避免模糊或過小的文字。
   文字至少 12pt 以上效果較好。

Q: 為什麼選擇輕量版？
A: • 檔案小（約 20-30 MB）
   • 下載快速
   • 啟動快速
   缺點：需要另外安裝 Tesseract

Q: 如何切換到完整版？
A: 完整版內建 Tesseract，無需另外安裝，但檔案較大（約 150 MB）

【版本資訊】
版本: 1.0 (Lite Edition)
打包日期: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

【技術資訊】
• OCR 引擎: Tesseract-OCR 5.x (需自行安裝)
• GUI 框架: CustomTkinter
• Python 版本: 3.x

【完整版 vs 輕量版】
┌─────────────┬──────────────┬──────────────┐
│   項目      │   完整版     │   輕量版     │
├─────────────┼──────────────┼──────────────┤
│ 檔案大小    │  ~150 MB     │  ~25 MB      │
│ 需要安裝    │  否          │  是(Tesseract)│
│ 啟動速度    │  快          │  較快        │
│ 便攜性      │  高          │  低          │
│ 更新語言包  │  困難        │  簡單        │
└─────────────┴──────────────┴──────────────┘

================================================
""")

print(f"✓ 使用說明已創建: {readme_path}")

# 創建 Tesseract 安裝指引
install_guide_path = os.path.join(release_folder, "Tesseract安裝指引.txt")
with open(install_guide_path, 'w', encoding='utf-8') as f:
    f.write("""╔═══════════════════════════════════════════════╗
║     Tesseract-OCR 安裝指引                    ║
╚═══════════════════════════════════════════════╝

【步驟 1】下載安裝程式
前往: https://github.com/UB-Mannheim/tesseract/wiki
選擇: tesseract-ocr-w64-setup-5.x.x.exe (最新版本)

【步驟 2】執行安裝
1. 雙擊下載的安裝程式
2. 點選 "I accept the agreement" 同意授權
3. 安裝路徑建議使用預設：
   C:\\Program Files\\Tesseract-OCR

【步驟 3】選擇語言包（重要！）
1. 在「Select Components」畫面
2. 展開「Additional language data」
3. ✓ 勾選以下語言包：
   
   必選：
   ☑ Chinese - Traditional (chi_tra)
   ☑ English (eng)
   
   選用：
   ☐ Japanese (jpn)
   ☐ Korean (kor)
   ☐ Chinese - Simplified (chi_sim)

【步驟 4】完成安裝
點擊「Install」開始安裝
等待安裝完成

【驗證安裝】
1. 開啟檔案總管
2. 前往 C:\\Program Files\\Tesseract-OCR
3. 確認存在以下檔案：
   ✓ tesseract.exe
   ✓ tessdata 資料夾
   ✓ tessdata 內有 .traineddata 檔案

【測試 CL_Scan】
1. 雙擊 CL_Scan.exe
2. 如果正常啟動，表示安裝成功
3. 如果顯示「找不到 Tesseract」，請檢查安裝路徑

【疑難排解】
Q: 安裝後仍顯示「找不到 Tesseract」
A: 1. 確認安裝路徑是否為：
      C:\\Program Files\\Tesseract-OCR\\tesseract.exe
   2. 如果路徑不同，請重新安裝到預設路徑

Q: 可以辨識但中文變亂碼
A: 安裝時沒有勾選 chi_tra 語言包
   請重新執行安裝程式，記得勾選語言包

Q: 需要支援更多語言
A: 重新執行安裝程式，在語言包清單中勾選需要的語言

═══════════════════════════════════════════════
""")

print(f"✓ 安裝指引已創建: {install_guide_path}")

# 創建 ZIP 壓縮檔
zip_name = f"CL_Scan_Lite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
zip_path = os.path.join(script_dir, zip_name)

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 添加執行檔
    zipf.write(
        os.path.join(release_folder, "CL_Scan.exe"),
        "CL_Scan.exe"
    )
    # 添加說明文件
    zipf.write(
        readme_path,
        "使用說明.txt"
    )
    # 添加安裝指引
    zipf.write(
        install_guide_path,
        "Tesseract安裝指引.txt"
    )

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
print("🎉 CL_Scan 輕量版打包完成！")
print("=" * 60)
print(f"\n📦 發布檔案位置:")
print(f"   - 執行檔資料夾: {release_folder}")
print(f"   - ZIP 壓縮檔: {zip_path}")
print(f"\n📊 檔案大小:")
exe_size = os.path.getsize(os.path.join(release_folder, "CL_Scan.exe")) / 1024 / 1024
zip_size = os.path.getsize(zip_path) / 1024 / 1024
print(f"   - CL_Scan.exe: {exe_size:.2f} MB")
print(f"   - {zip_name}: {zip_size:.2f} MB")
print("\n⚠️ 使用者需求:")
print("   • 自行安裝 Tesseract-OCR")
print("   • 安裝時選擇繁體中文語言包")
print("   • 安裝到預設路徑")
print("\n💡 優點:")
print("   ✓ 檔案小，下載快")
print("   ✓ 啟動速度快")
print("   ✓ 可自行更新語言包")
print("\n📌 提醒:")
print("   如需完整版（內建 Tesseract），請使用 build_exe.py")
print("=" * 60)
