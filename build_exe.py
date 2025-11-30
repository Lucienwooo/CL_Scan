"""
CL_Scan 自動打包工具（優化版）
使用 PyInstaller 打包成獨立執行檔，內建 Tesseract OCR
"""
import PyInstaller.__main__
import os
import sys
import shutil
import glob

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RELEASE_DIR = os.path.join(BASE_PATH, 'release')
BUILD_DIR = os.path.join(BASE_PATH, 'build')
TESSERACT_SRC = os.path.join(BASE_PATH, 'tesseract')

def clean_old_files():
    """清理舊的打包檔案"""
    if os.path.exists(RELEASE_DIR):
        print("🗑️  清理舊的發布檔案...")
        shutil.rmtree(RELEASE_DIR, ignore_errors=True)

def verify_tesseract():
    """驗證 Tesseract 資料夾完整性"""
    print("\n🔍 檢查 Tesseract 資料夾...")
    
    if not os.path.exists(TESSERACT_SRC):
        print(f"❌ 找不到 tesseract 資料夾: {TESSERACT_SRC}")
        return False
    
    tesseract_exe = os.path.join(TESSERACT_SRC, 'tesseract.exe')
    tessdata_dir = os.path.join(TESSERACT_SRC, 'tessdata')
    eng_data = os.path.join(tessdata_dir, 'eng.traineddata')
    
    if not os.path.exists(tesseract_exe):
        print(f"❌ 找不到 tesseract.exe")
        return False
    
    if not os.path.exists(tessdata_dir):
        print(f"❌ 找不到 tessdata 資料夾")
        return False
    
    if not os.path.exists(eng_data):
        print(f"❌ 找不到 eng.traineddata")
        return False
    
    print(f"✓ Tesseract 資料夾完整")
    print(f"✓ tesseract.exe: {os.path.getsize(tesseract_exe) // 1024} KB")
    print(f"✓ eng.traineddata: {os.path.getsize(eng_data) // 1024} KB")
    
    return True

def optimize_tesseract():
    """優化 Tesseract 資料夾（移除不必要的檔案）"""
    print("\n⚡ 優化 Tesseract 檔案...")
    
    tessdata_dir = os.path.join(TESSERACT_SRC, 'tessdata')
    
    # 只保留必要的語言檔案（eng）和配置檔
    keep_files = {
        'eng.traineddata',
        'osd.traineddata',  # 方向和腳本偵測（可選但建議保留）
        'pdf.ttf'  # PDF 輸出用（可選）
    }
    
    removed_count = 0
    saved_size = 0
    
    if os.path.exists(tessdata_dir):
        for file in os.listdir(tessdata_dir):
            file_path = os.path.join(tessdata_dir, file)
            if os.path.isfile(file_path):
                # 移除其他語言的 traineddata 檔案
                if file.endswith('.traineddata') and file not in keep_files:
                    file_size = os.path.getsize(file_path)
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        saved_size += file_size
                        print(f"  ✓ 已移除: {file} ({file_size // 1024} KB)")
                    except Exception as e:
                        print(f"  ✗ 無法移除 {file}: {e}")
    
    if removed_count > 0:
        print(f"\n💾 已優化，移除 {removed_count} 個檔案，節省 {saved_size // 1024} KB")
    else:
        print(f"  ℹ️  已是最精簡配置")
    
    return True

def clean_build_artifacts():
    """清理打包過程產生的暫存檔案"""
    print("\n🧹 清理打包暫存檔案...")
    
    # 刪除 .spec 檔案
    spec_files = glob.glob(os.path.join(BASE_PATH, '*.spec'))
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"  ✓ 已刪除: {os.path.basename(spec_file)}")
        except Exception as e:
            print(f"  ✗ 無法刪除 {os.path.basename(spec_file)}: {e}")
    
    # 刪除 build 資料夾
    if os.path.exists(BUILD_DIR):
        try:
            shutil.rmtree(BUILD_DIR)
            print(f"  ✓ 已刪除: build 資料夾")
        except Exception as e:
            print(f"  ✗ 無法刪除 build 資料夾: {e}")

def copy_tesseract_manually():
    """手動複製 Tesseract 到打包目錄（確保完整性）"""
    print("\n📦 手動複製 Tesseract 資料夾...")
    
    release_app_dir = os.path.join(RELEASE_DIR, 'CL_Scan')
    tesseract_dest = os.path.join(release_app_dir, 'tesseract')
    
    if not os.path.exists(release_app_dir):
        print(f"  ✗ 找不到打包輸出目錄: {release_app_dir}")
        return False
    
    # 複製整個 tesseract 資料夾
    try:
        if os.path.exists(tesseract_dest):
            shutil.rmtree(tesseract_dest)
        
        shutil.copytree(TESSERACT_SRC, tesseract_dest)
        
        # 驗證複製結果
        copied_exe = os.path.join(tesseract_dest, 'tesseract.exe')
        copied_data = os.path.join(tesseract_dest, 'tessdata', 'eng.traineddata')
        
        if os.path.exists(copied_exe) and os.path.exists(copied_data):
            print(f"  ✓ Tesseract 已成功複製到: {tesseract_dest}")
            return True
        else:
            print(f"  ✗ 複製後驗證失敗")
            return False
    except Exception as e:
        print(f"  ✗ 複製失敗: {e}")
        return False

def get_folder_size(folder_path):
    """計算資料夾大小"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def build_exe():
    """執行打包"""
    print("=" * 50)
    print("           CL_Scan 自動打包工具（優化版）")
    print("=" * 50)
    print("\n🚀 打包特點：")
    print("   ✓ 內建 Tesseract-OCR 引擎")
    print("   ✓ 排除不必要模組（numpy/pandas 等）")
    print("   ✓ 僅含英文語言包（最小化體積）")
    print("   ✓ 支援快捷鍵自訂功能")
    print("   ✓ 優化後體積約 40-50 MB\n")
    
    print("=" * 50)
    print("正在打包 CL_Scan...")
    print("=" * 50)
    print(f"\n📂 專案路徑: {BASE_PATH}")
    
    # 驗證 Tesseract
    if not verify_tesseract():
        print("\n❌ Tesseract 驗證失敗，無法繼續打包")
        return 1
    
    # 優化 Tesseract（移除不必要的語言包）
    optimize_tesseract()
    
    # 清理舊檔案
    clean_old_files()
    
    # PyInstaller 設定
    args = [
        'ocr_tool.py',
        '--name=CL_Scan',
        '--onedir',  # 資料夾模式
        '--windowed',  # 無命令列視窗
        '--clean',
        '--noconfirm',  # 不詢問直接覆蓋
        f'--distpath={RELEASE_DIR}',
    ]
    
    # 如果有圖示檔案就加上
    icon_path = os.path.join(BASE_PATH, 'CL_Scan.ico')
    if os.path.exists(icon_path):
        args.append(f'--icon={icon_path}')
    
    # 排除不需要的大型模組以減少體積
    exclude_modules = [
        'numpy', 'pandas', 'matplotlib', 'scipy', 
        'tensorflow', 'torch', 'IPython', 'notebook',
        'sphinx', 'pytest', 'setuptools._vendor',
        'unittest', 'test', 'tests',
        'pkg_resources.extern.jaraco',  # setuptools 的大型依賴
    ]
    for module in exclude_modules:
        args.append(f'--exclude-module={module}')
    
    print("\n⚙️  執行 PyInstaller...")
    try:
        PyInstaller.__main__.run(args)
        
        # 手動複製 Tesseract（確保完整）
        if not copy_tesseract_manually():
            print("\n❌ Tesseract 複製失敗")
            return 1
        
        # 計算最終大小
        release_app_dir = os.path.join(RELEASE_DIR, 'CL_Scan')
        if os.path.exists(release_app_dir):
            total_size = get_folder_size(release_app_dir)
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 最終大小: {size_mb:.1f} MB")
        
        # 打包完成後自動清理
        clean_build_artifacts()
        
        print("\n" + "=" * 50)
        print("🎉 打包完成！")
        print("=" * 50)
        print(f"\n📦 程式位置：{os.path.join(RELEASE_DIR, 'CL_Scan', 'CL_Scan.exe')}")
        print(f"📁 完整資料夾：{os.path.join(RELEASE_DIR, 'CL_Scan')}")
        print("\n💡 提示：整個 CL_Scan 資料夾可直接複製到任何 Windows 電腦使用")
        
        # 自動開啟發布資料夾
        print("\n正在開啟發布資料夾...")
        release_path = os.path.join(RELEASE_DIR, 'CL_Scan')
        if os.path.exists(release_path):
            os.startfile(release_path)
        
        return 0
    except Exception as e:
        print(f"\n❌ 打包失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = build_exe()
    
    print("\n按任意鍵退出...")
    input()
    
    sys.exit(exit_code)
