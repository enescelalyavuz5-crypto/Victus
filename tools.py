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
    """Victus'un kendi kendini geliştirmesi için karşılaştığı hataları raporlar."""
    try:
        zaman = time.strftime('%Y-%m-%d %H:%M:%S')
        with open("Victus_Hata_Kayitlari.txt", "a", encoding="utf-8") as f:
            f.write(f"[{zaman}] EKSİK/HATA: {error_message}\n")
        return "Geliştirme raporuna kaydedildi Üstad."
    except: return "Rapor tutulamadı."

def self_update():
    """İnternetteki yeni kodları çeker ve sistemi güncelleyip yeniden başlatır."""
    try:
        # ÜSTAD, KOPYALADIĞIN 4 RAW LİNKİNİ BURAYA YAPIŞTIR:
        tools_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/tools.py"
        brain_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/brain.py"
        main_url  = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/main.py"
        audio_url = "https://raw.githubusercontent.com/enescelalyavuz5-crypto/Victus/refs/heads/main/audio_manager.py"

        # Dosyaları internetten indir
        yeni_tools = requests.get(tools_url).text
        yeni_brain = requests.get(brain_url).text
        yeni_main  = requests.get(main_url).text
        yeni_audio = requests.get(audio_url).text

        # Güvenlik kontrolü (Dosyalar boş gelmediyse)
        if "import" in yeni_tools and "import" in yeni_brain:
            
            # Bilgisayardaki eski dosyaların üzerine acımasızca yaz
            with open("tools.py", "w", encoding="utf-8") as f: f.write(yeni_tools)
            with open("brain.py", "w", encoding="utf-8") as f: f.write(yeni_brain)
            with open("main.py", "w", encoding="utf-8") as f: f.write(yeni_main)
            with open("audio_manager.py", "w", encoding="utf-8") as f: f.write(yeni_audio)
            
            print("[SİSTEM] Yeni kodlar zihne kazındı. Victus yeniden doğuyor...")
            time.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv) # Fişi çekip takar
        else:
            return "İnternetteki dosyalar boş veya hatalı Paşam, güncelleme iptal."
    except Exception as e: return f"Güncelleme hatası: {e}"

def browser_control(action):
    """Tarayıcıda sekmeler arası gezinir."""
    minimize_victus()
    time.sleep(0.3)
    try:
        if action == "next_tab": keyboard.send("ctrl+tab")
        elif action == "prev_tab": keyboard.send("ctrl+shift+tab")
        elif action == "close_tab": keyboard.send("ctrl+w")
        return "Sekme komutu uygulandı."
    except Exception as e: return f"Sekme işleminde pürüz: {e}"

def file_manager(action, path, destination=None):
    """Dosya/Klasör kopyalar, taşır, siler."""
    try:
        path = os.path.abspath(path)
        if action == "copy" and destination:
            destination = os.path.abspath(destination)
            if os.path.isdir(path): shutil.copytree(path, destination)
            else: shutil.copy(path, destination)
            return f"'{path}' başarıyla kopyalandı."
        elif action == "move" and destination:
            destination = os.path.abspath(destination)
            shutil.move(path, destination)
            return f"'{path}' yeni yerine taşındı."
        elif action == "delete":
            if os.path.isdir(path): shutil.rmtree(path)
            else: os.remove(path)
            return f"'{path}' tamamen silindi."
    except Exception as e: return f"Dosya hatası: {e}"

def software_manager(action, app_name):
    """Winget ile sessiz program kurar/kaldırır."""
    try:
        if action == "install":
            subprocess.Popen(f"winget install {app_name} --silent --accept-source-agreements --accept-package-agreements", shell=True)
            return f"'{app_name}' arka planda kuruluyor Paşam."
        elif action == "uninstall":
            subprocess.Popen(f"winget uninstall {app_name} --silent", shell=True)
            return f"'{app_name}' kaldırılıyor."
    except: return "Winget çalışmadı."

def steam_search(query):
    minimize_victus()
    try:
        os.system(f"start steam://openurl/https://store.steampowered.com/search/?term={query}")
        return f"Steam'de '{query}' jet hızıyla aratıldı."
    except: return "Steam protokolü çalışmadı."

def focus_window(app_name):
    try:
        minimize_victus()
        windows = gw.getWindowsWithTitle(app_name)
        if not windows:
            for title in gw.getAllTitles():
                if app_name.lower() in title.lower():
                    windows = gw.getWindowsWithTitle(title)
                    break
        if windows:
            win = windows[0]
            if win.isMinimized: win.restore()
            win.activate()
            time.sleep(0.3)
            return f"'{app_name}' öne getirildi."
        return "Pencere bulunamadı."
    except: return "Odaklama hatası."

def open_app(app_name):
    app_lower = app_name.lower()
    if "gemini" in app_lower:
        os.system("start https://gemini.google.com")
        return "Gemini açıldı Paşam."
    sites = {"youtube": "https://www.youtube.com", "google": "https://www.google.com", "github": "https://www.github.com"}
    if app_lower in sites:
        os.system(f"start {sites[app_lower]}")
        return f"{app_name} açıldı."

    settings_map = {"ses": "sound", "ekran": "display", "internet": "network", "güncelleme": "windowsupdate"}
    for key, val in settings_map.items():
        if key in app_lower:
            os.system(f"start ms-settings:{val}")
            return f"Windows {key} ayarlarını açtım."

    focus_res = focus_window(app_name)
    if "öne getirildi" in focus_res: return focus_res

    search_paths = [r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\**\*.lnk', os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\**\*.lnk')]
    for path in search_paths:
        for shortcut in glob.glob(path, recursive=True):
            if app_lower in os.path.basename(shortcut).lower():
                os.startfile(shortcut)
                return f"{app_name} başlatıldı."
    
    os.system(f'start "" "{app_name}"')
    return "Komut gönderildi."

def click_on_text(target_text):
    minimize_victus()
    time.sleep(0.5)
    try:
        screenshot = pyautogui.screenshot()
        data = pytesseract.image_to_data(screenshot, lang='eng', output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data['text']):
            if text.strip() and target_text.lower() in text.lower():
                pyautogui.click(data['left'][i] + data['width'][i] // 2, data['top'][i] + data['height'][i] // 2)
                return f"'{target_text}' üzerine tıklandı."
        return "Yazıyı göremedim."
    except: return "Tıklama başarısız."

def click_and_type(target_text, input_text):
    res = click_on_text(target_text)
    if "tıklandı" in res:
        time.sleep(0.2)
        keyboard.write(input_text)
        keyboard.send("enter")
        return f"'{target_text}' kutusuna '{input_text}' yazıldı."
    return res

def type_text(text):
    try:
        time.sleep(0.5)
        if "+" in text.lower() or text.lower() in ["enter", "tab", "esc", "space"]: keyboard.send(text.lower())
        else:
            keyboard.write(text)
            keyboard.send("enter")
        return f"Klavye komutu uygulandı."
    except: return "Yazı yazma hatası."

def read_screen():
    minimize_victus()
    time.sleep(0.5)
    try:
        screenshot = pyautogui.screenshot()
        return f"Ekran: {pytesseract.image_to_string(screenshot, lang='eng')[:800]}"
    except: return "Ekran okunamadı."

def get_system_info():
    try:
        cpu = psutil.cpu_percent(); ram = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs(); gpu_info = f"{gpus[0].name}" if gpus else "GPU Yok"
        return f"Sistem: {gpu_info}, CPU: %{cpu}, RAM: %{ram}"
    except: return "Bilgi alınamadı."

def system_control(action):
    if action == "ses_ac": [keyboard.send("volume up") for _ in range(5)]
    elif action == "ses_kis": [keyboard.send("volume down") for _ in range(5)]
    elif action == "ses_kapat": keyboard.send("volume mute")
    return "Ses ayarlandı."

def media_control(action):
    if action == "play_pause": keyboard.send("play/pause media")
    elif action == "next": keyboard.send("next track")
    elif action == "prev": keyboard.send("previous track")
    return "Medya kontrol edildi."

def save_memory(note):
    with open("Victus_Hafiza.txt", "a", encoding="utf-8") as f: f.write(f"- {note}\n")
    return "Hafızaya kazıdım."
    
    def find_and_focus_tab(tab_name):
    """Tarayıcıda sekmeleri tek tek gezip isminden sekme bulur (Radar Sistemi)."""
    minimize_victus()
    time.sleep(0.5)
    try:
        # Önce Chrome'u veya Edge'i öne çektiğimizden emin olalım
        active = gw.getActiveWindow()
        if not active or ("chrome" not in active.title.lower() and "edge" not in active.title.lower()):
             focus_window("chrome")
             time.sleep(0.5)
             
        # En fazla 30 sekme arar (sonsuz döngüye girmesin diye)
        for _ in range(30):
            title = gw.getActiveWindowTitle()
            if title and tab_name.lower() in title.lower():
                return f"'{title}' sekmesini buldum ve ekrana getirdim Üstad."
            
            keyboard.send("ctrl+tab") # Yan sekmeye geç
            time.sleep(0.3) # Sekmenin yüklenmesi için saliselik bekleme
            
        return f"Tüm sekmeleri gezdim ama '{tab_name}' adında bir sekme bulamadım Paşam."
    except Exception as e: 
        return f"Sekme radarı bozuldu: {e}"

def exit_system():
    os._exit(0)
