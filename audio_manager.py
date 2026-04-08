# audio_manager.py
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
from faster_whisper import WhisperModel
import io
import os
import time
import threading

pygame.mixer.init()

print("\n[SİSTEM] Jet Motoru (Faster-Whisper - SMALL Model) Yüklendi...")
whisper_model = WhisperModel("small", device="cuda", compute_type="float16")
print("[SİSTEM] Kulaklar Açık ve VAD Filtresi Devrede!\n")

stop_flag = False

# ==========================================
# ÇÖZÜM 1: SAĞLAMLAŞTIRILMIŞ ACİL FREN
# ==========================================
def acil_susturucu():
    global stop_flag
    r_stop = sr.Recognizer()
    
    # Mikrofonu sürekli aç-kapa yapmak yerine BİR KERE açıyoruz, hep açık kalıyor.
    with sr.Microphone() as source:
        r_stop.adjust_for_ambient_noise(source, duration=1) # Odanın sessizliğini ölçer
        r_stop.energy_threshold = 800 # 2000'den 800'e çektik, artık bağırmana gerek yok
        
        while True:
            # Sadece Victus konuşurken dinle
            if pygame.mixer.music.get_busy():
                try:
                    # Dinleme süresini uzattık ki kelimeyi kaçırmasın
                    audio = r_stop.listen(source, timeout=0.5, phrase_time_limit=1.5)
                    komut = r_stop.recognize_google(audio, language="tr-TR").lower()
                    
                    if any(k in komut for k in ["dur", "sus", "yeter", "kes", "iptal"]):
                        stop_flag = True
                        print("\n[!!!] ÜSTAD FRENE BASTI, VİCTUS SUSTURULDU!")
                except:
                    pass
            else:
                time.sleep(0.1)

# Arka planda çalışması için Thread başlat
threading.Thread(target=acil_susturucu, daemon=True).start()

# ==========================================
# KONUŞMA MOTORU
# ==========================================
async def speak(text):
    global stop_flag
    if not text: return
    stop_flag = False 
    
    text = text.replace("*", "").replace("`", "").replace("#", "").replace("_", "").strip()
    temp_file = f"temp_ses_{int(time.time())}.mp3"
    
    try:
        communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural", rate="+10%")
        await communicate.save(temp_file)
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if stop_flag:
                pygame.mixer.music.stop() # Fren çekildiyse anında sus
                break
            await asyncio.sleep(0.05)
            
        pygame.mixer.music.unload()
        if os.path.exists(temp_file): 
            try: os.remove(temp_file)
            except: pass
    except Exception as e:
        print(f"[Ses Hatası]: {e}")

# ==========================================
# DİNLEME MOTORU (OPTİMİZE EDİLDİ)
# ==========================================
def listen():
    r = sr.Recognizer()
    r.pause_threshold = 1.0 # 1.5 saniye çok uzundu, seni 1 saniye bekleyip hemen çözüme geçecek
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            print("\n[Pusuda Bekliyorum...]")
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
            
            wav_data = audio.get_wav_data()
            
            # ÇÖZÜM 2: Kopya Kağıdını güncelledik. Artık "Ramzan" gibi saçmalamayacak.
            kopya_kagidi = "Victus, Spotify, Enes, Üstad, YouTube, Chrome, aç, kapat, sus, dur, hafıza, kaydet, not al, belleğe yaz."
            
            segments, info = whisper_model.transcribe(
                io.BytesIO(wav_data), 
                beam_size=5, 
                language="tr",
                vad_filter=True, 
                # Kelimelerin başını sonunu yutmasın diye VAD filtresine esneklik payı (500ms) verdik
                vad_parameters=dict(min_silence_duration_ms=500), 
                initial_prompt=kopya_kagidi 
            )
            
            metin = "".join([s.text for s in segments]).strip().lower()
            return metin
    except Exception:
        return ""