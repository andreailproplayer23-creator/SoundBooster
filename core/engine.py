import os
import requests
import subprocess
import threading
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SonicEngine:
    def __init__(self):
        self.config_dir = r"C:\Program Files\EqualizerAPO\config"
        self.config_path = os.path.join(self.config_dir, "config.txt")
        self.driver_installed = os.path.exists(self.config_path)

    def open_configurator(self):
        """Apre l'utility per selezionare le cuffie/dispositivi"""
        configurator_path = r"C:\Program Files\EqualizerAPO\Configurator.exe"
        if os.path.exists(configurator_path):
            print("🛠️ Apertura Configurator...")
            subprocess.Popen([configurator_path])
        else:
            print("❌ Errore: Configurator non trovato. Installa prima il driver.")

    def install_driver(self, callback_progress=None):
        def run_download():
            urls = [
                "https://netcologne.dl.sourceforge.net/project/equalizerapo/1.3/EqualizerAPO64-1.3.exe",
                "https://github.com/EqualizerAPO/EqualizerAPO/releases/download/1.3/EqualizerAPO64-1.3.exe",
                "https://nchc.dl.sourceforge.net/project/equalizerapo/1.3/EqualizerAPO64-1.3.exe"
            ]
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            installer = os.path.join(os.environ["TEMP"], "apo_setup.exe")
            success = False

            for i, url in enumerate(urls):
                try:
                    if callback_progress: callback_progress(f"Link {i+1}...")
                    if os.path.exists(installer): os.remove(installer)

                    response = requests.get(url, headers=headers, stream=True, timeout=15, verify=False)
                    
                    if response.status_code == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        with open(installer, "wb") as f:
                            downloaded = 0
                            for data in response.iter_content(chunk_size=1024*64):
                                downloaded += len(data)
                                f.write(data)
                                if callback_progress and total_size > 0:
                                    percent = int((downloaded / total_size) * 100)
                                    callback_progress(f"{percent}%")
                        
                        if os.path.getsize(installer) > 2000000:
                            success = True
                            break
                except:
                    continue

            if success:
                if callback_progress: callback_progress("Avvio...")
                os.startfile(installer)
            else:
                if callback_progress: callback_progress("FALLITO")

        threading.Thread(target=run_download, daemon=True).start()

    def start(self):
        if self.driver_installed: self._write_db(0.0)

    def _write_db(self, db):
        if self.driver_installed:
            try:
                os.makedirs(self.config_dir, exist_ok=True)
                with open(self.config_path, "w") as f:
                    f.write(f"Preamp: {db:.1f} dB")
            except: pass

    def set_gain(self, multiplier):
        if self.driver_installed:
            # 1.0 -> 0dB, 4.0 -> 45dB
            db_boost = (multiplier - 1.0) * 15.0 
            self._write_db(db_boost)

    def stop(self):
        self._write_db(0.0)