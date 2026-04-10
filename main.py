import tkinter as tk
import customtkinter as ctk
from core.engine import SonicEngine
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import sys
import ctypes
import os

# --- AUTO-AVVIO COME AMMINISTRATORE ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

ctk.set_appearance_mode("dark")

class SonicBoostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SonicBoost PRO")
        self.geometry("400x550") # Altezza aumentata per i nuovi tasti
        self.resizable(False, False)
        
        self.protocol('WM_DELETE_WINDOW', self.hide_window) 

        self.engine = SonicEngine()
        self.engine.start()

        # --- UI ---
        self.label = ctk.CTkLabel(self, text="SONIC BOOST PRO", font=("Arial", 26, "bold"), text_color="#00CCFF")
        self.label.pack(pady=25)

        # BOX STATO DRIVER
        self.status_frame = ctk.CTkFrame(self, fg_color="#2B2B2B")
        self.status_frame.pack(pady=10, padx=20, fill="x")

        if not self.engine.driver_installed:
            self.status_label = ctk.CTkLabel(self.status_frame, text="⚠️ DRIVER MANCANTE", text_color="orange", font=("Arial", 13, "bold"))
            self.status_label.pack(pady=5)
            
            self.install_btn = ctk.CTkButton(
                self, 
                text="Installa Driver Professionale", 
                command=self.start_download,
                fg_color="#1f538d",
                hover_color="#14375e"
            )
            self.install_btn.pack(pady=10)
        else:
            self.status_label = ctk.CTkLabel(self.status_frame, text="✅ DRIVER ATTIVO", text_color="#2ECC71", font=("Arial", 13, "bold"))
            self.status_label.pack(pady=5)

        # SLIDER BOOST
        self.slider = ctk.CTkSlider(
            self, 
            from_=1.0, 
            to=4.0, 
            command=self.update_volume, 
            progress_color="#00CCFF",
            button_color="#00CCFF"
        )
        self.slider.set(1.0)
        self.slider.pack(pady=35, padx=30, fill="x")

        self.vol_label = ctk.CTkLabel(self, text="Potenza: Normale (0dB)", font=("Arial", 16))
        self.vol_label.pack(pady=10)

        # --- NUOVO TASTO CONFIGURAZIONE DISPOSITIVI ---
        self.config_btn = ctk.CTkButton(
            self, 
            text="Configura Nuovi Dispositivi", 
            command=self.engine.open_configurator,
            fg_color="#333333",
            hover_color="#444444"
        )
        self.config_btn.pack(pady=20)

        self.info_footer = ctk.CTkLabel(self, text="Modalità: Bypassing Hardware Limits", font=("Arial", 10), text_color="gray")
        self.info_footer.pack(side="bottom", pady=15)

    def start_download(self):
        self.install_btn.configure(state="disabled", text="Inizializzazione...")
        def update_ui_percent(percent):
            self.after(0, lambda: self.install_btn.configure(text=f"Scaricando... {percent}"))
        self.engine.install_driver(callback_progress=update_ui_percent)

    def update_volume(self, value):
        db = (value - 1.0) * 15.0 # Boost massimo a +45dB
        text = f"Potenza: +{db:.1f} dB"
        color = "white" if value < 2.5 else "#FF4444"
        self.vol_label.configure(text=text, text_color=color)
        self.engine.set_gain(value)

    def hide_window(self):
        self.withdraw()
        self.create_tray_icon()

    def show_window(self, icon=None, item=None):
        if icon: icon.stop()
        self.after(0, self.deiconify)

    def quit_app(self, icon, item):
        icon.stop()
        self.engine.stop()
        self.destroy()
        sys.exit()

    def create_tray_icon(self):
        img = Image.new('RGB', (64, 64), color=(0, 204, 255))
        d = ImageDraw.Draw(img)
        d.polygon([(20, 15), (20, 49), (50, 32)], fill=(255, 255, 255))
        menu = (item('Apri SoundBooster', self.show_window), item('Esci', self.quit_app))
        self.icon = pystray.Icon("SonicBoost", img, "SonicBoost Active", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

if __name__ == "__main__":
    app = SonicBoostApp()
    app.mainloop()