import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk, ImageGrab, ImageEnhance
import pytesseract
import pyperclip
import os
import sys
import ctypes
import string
import time
import json

# ================= 路徑設定（支援打包後執行）=================
if getattr(sys, 'frozen', False):
    # 打包後：exe 所在的資料夾
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # 開發中：py 檔案所在的資料夾
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

print(f"程式路徑: {BASE_PATH}")

# Tesseract 設定
TESSERACT_DIR = os.path.join(BASE_PATH, 'tesseract')
TESSERACT_CMD = os.path.join(TESSERACT_DIR, 'tesseract.exe')
TESSDATA_DIR = os.path.join(TESSERACT_DIR, 'tessdata')

has_tesseract = False
tesseract_error_msg = ""

if os.path.exists(TESSERACT_CMD) and os.path.exists(TESSDATA_DIR):
    try:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
        
        # 測試 Tesseract 是否能正常工作
        version = pytesseract.get_tesseract_version()
        has_tesseract = True
        print(f"✓ Tesseract 已載入 (版本: {version})")
        print(f"✓ 執行檔: {TESSERACT_CMD}")
        print(f"✓ 語言包: {TESSDATA_DIR}")
    except Exception as e:
        tesseract_error_msg = f"初始化失敗: {str(e)}"
        print(f"✗ Tesseract {tesseract_error_msg}")
else:
    # 記錄找不到的原因
    if not os.path.exists(TESSERACT_DIR):
        tesseract_error_msg = f"找不到 tesseract 資料夾\n路徑: {TESSERACT_DIR}"
    elif not os.path.exists(TESSERACT_CMD):
        tesseract_error_msg = f"找不到 tesseract.exe\n路徑: {TESSERACT_CMD}"
    elif not os.path.exists(TESSDATA_DIR):
        tesseract_error_msg = f"找不到 tessdata 資料夾\n路徑: {TESSDATA_DIR}"
    else:
        tesseract_error_msg = "未知錯誤"
    
    print(f"✗ {tesseract_error_msg}")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ================= DPI 設定 (關鍵修復) =================
try:
    # 設定為 Per-Monitor DPI Aware V2，這對於解決座標偏移至關重要
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ================= 輔助函數 =================
def clean_text(text):
    allowed_chars = set(string.printable)
    filtered_lines = []
    for line in text.splitlines():
        clean_line = ''.join(char for char in line if char in allowed_chars)
        if clean_line.strip():
            filtered_lines.append(clean_line)
    return '\n'.join(filtered_lines)

# ================= 截圖工具類別 (修復版) =================
class SnippingTool(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        # 1. 隱藏主視窗並等待一下，確保不會截到主視窗
        parent.withdraw()
        time.sleep(0.2)
        
        # 2. 取得全螢幕截圖 (包含多螢幕)
        # 這裡不進行任何 resize，保持原始像素以確保 OCR 準確度
        self.original_image = ImageGrab.grab(all_screens=True)
        
        # 3. 製作「變暗」的背景圖 (微軟截圖風格)
        enhancer = ImageEnhance.Brightness(self.original_image)
        self.dark_image = enhancer.enhance(0.5) # 亮度降低 50%
        
        # 4. 取得虛擬螢幕的幾何資訊 (處理多螢幕座標)
        user32 = ctypes.windll.user32
        self.virtual_left = user32.GetSystemMetrics(76) # SM_XVIRTUALSCREEN
        self.virtual_top = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        self.virtual_width = user32.GetSystemMetrics(78) # SM_CXVIRTUALSCREEN
        self.virtual_height = user32.GetSystemMetrics(79)# SM_CYVIRTUALSCREEN
        
        # 5. 設定視窗屬性
        self.overrideredirect(True) # 無邊框
        self.attributes('-topmost', True) # 最上層
        
        # 設定視窗位置覆蓋整個虛擬螢幕
        geometry_str = f"{self.virtual_width}x{self.virtual_height}+{self.virtual_left}+{self.virtual_top}"
        self.geometry(geometry_str)
        
        # 6. 建立 Canvas
        self.canvas = tk.Canvas(
            self, 
            width=self.virtual_width, 
            height=self.virtual_height,
            cursor="cross", 
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # 轉換圖片為 Tkinter 格式
        self.tk_dark_image = ImageTk.PhotoImage(self.dark_image)
        self.tk_original_image = ImageTk.PhotoImage(self.original_image)
        
        # 繪製暗色背景
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_dark_image)

        # 初始化變數
        self.start_x = None
        self.start_y = None
        self.rect_id = None      # 紅色邊框
        self.highlight_id = None # 亮色區域圖片

        # 綁定滑鼠事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # ESC 或 右鍵 退出
        self.bind("<Escape>", self.exit_snipping)
        self.canvas.bind("<Button-3>", self.exit_snipping)
        
        # 顯示操作提示
        self.canvas.create_text(
            self.virtual_width // 2, 100,
            text="拖曳滑鼠選取區域 (ESC 取消)",
            fill="white", font=("Arial", 16, "bold"), tags="instruction"
        )

    def on_button_press(self, event):
        # 記錄起始座標
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        # 清除提示文字
        self.canvas.delete("instruction")
        
        # 建立選取框 (紅色邊框)
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline='#FF3333', width=2
        )

    def on_move_press(self, event):
        if not self.rect_id:
            return
            
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        # 更新紅色邊框
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)
        
        # === 實現微軟截圖的「打亮」效果 ===
        # 刪除舊的亮色區域
        if self.highlight_id:
            self.canvas.delete(self.highlight_id)
            
        # 計算正規化的座標 (左上, 右下)
        x1, y1 = min(self.start_x, cur_x), min(self.start_y, cur_y)
        x2, y2 = max(self.start_x, cur_x), max(self.start_y, cur_y)
        
        # 只有當區域夠大時才繪製，避免效能問題
        if (x2 - x1) > 1 and (y2 - y1) > 1:
            try:
                # 從原始「亮」圖中裁切選取區域
                # 注意：這裡的 crop 是基於圖片座標，因為圖片與 canvas 是 1:1 對應的
                crop = self.original_image.crop((int(x1), int(y1), int(x2), int(y2)))
                self.tk_crop = ImageTk.PhotoImage(crop)
                
                # 將裁切下來的亮圖疊加在暗圖之上
                self.highlight_id = self.canvas.create_image(
                    x1, y1, anchor="nw", image=self.tk_crop
                )
                # 確保紅框在最上面
                self.canvas.tag_raise(self.rect_id)
            except Exception:
                pass

    def on_button_release(self, event):
        if not self.start_x:
            self.exit_snipping()
            return

        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        
        x1 = min(self.start_x, cur_x)
        y1 = min(self.start_y, cur_y)
        x2 = max(self.start_x, cur_x)
        y2 = max(self.start_y, cur_y)

        # 關閉截圖視窗
        self.withdraw()
        
        # 執行裁切與回調
        if (x2 - x1) > 5 and (y2 - y1) > 5:
            try:
                # 裁切圖片
                selected_area = self.original_image.crop((int(x1), int(y1), int(x2), int(y2)))
                self.destroy()
                self.callback(selected_area)
            except Exception as e:
                print(f"裁切錯誤: {e}")
                self.exit_snipping()
        else:
            self.exit_snipping()

    def exit_snipping(self, event=None):
        self.destroy()
        # 恢復主視窗
        self.master.deiconify()

# ================= 主程式 =================
class OCRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CL_Scan (OCR Tool)")
        self.geometry("500x700")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # 調試模式開關
        self.debug_mode = False
        self.last_processed_image = None
        
        # 載入快捷鍵設定
        self.config_file = os.path.join(BASE_PATH, 'hotkey_config.json')
        self.hotkey = self.load_hotkey()
        
        # 綁定快捷鍵
        self.bind(f"<{self.hotkey}>", lambda e: self.start_snipping())

        # 按鈕區
        self.btn_capture = ctk.CTkButton(
            self, text=f"截圖辨識 (Screen Snipping) - {self.hotkey}", command=self.start_snipping,
            height=50, font=("Microsoft JhengHei UI", 16, "bold"),
            fg_color="#106EBE", hover_color="#005A9E"
        )
        self.btn_capture.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # 綁定右鍵更改快捷鍵
        self.btn_capture.bind("<Button-3>", self.change_hotkey)
        
        # 調試按鈕
        self.btn_debug = ctk.CTkButton(
            self, text="💾 保存預處理圖片", command=self.save_debug_image,
            height=30, font=("Microsoft JhengHei UI", 12),
            fg_color="#666666", hover_color="#555555"
        )
        self.btn_debug.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        # 圖片預覽區
        self.preview_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        self.preview_frame.grid(row=2, column=0, padx=20, pady=0, sticky="ew")
        
        self.lbl_image = ctk.CTkLabel(
            self.preview_frame, text="截圖預覽", width=300, height=150, corner_radius=8
        )
        self.lbl_image.pack(padx=10, pady=10)

        # 狀態標籤
        self.lbl_status = ctk.CTkLabel(self, text="準備就緒", text_color="#AAAAAA")
        self.lbl_status.grid(row=3, column=0, pady=(10, 5))

        # 結果文字框
        lbl_result_title = ctk.CTkLabel(self, text="辨識結果 (點擊複製):", anchor="w")
        lbl_result_title.grid(row=4, column=0, padx=20, pady=(10,0), sticky="nw")

        self.textbox = ctk.CTkTextbox(
            self, font=("Consolas", 14), fg_color="#1D1D1D", text_color="#FFFFFF"
        )
        self.textbox.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.textbox.bind("<Button-1>", self.copy_to_clipboard)
    
    def load_hotkey(self):
        """載入快捷鍵設定"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('hotkey', 'F3')
        except:
            pass
        return 'F3'  # 預設值
    
    def save_hotkey(self, hotkey):
        """儲存快捷鍵設定"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'hotkey': hotkey}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"儲存設定失敗: {e}")
    
    def change_hotkey(self, event):
        """右鍵更改快捷鍵"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("更改快捷鍵")
        dialog.geometry("400x220")
        dialog.transient(self)
        dialog.grab_set()
        
        # 置中顯示
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (200)
        y = self.winfo_y() + (self.winfo_height() // 2) - (110)
        dialog.geometry(f"400x220+{x}+{y}")
        
        # 標題
        title_label = ctk.CTkLabel(
            dialog, 
            text="⌨️ 自訂快捷鍵", 
            font=("Microsoft JhengHei UI", 18, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # 當前快捷鍵顯示
        current_label = ctk.CTkLabel(
            dialog, 
            text=f"目前快捷鍵: {self.hotkey}", 
            font=("Microsoft JhengHei UI", 12),
            text_color="#AAAAAA"
        )
        current_label.pack(pady=5)
        
        # 提示文字
        hint_label = ctk.CTkLabel(
            dialog, 
            text="輸入新快捷鍵 (例如: F3, F4, Control-s)", 
            font=("Microsoft JhengHei UI", 10),
            text_color="#888888"
        )
        hint_label.pack(pady=(5, 10))
        
        # 輸入框
        entry = ctk.CTkEntry(
            dialog, 
            font=("Microsoft JhengHei UI", 14),
            width=250,
            height=35,
            justify="center"
        )
        entry.insert(0, self.hotkey)
        entry.pack(pady=10)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def apply_hotkey():
            new_hotkey = entry.get().strip()
            if new_hotkey:
                # 解除舊快捷鍵
                try:
                    self.unbind(f"<{self.hotkey}>")
                except:
                    pass
                
                # 設定新快捷鍵
                self.hotkey = new_hotkey
                self.save_hotkey(new_hotkey)
                
                # 綁定新快捷鍵
                try:
                    self.bind(f"<{new_hotkey}>", lambda e: self.start_snipping())
                    self.btn_capture.configure(text=f"截圖辨識 (Screen Snipping) - {new_hotkey}")
                    self.lbl_status.configure(text=f"✅ 快捷鍵已更改為 {new_hotkey}", text_color="#2CC985")
                except Exception as e:
                    self.lbl_status.configure(text=f"❌ 快捷鍵設定失敗: {e}", text_color="red")
                
                dialog.destroy()
        
        # 按鈕區
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        btn_ok = ctk.CTkButton(
            btn_frame, 
            text="✓ 確定", 
            command=apply_hotkey,
            font=("Microsoft JhengHei UI", 12, "bold"),
            width=100,
            height=35,
            fg_color="#106EBE",
            hover_color="#005A9E"
        )
        btn_ok.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = ctk.CTkButton(
            btn_frame, 
            text="✕ 取消", 
            command=dialog.destroy,
            font=("Microsoft JhengHei UI", 12),
            width=100,
            height=35,
            fg_color="#666666",
            hover_color="#555555"
        )
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        # 按 Enter 確定
        entry.bind("<Return>", lambda e: apply_hotkey())
        # 按 Escape 取消
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def start_snipping(self):
        # SnippingTool 會自動隱藏主視窗，這裡不需要手動 iconify
        SnippingTool(self, self.process_image)

    def process_image(self, image):
        self.deiconify() # 顯示主視窗
        
        # 顯示預覽 (縮放以適應視窗)
        display_img = image.copy()
        # 限制預覽圖最大尺寸
        display_img.thumbnail((400, 200))
        ctk_img = ctk.CTkImage(light_image=display_img, dark_image=display_img, size=display_img.size)
        self.lbl_image.configure(image=ctk_img, text="")
        
        self.lbl_status.configure(text="處理中...", text_color="#FFD700")
        self.textbox.delete("0.0", "end")
        self.update_idletasks()

        final_text = ""
        try:
            if not has_tesseract:
                error_detail = f"""OCR 引擎載入失敗

{tesseract_error_msg}

請確認：
1. tesseract 資料夾在程式目錄中
2. tessdata 資料夾包含 eng.traineddata
3. 所有 DLL 檔案完整

程式路徑: {BASE_PATH}
"""
                self.textbox.insert("0.0", error_detail)
                self.lbl_status.configure(text="❌ 系統錯誤", text_color="red")
                return

            # === 圖像預處理：提高辨識率 ===
            from PIL import ImageEnhance, ImageFilter, ImageOps
            
            # 1. 轉為灰階
            processed_image = image.convert('L')
            
            # 2. 自動對比（處理不均勻光照）
            processed_image = ImageOps.autocontrast(processed_image)
            
            # 3. 智能放大
            if processed_image.width < 100 or processed_image.height < 50:
                scale = 4  # 小圖放大 4 倍
                processed_image = processed_image.resize(
                    (processed_image.width * scale, processed_image.height * scale), 
                    Image.Resampling.LANCZOS
                )
            else:
                # 一般圖片放大 2.5 倍
                scale = 2.5
                new_width = int(processed_image.width * scale)
                new_height = int(processed_image.height * scale)
                processed_image = processed_image.resize(
                    (new_width, new_height), 
                    Image.Resampling.LANCZOS
                )

            # 4. 增強對比度
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(2.5)
            
            # 5. 雙重銳化（提升邊緣清晰度）
            processed_image = processed_image.filter(ImageFilter.SHARPEN)
            processed_image = processed_image.filter(ImageFilter.SHARPEN)
            
            # 6. 二值化處理（讓文字更清晰）
            # 使用固定閾值進行二值化
            threshold = 150
            processed_image = processed_image.point(lambda p: 255 if p > threshold else 0)
            
            # 保存預處理後的圖片供調試使用
            self.last_processed_image = processed_image
            
            # OCR 設定 - 使用更適合表格和數字的配置
            config = r'--oem 3 --psm 6'
            
            # 執行 OCR，處理編碼問題
            try:
                raw_text = pytesseract.image_to_string(
                    processed_image, 
                    lang='eng', 
                    config=config
                )
            except UnicodeDecodeError:
                # 如果 UTF-8 解碼失敗，嘗試其他編碼
                try:
                    # 直接取得 bytes 並手動解碼
                    raw_bytes = pytesseract.image_to_string(
                        processed_image, 
                        lang='eng', 
                        config=config,
                        output_type=pytesseract.Output.BYTES
                    )
                    # 嘗試多種編碼
                    for encoding in ['utf-8', 'big5', 'gbk', 'latin-1']:
                        try:
                            raw_text = raw_bytes.decode(encoding)
                            break
                        except:
                            continue
                    else:
                        raw_text = raw_bytes.decode('utf-8', errors='ignore')
                except:
                    raw_text = ""
            
            final_text = clean_text(raw_text)

        except Exception as e:
            print(f"OCR Error: {e}")
            self.textbox.insert("0.0", f"OCR 執行錯誤：{str(e)}")
            self.lbl_status.configure(text="❌ 執行錯誤", text_color="red")
            return

        if final_text.strip():
            self.textbox.insert("0.0", final_text)
            self.lbl_status.configure(text="✅ 完成 (點擊複製)", text_color="#2CC985")
            # 自動複製到剪貼簿 (可選)
            pyperclip.copy(final_text)
        else:
            self.textbox.insert("0.0", "（未偵測到有效文字）")
            self.lbl_status.configure(text="⚠️ 無內容", text_color="#FFA500")

    def copy_to_clipboard(self, event):
        content = self.textbox.get("0.0", "end").strip()
        if content:
            pyperclip.copy(content)
            self.lbl_status.configure(text="📋 已複製！", text_color="#00BFFF")
            self.after(1500, lambda: self.lbl_status.configure(text="✅ 完成 (點擊複製)", text_color="#2CC985"))
    
    def save_debug_image(self):
        """保存預處理後的圖片用於調試"""
        if self.last_processed_image is None:
            self.lbl_status.configure(text="⚠️ 請先執行截圖辨識", text_color="#FFA500")
            return
        
        try:
            # 生成檔名（使用時間戳記）
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_processed_{timestamp}.png"
            filepath = os.path.join(BASE_PATH, filename)
            
            # 保存圖片
            self.last_processed_image.save(filepath)
            
            self.lbl_status.configure(text=f"💾 已保存: {filename}", text_color="#00FF00")
            print(f"調試圖片已保存: {filepath}")
            
            # 3秒後恢復原狀態
            self.after(3000, lambda: self.lbl_status.configure(text="✅ 完成 (點擊複製)", text_color="#2CC985"))
        except Exception as e:
            self.lbl_status.configure(text=f"❌ 保存失敗: {str(e)}", text_color="red")
            print(f"保存調試圖片失敗: {e}")

if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()