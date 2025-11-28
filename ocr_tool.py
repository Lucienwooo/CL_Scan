import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import pytesseract
import pyperclip
import os
import sys
import ctypes # 用來處理 Windows 高解析度縮放

# ================= 配置區 =================
# 自動偵測 Tesseract 路徑（支援打包後的執行檔）
if getattr(sys, 'frozen', False):
    # 如果是打包後的 exe
    base_path = os.path.dirname(sys.executable)
    TESSERACT_CMD = os.path.join(base_path, 'tesseract', 'tesseract.exe')
    TESSDATA_DIR = os.path.join(base_path, 'tessdata')
else:
    # 開發環境
    TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    TESSDATA_DIR = r'C:\Program Files\Tesseract-OCR\tessdata'

# 設定 Tesseract 路徑
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
    
    # 自動偵測可用語言包
    available_languages = ['eng']  # 預設英文
    if os.path.exists(TESSDATA_DIR):
        lang_map = {
            'chi_tra.traineddata': 'chi_tra',
            'jpn.traineddata': 'jpn',
            'kor.traineddata': 'kor'
        }
        for lang_file, lang_code in lang_map.items():
            if os.path.exists(os.path.join(TESSDATA_DIR, lang_file)):
                available_languages.append(lang_code)
    
    # 組合語言字串
    TESSERACT_LANG = '+'.join(available_languages)
    print(f"✓ Tesseract 已載入，支援語言: {', '.join(available_languages)}")
else:
    print("警告: 找不到 Tesseract，請確認路徑")
    TESSERACT_LANG = 'eng'

# 設定外觀
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ================= 系統環境設定 (關鍵修正) =================
# 強制開啟 Windows 高 DPI 感知，確保截圖座標精準，不會模糊或偏移
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass # 非 Windows 系統或版本過舊則跳過

# ================= 截圖工具類別 =================
class SnippingTool(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        
        # 1. 設定視窗為無邊框模式
        self.overrideredirect(True)
        
        # 2. 獲取全螢幕尺寸 (包含縮放後的真實解析度)
        # 注意: 多螢幕環境下，Tkinter 預設只能抓主螢幕。
        # 若需跨螢幕，通常需要更複雜的 mss 套件，這裡使用標準 Tkinter 抓取主螢幕全範圍。
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # 3. 設定視覺效果：置頂、半透明黑色背景
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.4) # 整體透明度，讓螢幕變暗
        self.configure(bg="black")
        
        # 4. 建立畫布
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # 變數初始化
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.info_text = None

        # 綁定事件
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        # 按 ESC 或右鍵取消
        self.bind("<Escape>", lambda e: self.destroy())
        self.canvas.bind("<Button-3>", lambda e: self.destroy())

        # 顯示操作提示
        self.canvas.create_text(
            screen_width // 2, screen_height // 2,
            text="按住滑鼠左鍵拖曳選取區域\n(ESC 取消)",
            fill="white",
            font=("Microsoft JhengHei UI", 20, "bold"),
            justify="center"
        )

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        
        # 清除提示文字
        self.canvas.delete("all")
        
        # 建立選取框 (紅色邊框，內部透明)
        # 這裡利用 stipple 模擬透明填充，或僅畫邊框
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, 1, 1, 
            outline='#00FF00', # 螢光綠，對比度高
            width=2
        )

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        
        # 更新矩形座標
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        
        # 動態顯示尺寸資訊
        if self.info_text:
            self.canvas.delete(self.info_text)
        self.info_text = self.canvas.create_text(
            cur_x, cur_y - 20,
            text=f"W:{abs(cur_x - self.start_x)} H:{abs(cur_y - self.start_y)}",
            fill="#00FF00",
            font=("Arial", 10, "bold")
        )

    def on_button_release(self, event):
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)

            # 隱藏遮罩視窗，準備截圖
            self.withdraw()
            
            # 給系統一點時間重繪背景 (0.2秒)
            self.after(200, lambda: self.perform_capture(x1, y1, x2, y2))

    def perform_capture(self, x1, y1, x2, y2):
        # 防止誤觸 (截圖太小)
        if (x2 - x1) < 5 or (y2 - y1) < 5:
            self.destroy()
            return

        try:
            # 擷取螢幕實際內容
            # bbox = (left, top, right, bottom)
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.callback(img)
        except Exception as e:
            print(f"Capture Error: {e}")
        finally:
            self.destroy()

# ================= 主程式 =================
class OCRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CL_Scan - 快速文字辨識工具")
        self.geometry("450x650")
        
        # 介面佈局配置
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # 讓文字框區域可伸縮

        # 1. 頂部按鈕
        self.btn_capture = ctk.CTkButton(
            self, 
            text="開始截圖", 
            command=self.start_snipping,
            height=50,
            font=("Microsoft JhengHei UI", 16, "bold"),
            fg_color="#106EBE", # 微軟藍
            hover_color="#005A9E"
        )
        self.btn_capture.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # 2. 預覽區域 Frame
        self.preview_container = ctk.CTkFrame(self, fg_color="#202020")
        self.preview_container.grid(row=1, column=0, padx=20, pady=0)
        
        self.lbl_image = ctk.CTkLabel(
            self.preview_container, 
            text="[ 預覽圖片 ]", 
            width=256, 
            height=256,
            corner_radius=8
        )
        self.lbl_image.pack(padx=5, pady=5)

        # 3. 狀態提示
        self.lbl_status = ctk.CTkLabel(
            self, 
            text="準備就緒，請點擊上方按鈕開始", 
            text_color="#AAAAAA",
            font=("Microsoft JhengHei UI", 12)
        )
        self.lbl_status.grid(row=2, column=0, pady=(10, 5))

        # 4. 結果文字框 (包含標題)
        lbl_result_title = ctk.CTkLabel(self, text="辨識結果 (點擊內容複製):", anchor="w")
        lbl_result_title.grid(row=3, column=0, padx=20, pady=(10,0), sticky="nw")

        self.textbox = ctk.CTkTextbox(
            self, 
            font=("Consolas", 14),
            fg_color="#1D1D1D",
            text_color="#FFFFFF",
            border_color="#444444",
            border_width=1
        )
        self.textbox.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="nsew")
        
        # 綁定複製功能
        self.textbox.bind("<Button-1>", self.copy_to_clipboard)

    def start_snipping(self):
        # 最小化主視窗，避免擋住
        self.iconify()
        # 啟動截圖遮罩
        SnippingTool(self, self.process_image)

    def process_image(self, image):
        # 截圖完成，恢復主視窗
        self.deiconify()
        
        # --- 1. 處理預覽圖 ---
        # 製作顯示用的縮圖，保持比例，不變形
        display_img = image.copy()
        display_img.thumbnail((256, 256))
        ctk_img = ctk.CTkImage(light_image=display_img, dark_image=display_img, size=display_img.size)
        
        self.lbl_image.configure(image=ctk_img, text="")
        
        # --- 2. OCR 辨識 ---
        self.lbl_status.configure(text="🔍 正在分析文字與符號...", text_color="#FFD700") # 金色提示
        self.update_idletasks()

        try:
            # 設定參數: 
            # lang: 使用自動偵測的語言
            # config: 保留特殊符號
            custom_config = r'--oem 3 --psm 6' 
            # --psm 6: 假設是一個統一的文字塊 (適合擷取參數)
            
            text = pytesseract.image_to_string(
                image, 
                lang=TESSERACT_LANG,  # 使用自動偵測的語言
                config=custom_config
            )
            
            # 清理結果 (去除過多空白行，但保留參數格式)
            clean_text = "\n".join([line for line in text.splitlines() if line.strip()])
            
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", clean_text)
            
            self.lbl_status.configure(text="✅ 辨識完成！點擊下方文字框即可複製", text_color="#2CC985")
            
        except Exception as e:
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", f"錯誤: {e}\n\n可能原因: 未安裝 Tesseract 中文包")
            self.lbl_status.configure(text="❌ 辨識發生錯誤", text_color="#FF5555")

    def copy_to_clipboard(self, event):
        content = self.textbox.get("0.0", "end").strip()
        if content:
            pyperclip.copy(content)
            self.lbl_status.configure(text="📋 已複製內容到剪貼簿！", text_color="#00BFFF")
            self.after(2000, lambda: self.lbl_status.configure(text="✅ 辨識完成！點擊下方文字框即可複製", text_color="#2CC985"))

if __name__ == "__main__":
    app = OCRApp()
    app.mainloop()