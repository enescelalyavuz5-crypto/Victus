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
    """GitHub'dan güncel kodları çeker."""
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

def browser_control(action):
    """Tarayıcı kontrolleri."""
    minimize_victus()
    time.sleep(0.3)
    try:
        if action == "next_tab": keyboard.send("ctrl+tab")
        elif action == "prev_tab": keyboard.send("ctrl+shift+tab")
        elif action == "close_tab": keyboard.send("ctrl+w")
        return "Sekme komutu uygulandı."
    except Exception as e: return f"Hata: {e}"

def find_and_focus_tab(tab_name):
    """Tarayıcıyı bulur ve sekme ismine göre radarı çalıştırır."""
    minimize_victus()
    try:
        # Chrome veya Edge'i bul ve zorla öne getir
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
        for _ in range(30): # 30 sekmeye kadar tara
            current_title = gw.getActiveWindowTitle()
            if current_title and tab_name.lower() in current_title.lower():
                return f"'{tab_name}' sekmesini buldum ve odaklandım Paşam."
            
            keyboard.send("ctrl+tab")
            time.sleep(0.3)
            
        return f"'{tab_name}' sekmesini bulamadım."
    except Exception as e: return f"Radar hatası: {e}"

def file_manager(action, path, destination=None):
    """Dosya işlemleri."""
    try:
        path = os.path.abspath(path)
        if action == "copy" and destination:
            destination = os.path.abspath(destination)
            if os.path.isdir(path): shutil.copytree(path, destination)
            else: shutil.copy(path, destination)
            return "Kopyalandı."
        elif action == "move" and destination:
            shutil.move(path, os.path.abspath(destination))
            return "Taşındı."
        elif action == "delete":
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
            return "Silindi."
    except Exception as e: return f"Hata: {e}"

def software_manager(action, app_name):
    """Uygulama kur/kaldır."""
    try:
        cmd = f"winget {action} {app_name} --silent"
        subprocess.Popen(cmd, shell=True)
        return f"{app_name} işlemi başlatıldı."
    except: return "Hata oluştu."

def steam_search(query):
    """Steam araması."""
    minimize_victus()
    os.system(f"start steam://openurl/https://store.steampowered.com/search/?term={query}")
    return "Steam araması açıldı."

def focus_window(app_name):
    """Pencereyi öne getirir."""
    try:
        minimize_victus()
        windows = [w for w in gw.getAllWindows() if app_name.lower() in w.title.lower()]
        if windows:
            win = windows[0]
            if win.isMinimized: win.restore()
            win.activate()
            return f"{app_name} öne getirildi."
        return "Pencere bulunamadı."
    except: return "Odaklama hatası."

def open_app(app_name):
    """Program veya site açar."""
    app_lower = app_name.lower()
    if "gemini" in app_lower: os.system("start https://gemini.google.com")
    elif "youtube" in app_lower: os.system("start https://www.youtube.com")
    elif "google" in app_lower: os.system("start https://www.google.com")
    else: os.system(f'start "" "{app_name}"')
    return f"{app_name} açıldı."

def click_on_text(target_text):
    """Ekranda yazı bulup tıklar."""
    minimize_victus()
    time.sleep(0.5)
    try:
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            if target_text.lower() in text.lower():
                pyautogui.click(data['left'][i] + data['width'][i]//2, data['top'][i] + data['height'][i]//2)
                return f"'{target_text}' tıklandı."
        return "Yazı bulunamadı."
    except: return "OCR hatası."

def click_and_type(target_text, input_text):
    """Tıkla ve yaz."""
    res = click_on_text(target_text)
    if "tıklandı" in res:
        time.sleep(0.2); keyboard.write(input_text); keyboard.send("enter")
        return "Yazıldı."
    return res

def type_text(text):
    """Klavye girişi."""
    time.sleep(0.5)
    if "+" in text: keyboard.send(text.lower())
    else: keyboard.write(text); keyboard.send("enter")
    return "Klavye emri verildi."

def read_screen():
    """Ekranı okur."""
    minimize_victus()
    try:
        screenshot = pyautogui.screenshot()
        return f"Ekran: {pytesseract.image_to_string(screenshot)[:500]}"
    except: return "Okunamadı."

def get_system_info():
    """Sistem bilgisi."""
    try:
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        return f"CPU: %{cpu}, RAM: %{ram}"
    except: return "Bilgi alınamadı."

def system_control(action):
    """Ses ayarı."""
    if "ac" in action: keyboard.send("volume up")
    elif "kis" in action: keyboard.send("volume down")
    return "Ses ayarlandı."

def media_control(action):
    """Medya kontrol."""
    if "play" in action: keyboard.send("play/pause media")
    return "Medya komutu."

def save_memory(note):
    """Not alır."""
    with open("Victus_Hafiza.txt", "a", encoding="utf-8") as f: f.write(f"- {note}\n")
    return "Hafızaya alındı."

def exit_system():
    """Kapatır."""
    os._exit(0)
