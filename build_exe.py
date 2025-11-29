"""
CL_Scan 打包腳本
使用 PyInstaller 打包成獨立執行檔
"""
import PyInstaller.__main__
import os
import sys
import shutil

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RELEASE_DIR = os.path.join(BASE_PATH, 'release')

print("🔨 開始打包 CL_Scan...")
print(f"📂 專案路徑: {BASE_PATH}")

# 清理舊的打包檔案
if os.path.exists(RELEASE_DIR):
    print("🗑️  清理舊檔案...")
    shutil.rmtree(RELEASE_DIR, ignore_errors=True)

# PyInstaller 設定
args = [
    'ocr_tool.py',
    '--name=CL_Scan',
    '--onedir',  # 資料夾模式
    '--windowed',  # 無命令列視窗
    '--clean',
    f'--distpath={RELEASE_DIR}',
    '--add-data=tesseract;tesseract',  # 包含 tesseract 資料夾
]

# 如果有圖示檔案就加上
icon_path = os.path.join(BASE_PATH, 'CL_Scan.ico')
if os.path.exists(icon_path):
    args.append(f'--icon={icon_path}')

# 排除不需要的模組以減少體積
exclude_modules = [
    'numpy', 'pandas', 'matplotlib', 'scipy', 
    'tensorflow', 'torch', 'IPython', 'notebook'
]
for module in exclude_modules:
    args.append(f'--exclude-module={module}')

print("⚙️  執行 PyInstaller...")
try:
    PyInstaller.__main__.run(args)
    print("\n✅ 打包完成！")
    print(f"📦 輸出位置: {os.path.join(RELEASE_DIR, 'CL_Scan', 'CL_Scan.exe')}")
except Exception as e:
    print(f"\n❌ 打包失敗: {e}")
    sys.exit(1)
