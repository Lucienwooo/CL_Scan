"""
精簡 Tesseract 資料夾
移除不需要的語言包和訓練工具，只保留 OCR 辨識所需的檔案
"""
import os
import shutil

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def get_folder_size(folder_path):
    """計算資料夾大小（MB）"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def remove_files(base_path, files_to_remove, description):
    """移除指定的檔案"""
    removed_count = 0
    saved_size = 0
    
    for file_name in files_to_remove:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path) / (1024 * 1024)
            try:
                os.remove(file_path)
                removed_count += 1
                saved_size += size
                print(f"  ✓ 移除: {file_name} ({size:.2f} MB)")
            except Exception as e:
                print(f"  ✗ 無法移除: {file_name} - {e}")
    
    return removed_count, saved_size

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tesseract_dir = os.path.join(script_dir, "tesseract")
    
    print_section("Tesseract 資料夾精簡工具")
    
    if not os.path.exists(tesseract_dir):
        print(f"❌ 找不到 tesseract 資料夾: {tesseract_dir}")
        input("按 Enter 退出...")
        return
    
    # 計算原始大小
    original_size = get_folder_size(tesseract_dir)
    print(f"\n📊 原始大小: {original_size:.2f} MB")
    
    # 1. 移除不需要的語言包（只保留英文）
    print("\n[步驟 1/4] 移除多餘的語言包...")
    tessdata_dir = os.path.join(tesseract_dir, "tessdata")
    
    # 保留 eng.traineddata，移除其他語言包
    unnecessary_languages = [
        "chi_tra.traineddata",      # 繁體中文 (2.26 MB)
        "chi_tra_vert.traineddata", # 繁中直排 (1.74 MB)
        "jpn.traineddata",          # 日文 (2.36 MB)
        "jpn_vert.traineddata",     # 日文直排 (2.90 MB)
        "kor.traineddata",          # 韓文 (1.60 MB)
    ]
    
    count1, size1 = remove_files(tessdata_dir, unnecessary_languages, "語言包")
    print(f"✓ 移除 {count1} 個語言包，節省 {size1:.2f} MB")
    
    # 2. 移除訓練工具（只需要 tesseract.exe 來執行 OCR）
    print("\n[步驟 2/4] 移除訓練工具...")
    training_tools = [
        "text2image.exe",                # 訓練用 (0.35 MB)
        "lstmtraining.exe",              # 訓練用 (0.30 MB)
        "lstmeval.exe",                  # 訓練用 (0.29 MB)
        "set_unicharset_properties.exe", # 訓練用 (0.24 MB)
        "mftraining.exe",                # 訓練用 (0.21 MB)
        "shapeclustering.exe",           # 訓練用 (0.20 MB)
        "cntraining.exe",                # 訓練用 (0.20 MB)
        "classifier_tester.exe",         # 訓練用 (0.20 MB)
        "unicharset_extractor.exe",      # 訓練用 (0.14 MB)
        "combine_lang_model.exe",        # 訓練用 (0.13 MB)
        "wordlist2dawg.exe",             # 訓練用 (0.09 MB)
        "combine_tessdata.exe",          # 訓練用 (0.06 MB)
        "dawg2wordlist.exe",             # 訓練用 (0.06 MB)
        "ambiguous_words.exe",           # 訓練用 (0.06 MB)
        "merge_unicharsets.exe",         # 訓練用 (0.05 MB)
        "tesseract-uninstall.exe",       # 安裝程式 (0.15 MB)
        "winpath.exe",                   # 工具 (0.02 MB)
    ]
    
    count2, size2 = remove_files(tesseract_dir, training_tools, "訓練工具")
    print(f"✓ 移除 {count2} 個訓練工具，節省 {size2:.2f} MB")
    
    # 3. 移除 HTML 文檔
    print("\n[步驟 3/4] 移除文檔檔案...")
    html_files = [
        "tesseract.1.html",
        "text2image.1.html",
        "lstmtraining.1.html",
        "lstmeval.1.html",
        "set_unicharset_properties.1.html",
        "mftraining.1.html",
        "shapeclustering.1.html",
        "cntraining.1.html",
        "classifier_tester.1.html",
        "unicharset_extractor.1.html",
        "combine_lang_model.1.html",
        "wordlist2dawg.1.html",
        "combine_tessdata.1.html",
        "dawg2wordlist.1.html",
        "ambiguous_words.1.html",
        "merge_unicharsets.1.html",
        "unicharset.5.html",
        "unicharambigs.5.html",
    ]
    
    count3, size3 = remove_files(tesseract_dir, html_files, "文檔")
    print(f"✓ 移除 {count3} 個文檔檔案，節省 {size3:.2f} MB")
    
    # 4. 移除 tessdata 中不需要的資料夾和檔案
    print("\n[步驟 4/4] 移除額外的資料...")
    extra_items = []
    
    # 移除 JAR 檔案（用於 ScrollView GUI，OCR 不需要）
    jar_files = [
        "piccolo2d-core-3.0.1.jar",
        "piccolo2d-extras-3.0.1.jar",
        "ScrollView.jar",
    ]
    for jar in jar_files:
        jar_path = os.path.join(tessdata_dir, jar)
        if os.path.exists(jar_path):
            size = os.path.getsize(jar_path) / (1024 * 1024)
            try:
                os.remove(jar_path)
                extra_items.append((jar, size))
                print(f"  ✓ 移除: {jar} ({size:.2f} MB)")
            except Exception as e:
                print(f"  ✗ 無法移除: {jar} - {e}")
    
    # 移除不需要的資料夾
    folders_to_remove = ["configs", "tessconfigs", "script"]
    for folder in folders_to_remove:
        folder_path = os.path.join(tessdata_dir, folder)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"  ✓ 移除資料夾: {folder}/")
            except Exception as e:
                print(f"  ✗ 無法移除: {folder}/ - {e}")
    
    size4 = sum([item[1] for item in extra_items])
    print(f"✓ 移除額外資料，節省 {size4:.2f} MB")
    
    # 計算最終大小
    final_size = get_folder_size(tesseract_dir)
    total_saved = original_size - final_size
    percentage = (total_saved / original_size) * 100
    
    print_section("精簡完成")
    print(f"\n📊 原始大小: {original_size:.2f} MB")
    print(f"📊 精簡後:   {final_size:.2f} MB")
    print(f"💾 節省空間: {total_saved:.2f} MB ({percentage:.1f}%)")
    
    print(f"\n✅ 保留的關鍵檔案:")
    essential_files = [
        "tesseract.exe (OCR 引擎)",
        "所有 DLL 檔案 (相依函式庫)",
        "tessdata/eng.traineddata (英文語言包)",
        "tessdata/pdf.ttf (字型檔案)",
    ]
    for f in essential_files:
        print(f"  ✓ {f}")
    
    print(f"\n📋 移除統計:")
    print(f"  • 語言包: {count1} 個，{size1:.2f} MB")
    print(f"  • 訓練工具: {count2} 個，{size2:.2f} MB")
    print(f"  • 文檔檔案: {count3} 個，{size3:.2f} MB")
    print(f"  • 額外資料: {len(extra_items)} 個，{size4:.2f} MB")
    
    print("\n" + "=" * 70)
    print("精簡完成！OCR 功能不受影響，只保留英文辨識所需的檔案。")
    print("=" * 70)
    
    input("\n按 Enter 退出...")

if __name__ == "__main__":
    main()
