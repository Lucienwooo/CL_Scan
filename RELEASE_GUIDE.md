# CL_Scan 發布指南

## 📦 打包完成後的檔案

執行 `python build_exe.py` 後會生成：

### 1. 主程式
```
release/CL_Scan/
├── CL_Scan.exe          # 主程式
├── Language.bat         # 語言包自動安裝工具
├── tesseract/           # OCR 引擎
└── tessdata/
    └── eng.traineddata  # 英文語言包（已內建）
```

### 2. 語言包（用於上傳 GitHub Release）
```
language_packs_release/
├── CL_Scan_Lang_chi_tra.zip  # 繁體中文 (~25 MB)
├── CL_Scan_Lang_jpn.zip      # 日文 (~18 MB)
└── CL_Scan_Lang_kor.zip      # 韓文 (~15 MB)
```

### 3. 完整壓縮包
```
CL_Scan_YYYYMMDD_HHMMSS.zip  # 主程式壓縮包
```

---

## 🚀 發布到 GitHub Release

### 步驟 1：創建 Release

1. 前往 GitHub 倉庫：https://github.com/Lucienwooo/CL_Scan
2. 點擊右側的 **Releases**
3. 點擊 **Draft a new release**

### 步驟 2：填寫 Release 資訊

- **Tag version**: `v1.0`
- **Release title**: `CL_Scan v1.0 - 快速文字辨識工具`
- **Description**:

```markdown
## 🎉 CL_Scan v1.0 正式發布

快速截圖 OCR 文字辨識工具，支援多國語言。

### ✨ 功能特點
- ✅ 內建 Tesseract-OCR 引擎，無需額外安裝
- ✅ 基礎版僅 70 MB，輕量快速
- ✅ 模組化語言包設計，按需安裝
- ✅ 自動化語言包安裝工具（Language.bat）
- ✅ 支援繁體中文、日文、韓文、英文

### 📥 下載說明

#### 主程式（必需）
下載 `CL_Scan_YYYYMMDD_HHMMSS.zip`，內含：
- CL_Scan.exe（主程式）
- Language.bat（語言包安裝工具）
- 英文語言包（已內建）

#### 語言包（可選）
如需辨識其他語言，可使用以下兩種方式：

**方式一：自動安裝（推薦）**
1. 執行 `Language.bat`
2. 選擇要安裝的語言
3. 自動下載並安裝

**方式二：手動安裝**
下載對應的語言包 ZIP：
- `CL_Scan_Lang_chi_tra.zip` - 繁體中文
- `CL_Scan_Lang_jpn.zip` - 日文
- `CL_Scan_Lang_kor.zip` - 韓文

解壓後將 `.traineddata` 檔案放入 `CL_Scan/tessdata/` 資料夾

### 🖥️ 系統需求
- Windows 10/11 (64位元)
- 約 70 MB 硬碟空間（基礎版）
- 網路連線（使用 Language.bat 時需要）

### 📝 使用方法
1. 解壓縮 ZIP 檔案
2. 執行 `CL_Scan.exe`
3. 點擊「📷 開始截圖辨識」
4. 拖曳滑鼠選取要辨識的區域
5. 點擊文字框複製結果

### 🔧 安裝語言包
執行 `Language.bat` → 選擇語言 → 自動下載安裝 → 完成！

---

**完整使用說明請參閱壓縮包內的「使用說明.txt」**
```

### 步驟 3：上傳檔案

在 **Attach binaries** 區域，上傳以下檔案：

1. **主程式**（必需）
   - `CL_Scan_YYYYMMDD_HHMMSS.zip`

2. **語言包**（必需，讓 Language.bat 能下載）
   - `CL_Scan_Lang_chi_tra.zip`
   - `CL_Scan_Lang_jpn.zip`
   - `CL_Scan_Lang_kor.zip`

### 步驟 4：發布

點擊 **Publish release**

---

## ✅ 驗證 Release

### 檢查下載連結

確認以下 URL 可以正常下載：

```
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_YYYYMMDD_HHMMSS.zip
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_chi_tra.zip
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_jpn.zip
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_kor.zip
```

### 測試 Language.bat

1. 下載並解壓縮主程式
2. 執行 `Language.bat`
3. 選擇一個語言包
4. 確認能正常下載並安裝
5. 確認程式自動啟動
6. 測試該語言的辨識功能

---

## 🔄 更新 Release

如需更新語言包或主程式：

1. 重新執行 `python build_exe.py`
2. 前往 Release 頁面
3. 點擊 **Edit release**
4. 刪除舊檔案，上傳新檔案
5. **注意**：檔案名稱必須與 `Language.bat` 中的一致

---

## ⚠️ 重要注意事項

### Language.bat 下載 URL 格式

Language.bat 會從以下 URL 下載語言包：

```
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_chi_tra.zip
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_jpn.zip
https://github.com/Lucienwooo/CL_Scan/releases/download/v1.0/CL_Scan_Lang_kor.zip
```

**檔案名稱格式必須為**：`CL_Scan_Lang_[語言代碼].zip`

### 支援的語言代碼

- `chi_tra` - 繁體中文
- `jpn` - 日文
- `kor` - 韓文

### 語言包內部結構

每個語言包 ZIP 必須包含：

```
tessdata/
└── [語言代碼].traineddata

例如：
tessdata/
└── chi_tra.traineddata
```

Language.bat 會自動解壓並複製到正確位置。

---

## 🐛 故障排除

### Language.bat 下載失敗

**可能原因**：
1. GitHub Release 尚未上傳語言包
2. 檔案名稱不符合格式
3. Release 版本號不是 `v1.0`
4. 網路連線問題

**解決方法**：
1. 確認 Release 已發布且檔案已上傳
2. 檢查檔案名稱是否正確
3. 在瀏覽器中測試下載連結
4. 提供手動下載說明

### 修改下載 URL

如果需要修改 Release 版本號，編輯 `build_exe.py`：

```python
GITHUB_RELEASE_URL = "https://github.com/Lucienwooo/CL_Scan/releases/download/v1.1"
```

然後重新打包。

---

## 📊 檔案大小參考

| 檔案 | 大小 | 說明 |
|------|------|------|
| 主程式 ZIP | ~70 MB | 包含程式和英文語言包 |
| 繁中語言包 | ~25 MB | chi_tra.traineddata |
| 日文語言包 | ~18 MB | jpn.traineddata |
| 韓文語言包 | ~15 MB | kor.traineddata |
| **總計（全部）** | **~128 MB** | 主程式 + 所有語言包 |

---

## 🎯 使用者體驗流程

### 新使用者（英文辨識）
1. 下載主程式 ZIP
2. 解壓縮
3. 執行 CL_Scan.exe
4. ✅ 立即可用（英文辨識）

### 新使用者（中文辨識）
1. 下載主程式 ZIP
2. 解壓縮
3. 雙擊 Language.bat
4. 選擇「繁體中文」
5. 等待下載安裝（自動）
6. ✅ 自動啟動程式，可辨識中文

**總時間：約 3-5 分鐘（取決於網速）**

---

## 📝 Release Checklist

打包並發布 Release 前的檢查清單：

- [ ] 執行 `python build_exe.py` 成功
- [ ] 測試主程式能正常啟動
- [ ] 測試英文辨識功能
- [ ] 檢查 Language.bat 已生成
- [ ] 檢查 3 個語言包 ZIP 已生成
- [ ] 創建 GitHub Release v1.0
- [ ] 上傳主程式 ZIP
- [ ] 上傳 3 個語言包 ZIP
- [ ] 發布 Release
- [ ] 測試主程式下載連結
- [ ] 測試語言包下載連結
- [ ] 測試 Language.bat 自動下載功能
- [ ] 測試每個語言包的辨識功能
- [ ] 更新 README.md（如有）

---

**完成！現在使用者可以輕鬆下載和安裝 CL_Scan 及語言包了！** 🎉
