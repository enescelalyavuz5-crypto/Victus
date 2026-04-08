# main.py
import asyncio
from audio_manager import listen, speak
from brain import think_and_act

async def victus_core():
    print("=== VICTUS V3 (MODÜLER JARVIS MODU) AKTİF ===")
    await speak("Sistemler devrede ustad, emrini bekliyorum.")
    
    is_sleeping = False
    
    while True:
        soru = await asyncio.to_thread(listen)
        if not soru or len(soru) < 3: continue 
        print(f"[Siz]: {soru}")

        # ÇÖZÜM 4: Spesifik Uyku Komutları ("kapat" kelimesi artık tek başına uyutmaz)
        uyku_komutlari = ["victus uyu", "kendini kapat", "sessiz moda geç", "uyku moduna gir"]
        if any(komut in soru for komut in uyku_komutlari):
            is_sleeping = True
            await speak("Sessiz moda geçiyorum ustad. İhtiyacın olursa seslen.")
            continue
            
        if is_sleeping:
            uyanma_komutlari = ["victus uyan", "aktif ol", "kendini aç", "burada mısın"]
            if any(komut in soru for komut in uyanma_komutlari):
                is_sleeping = False
                await speak("Uyandım ustad, seni dinliyorum.")
            continue

        # Eğer uyumuyorsa düşün ve harekete geç
        print("Victus Düşünüyor... ⚙️")
        cevap = await think_and_act(soru)
        
        if cevap:
            print(f"[Victus]: {cevap}")
            await speak(cevap)

if __name__ == "__main__":
    try:
        asyncio.run(victus_core())
    except KeyboardInterrupt:
        print("\nVictus kapatıldı.")
    except Exception as e:
        print(f"\n[KRİTİK HATA]: {e}")
        input("Çıkmak için Enter'a basın...")