import os
import sys
import pyautogui
import pytesseract
import psutil
import GPUtil
import keyboard
import time
import requests
import glob
import shutil
import subprocess
import pygetwindow as gw
import webbrowser

# OCR Yolu - Tesseract'ın kurulu olduğu yer
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def minimize_victus():
    """Victus terminalini pusuya yatırır."""
    try:
        # "Victus" ismini içeren tüm pencereleri küçült
        for win in gw.getWindowsWithTitle("Victus"):
            if not win.isMinimized:
                win.minimize()
    except: pass

def log_error(error_message):
    """Hataları Üstad için rapora kaydeder."""
    try:
        zaman = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("Victus_Hata_Kayitlari.txt", "a", encoding="utf-8") as f:
            f.write(f"[{zaman}] EKSİK/HATA: {error_message}\n")
        return "Geliştirme raporuna kaydedildi Üstad."
    except: return "Rapor tutulamadı."

def self_update():
    """GitHub'dan güncel kodları çeker ve Victus'u yeniden doğurur."""
    try:
        base_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/"
        files = ["tools.py", "brain.py", "main.py", "audio_manager.py"]
        
        for file in files:
            content = requests.get(base_url + file).text
            if "import" in content:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(content)
        
        print("[SİSTEM] Yeni kodlar zihne kazındı. Victus yeniden başlatılıyor...")
        time.sleep(1)
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e: return f"Güncelleme hatası: {e}"

def find_and_focus_tab(tab_name):
    """Agresif Sekme Radarı: Önce pencere listesine bakar, yoksa sekmeleri döner."""
    minimize_victus()
    try:
        # 1. Aşama: Direkt Pencere Başlığı Kontrolü (Jet Hızında)
        for title in gw.getAllTitles():
            if tab_name.lower() in title.lower():
                win = gw.getWindowsWithTitle(title)[0]
                if win.isMinimized: win.restore()
                win.activate()
                return f"'{tab_name}' sekmesini direkt buldum ve odaklandım Paşam."

        # 2. Aşama: Tarayıcıyı Bul ve Sekmeleri Gez
        browser_found = False
        target_browsers = ["google chrome", "microsoft edge", "opera", "brave"]
        for title in gw.getAllTitles():
            if any(browser in title.lower() for browser in target_browsers):
                win = gw.getWindowsWithTitle(title)[0]
                if win.isMinimized: win.restore()
                win.activate()
                browser_found = True
                break
        
        if not browser_found: return "Tarayıcı açık değil Üstad, önce açmamı ister misin?"
        
        # Sekmeleri hızlıca döngüye al
        time.sleep(0.5)
        for _ in range(15): # 30 çok fazlaydı, 15 tur yeterli
            current_title = gw.getActiveWindowTitle()
            if current_title and tab_name.lower() in current_title.lower():
                return f"'{tab_name}' sekmesini gezerek buldum Paşam."
            keyboard.send("ctrl+tab")
            time.sleep(0.2)
        
        return f"'{tab_name}' sekmesini tüm sekmelerde aradım ama bulamadım Üstad."
    except Exception as e: return f"Radar hatası: {e}"

def open_app(app_name):
    """Uygulama, site veya ayarları hatasız açar."""
    app_lower = app_name.lower()
    
    # Chrome ve Gemini Fixi
    if "chrome" in app_lower or "gemini" in app_lower:
        url = "https://gemini.google.com" if "gemini" in app_lower else ""
        # 'start chrome' Windows için en temiz komuttur
        subprocess.Popen(f"start chrome {url}", shell=True)
        return "Chrome/Gemini emrin üzerine başlatıldı Paşam."

    # Web Siteleri
    sites = {"youtube": "https://www.youtube.com", "google": "https://www.google.com", "github": "https://www.github.com"}
    if app_lower in sites:
        webbrowser.open(sites[app_lower])
        return f"{app_name} açıldı."

    # Windows Ayarları
    settings_map = {"ses": "sound", "ekran": "display", "internet": "network", "güncelleme": "windowsupdate", "ayarlar": "home"}
    for key, val in settings_map.items():
        if key in app_lower:
            os.system(f"start ms-settings:{val}")
            return f"{key.capitalize()} ayarları açıldı."

    # Genel Uygulama Başlatma
    try:
        os.system(f'start "" "{app_name}"')
        return f"'{app_name}' için başlatma komutu gönderildi."
    except:
        return f"'{app_name}' uygulamasını bulamadım Üstad."

def click_on_text(target_text):
    """Ekranda yazı bulur ve tıklar."""
    minimize_victus()
    time.sleep(0.7) # Ekranın oturması için biraz daha süre
    try:
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            if target_text.lower() in text.lower() and text.strip():
                x = data['left'][i] + data['width'][i]//2
                y = data['top'][i] + data['height'][i]//2
                pyautogui.click(x, y)
                return f"'{target_text}' tıklandı."
        return f"Ekranda '{target_text}' yazısını seçemedim Paşam."
    except Exception as e: return f"OCR Hatası: {e}"

def file_manager(action, path, destination=None):
    """Kopyala, taşı veya sil işlerini halleder."""
    try:
        path = os.path.abspath(path)
        if action == "copy" and destination:
            dest = os.path.abspath(destination)
            if os.path.isdir(path): shutil.copytree(path, dest, dirs_exist_ok=True)
            else: shutil.copy(path, dest)
            return "Kopyalama başarılı Paşam."
        elif action == "move" and destination:
            shutil.move(path, os.path.abspath(destination))
            return "Taşıma işlemi tamam."
        elif action == "delete":
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
            return "Dosya/Klasör imha edildi."
        return "Geçersiz dosya işlemi."
    except Exception as e: return f"Dosya hatası: {e}"

def software_manager(action, app_name):
    """Winget ile sessiz kurulum/kaldırma."""
    try:
        # --force ekledim ki takılmasın
        cmd = f"winget {action} {app_name} --silent --accept-source-agreements --accept-package-agreements --force"
        subprocess.Popen(cmd, shell=True)
        return f"{app_name} için {action} işlemi arka planda, sessizce başlatıldı."
    except: return "Winget sisteminde bir sorun var Üstad."

def get_system_info():
    """RTX 4050 ve işlemci durumunu raporlar."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs()
        gpu_info = f"{gpus[0].name} ({gpus[0].temperature}°C)" if gpus else "GPU Yok"
        return f"CPU: %{cpu}, RAM: %{ram}, GPU: {gpu_info} Üstad."
    except: return "Sistem bilgileri okunamadı."

def read_screen():
    """Ekrandaki her şeyi okur ve özetler."""
    minimize_victus()
    time.sleep(0.8)
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        if not text.strip(): return "Ekran şu an boş veya okunamıyor Paşam."
        return f"Ekran İçeriği: {text[:500]}..."
    except: return "Ekran okuma hatası."

def type_text(text):
    """Klavye simülasyonu (Kısayol desteğiyle)."""
    time.sleep(0.5)
    try:
        if "+" in text:
            keyboard.send(text.lower())
        else:
            keyboard.write(text)
            keyboard.send("enter")
        return "Klavye girişi yapıldı Üstad."
    except: return "Yazma hatası."

def click_and_type(target_text, input_text):
    """Yazıya tıklar ve metni yapıştırır."""
    res = click_on_text(target_text)
    if "tıklandı" in res:
        time.sleep(0.3)
        keyboard.write(input_text)
        keyboard.send("enter")
        return f"'{target_text}' alanına '{input_text}' yazıldı."
    return res

def steam_search(query):
    """Steam'de oyun arar."""
    minimize_victus()
    os.system(f"start steam://openurl/https://store.steampowered.com/search/?term={query}")
    return f"Steam'de '{query}' aranıyor Paşam."

def system_control(action):
    """Ses seviyesi kontrolleri."""
    if "ac" in action: [keyboard.send("volume up") for _ in range(5)]
    elif "kis" in action: [keyboard.send("volume down") for _ in range(5)]
    elif "kapat" in action: keyboard.send("volume mute")
    return "Ses ayarlandı Üstad."

def media_control(action):
    """Oynatma kontrolleri."""
    actions = {"play": "play/pause media", "next": "next track", "prev": "previous track"}
    if action in actions:
        keyboard.send(actions[action])
        return "Medya kontrol edildi."
    return "Bilinmeyen medya komutu."

def save_memory(note):
    """Önemli notları Victus'un hafızasına kazır."""
    try:
        with open("Victus_Hafiza.txt", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d')}] - {note}\n")
        return "Hafızaya alındı Üstad, unutmam."
    except: return "Hafıza yazma hatası."

def exit_system():
    """Victus'u kapatır."""
    print("Victus pusuya yatıyor... Görüşürüz Paşam.")
    os._exit(0)

# Gereksiz fonksiyonları ve hatalı döngüleri ayıkladım Üstad.
# Bu kod direkt senin sistemine tam uyumlu.
