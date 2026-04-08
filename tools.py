import os, sys, pyautogui, pytesseract, psutil, GPUtil, keyboard, time, requests, glob, shutil, subprocess
import pygetwindow as gw

# OCR Yolu - Tesseract'ın kurulu olduğu yer
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def minimize_victus():
    """Victus terminalini gizler."""
    try:
        for win in gw.getWindowsWithTitle("Victus"):
            win.minimize()
    except: pass

def log_error(error_message):
    """Hataları rapora kaydeder."""
    try:
        zaman = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("Victus_Hata_Kayitlari.txt", "a", encoding="utf-8") as f:
            f.write(f"[{zaman}] EKSİK/HATA: {error_message}\n")
        return "Geliştirme raporuna kaydedildi Üstad."
    except: return "Rapor tutulamadı."

def self_update():
    """GitHub'dan güncel kodları çeker ve sistemi yeniden başlatır."""
    try:
        tools_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/tools.py"
        brain_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/brain.py"
        main_url  = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/main.py"
        audio_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/audio_manager.py"

        yeni_tools = requests.get(tools_url).text
        yeni_brain = requests.get(brain_url).text
        yeni_main  = requests.get(main_url).text
        yeni_audio = requests.get(audio_url).text

        if "import" in yeni_tools and "import" in yeni_brain:
            with open("tools.py", "w", encoding="utf-8") as f: f.write(yeni_tools)
            with open("brain.py", "w", encoding="utf-8") as f: f.write(yeni_brain)
            with open("main.py", "w", encoding="utf-8") as f: f.write(yeni_main)
            with open("audio_manager.py", "w", encoding="utf-8") as f: f.write(yeni_audio)
            print("[SİSTEM] Yeni kodlar zihne kazındı. Victus yeniden doğuyor...")
            time.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv)
        else: return "Güncelleme dosyaları hatalı."
    except Exception as e: return f"Güncelleme hatası: {e}"

def find_and_focus_tab(tab_name):
    """Agresif Sekme Radarı: Tarayıcıyı bulur ve sekmeyi yakalar."""
    minimize_victus()
    try:
        browser_found = False
        for title in gw.getAllTitles():
            if "google chrome" in title.lower() or "microsoft edge" in title.lower():
                win = gw.getWindowsWithTitle(title)[0]
                if win.isMinimized: win.restore()
                win.activate()
                browser_found = True
                break
        if not browser_found: return "Tarayıcı açık değil Üstad."
        
        time.sleep(0.5)
        for _ in range(30):
            current_title = gw.getActiveWindowTitle()
            if current_title and tab_name.lower() in current_title.lower():
                return f"'{tab_name}' bulundu Paşam."
            keyboard.send("ctrl+tab")
            time.sleep(0.3)
        return f"'{tab_name}' sekmesini bulamadım."
    except Exception as e: return f"Radar hatası: {e}"

def browser_control(action):
    """Sekme değiştirir veya kapatır."""
    minimize_victus()
    time.sleep(0.3)
    try:
        if action == "next_tab": keyboard.send("ctrl+tab")
        elif action == "prev_tab": keyboard.send("ctrl+shift+tab")
        elif action == "close_tab": keyboard.send("ctrl+w")
        return "Sekme işlemi tamam."
    except Exception as e: return f"Hata: {e}"

def file_manager(action, path, destination=None):
    """Kopyala, taşı veya sil."""
    try:
        path = os.path.abspath(path)
        if action == "copy" and destination:
            dest = os.path.abspath(destination)
            if os.path.isdir(path): shutil.copytree(path, dest)
            else: shutil.copy(path, dest)
            return "Kopyalandı."
        elif action == "move" and destination:
            shutil.move(path, os.path.abspath(destination))
            return "Taşındı."
        elif action == "delete":
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
            return "Silindi."
    except Exception as e: return f"Dosya hatası: {e}"

def software_manager(action, app_name):
    """Winget ile sessiz kurulum/kaldırma."""
    try:
        cmd = f"winget {action} {app_name} --silent --accept-source-agreements --accept-package-agreements"
        subprocess.Popen(cmd, shell=True)
        return f"{app_name} işlemi arka planda başlatıldı."
    except: return "Winget hatası."

def steam_search(query):
    """Steam üzerinde oyun arar."""
    minimize_victus()
    os.system(f"start steam://openurl/https://store.steampowered.com/search/?term={query}")
    return "Steam araması açıldı Paşam."

def focus_window(app_name):
    """İstenen pencereyi en öne getirir."""
    try:
        minimize_victus()
        windows = [w for w in gw.getAllWindows() if app_name.lower() in w.title.lower()]
        if windows:
            win = windows[0]
            if win.isMinimized: win.restore()
            win.activate()
            return f"{app_name} odaklandı."
        return "Pencere bulunamadı."
    except: return "Odaklama hatası."

def open_app(app_name):
    """Uygulama, site veya ayarları açar."""
    app_lower = app_name.lower()
    if "gemini" in app_lower:
        res = find_and_focus_tab("Gemini")
        if "buldum" not in res:
            os.system("start https://gemini.google.com")
            return "Gemini yeni sekmede açıldı."
        return res
    sites = {"youtube": "https://www.youtube.com", "google": "https://www.google.com", "github": "https://www.github.com"}
    if app_lower in sites:
        os.system(f"start {sites[app_lower]}")
        return f"{app_name} açıldı."
    
    settings_map = {"ses": "sound", "ekran": "display", "internet": "network", "güncelleme": "windowsupdate"}
    for key, val in settings_map.items():
        if key in app_lower:
            os.system(f"start ms-settings:{val}")
            return f"{key} ayarları açıldı."
            
    os.system(f'start "" "{app_name}"')
    return f"{app_name} başlatma komutu gönderildi."

def click_on_text(target_text):
    """Ekranda yazı bulur ve tıklar."""
    minimize_victus()
    time.sleep(0.5)
    try:
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            if target_text.lower() in text.lower():
                pyautogui.click(data['left'][i] + data['width'][i]//2, data['top'][i] + data['height'][i]//2)
                return f"'{target_text}' tıklandı."
        return "Yazı ekranda bulunamadı."
    except: return "OCR hatası."

def click_and_type(target_text, input_text):
    """Metne tıklar ve hemen ardından yazar."""
    res = click_on_text(target_text)
    if "tıklandı" in res:
        time.sleep(0.2); keyboard.write(input_text); keyboard.send("enter")
        return f"'{target_text}' üzerine yazıldı."
    return res

def type_text(text):
    """Klavye simülasyonu."""
    time.sleep(0.5)
    if "+" in text: keyboard.send(text.lower())
    else: keyboard.write(text); keyboard.send("enter")
    return "Klavye girişi yapıldı."

def read_screen():
    """Ekrandaki her şeyi okur."""
    minimize_victus()
    try:
        screenshot = pyautogui.screenshot()
        return f"Ekran İçeriği: {pytesseract.image_to_string(screenshot)[:800]}"
    except: return "Okuma hatası."

def get_system_info():
    """Sistem kaynaklarını okur."""
    try:
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs(); gpu = gpus[0].name if gpus else "GPU Yok"
        return f"CPU: %{cpu}, RAM: %{ram}, GPU: {gpu}"
    except: return "Bilgi alınamadı."

def system_control(action):
    """Ses seviyesi ayarı."""
    if "ac" in action: [keyboard.send("volume up") for _ in range(5)]
    elif "kis" in action: [keyboard.send("volume down") for _ in range(5)]
    elif "kapat" in action: keyboard.send("volume mute")
    return "Ses ayarlandı."

def media_control(action):
    """Oynatma kontrolleri."""
    if "play" in action: keyboard.send("play/pause media")
    elif "next" in action: keyboard.send("next track")
    elif "prev" in action: keyboard.send("previous track")
    return "Medya kontrol edildi."

def save_memory(note):
    """Önemli notları kaydeder."""
    with open("Victus_Hafiza.txt", "a", encoding="utf-8") as f: f.write(f"- {note}\n")
    return "Hafızaya alındı Paşam."

def exit_system():
    """Victus'u kapatır."""
    os._exit(0)
