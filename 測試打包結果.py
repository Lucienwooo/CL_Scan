"""
測試打包後的 CL_Scan 程式
檢查所有關鍵檔案是否存在
"""
import os
import sys

def check_file(path, description):
    """檢查檔案是否存在"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    size_info = ""
    if exists and os.path.isfile(path):
        size_kb = os.path.getsize(path) / 1024
        size_info = f" ({size_kb:.1f} KB)"
    print(f"{status} {description}: {path}{size_info}")
    return exists

def main():
    print("=" * 70)
    print("CL_Scan 檔案完整性檢查")
    print("=" * 70)
    
    # 檢查 release 資料夾
    release_path = os.path.join(os.path.dirname(__file__), "release", "CL_Scan")
    
    if not os.path.exists(release_path):
        print(f"\n✗ 找不到發布資料夾: {release_path}")
        print("請先執行「一鍵打包.bat」建立發布版本")
        input("\n按 Enter 退出...")
        return
    
    print(f"\n檢查路徑: {release_path}\n")
    
    # 必要檔案清單
    files_to_check = [
        ("CL_Scan.exe", "主程式執行檔"),
        ("CL_Scan.ico", "程式圖示"),
        ("使用說明.txt", "使用說明文件"),
        ("tesseract/tesseract.exe", "Tesseract OCR 引擎"),
        ("tesseract/tessdata/eng.traineddata", "英文語言包"),
        ("_internal/", "程式庫資料夾"),
    ]
    
    all_ok = True
    for rel_path, desc in files_to_check:
        full_path = os.path.join(release_path, rel_path)
        if not check_file(full_path, desc):
            all_ok = False
    
    # 檢查 DLL 檔案
    print("\n檢查 Tesseract DLL 檔案...")
    tesseract_dir = os.path.join(release_path, "tesseract")
    dll_count = 0
    if os.path.exists(tesseract_dir):
        for file in os.listdir(tesseract_dir):
            if file.endswith('.dll'):
                dll_count += 1
        print(f"✓ 找到 {dll_count} 個 DLL 檔案")
        if dll_count < 50:
            print("⚠️ DLL 檔案數量可能不足")
    else:
        print("✗ tesseract 資料夾不存在")
        all_ok = False
    
    # 計算總大小
    print("\n計算資料夾大小...")
    total_size = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(release_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
            file_count += 1
    
    size_mb = total_size / (1024 * 1024)
    print(f"總檔案數: {file_count}")
    print(f"總大小: {size_mb:.1f} MB")
    
    # 結果
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ 所有關鍵檔案檢查通過！")
        print("\n可將以下資料夾複製到任何 Windows 電腦使用：")
        print(f"   {release_path}")
        print("\n使用方法：")
        print("   1. 複製整個 CL_Scan 資料夾")
        print("   2. 雙擊 CL_Scan.exe 啟動程式")
        print("   3. 點擊「截圖辨識」開始使用")
    else:
        print("❌ 部分檔案遺失或不完整")
        print("請重新執行打包程式")
    print("=" * 70)
    
    input("\n按 Enter 退出...")

if __name__ == "__main__":
    main()
