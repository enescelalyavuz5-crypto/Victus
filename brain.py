import os, json, asyncio
from openai import AsyncOpenAI
from config import DEEPSEEK_API_KEY, SYSTEM_PROMPT
from tools import *

client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def hafizayi_yukle():
    """Paşamın geçmiş notlarını Victus'un zihnine yükler."""
    if os.path.exists("Victus_Hafiza.txt"):
        with open("Victus_Hafiza.txt", "r", encoding="utf-8") as f:
            return f"\n\n[PAŞAMIN HAFIZASI]:\n{f.read()}"
    return ""

SUS_TALIMATI = "\n\n[KRİTİK]: Tarayıcı işlemleri için 'read_screen' ameleliği yapma, direkt 'find_and_focus_tab' aracını kullan. Eğer kullanıcı 'sus', 'dur' veya 'yeter' derse, hiçbir açıklama yapmadan direkt konuşmayı kes."

# İlk kurulumda sistemi ve hafızayı bağla
memory = [{"role": "system", "content": SYSTEM_PROMPT + hafizayi_yukle() + SUS_TALIMATI}]

# BÜTÜN YETENEKLER ŞEMASI (TAM 18 ADET)
tools_schema = [
    {"type": "function", "function": {"name": "self_update", "description": "Sistemi GitHub üzerinden günceller ve yeniden başlatır.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "find_and_focus_tab", "description": "Tarayıcıda belirli bir sekmeyi isminden (Örn: 'Gemini', 'YouTube') bulana kadar otomatik gezer.", "parameters": {"type": "object", "properties": {"tab_name": {"type": "string"}}, "required": ["tab_name"]}}},
    {"type": "function", "function": {"name": "log_error", "description": "Hataları geliştirme raporuna kaydeder.", "parameters": {"type": "object", "properties": {"error_message": {"type": "string"}}, "required": ["error_message"]}}},
    {"type": "function", "function": {"name": "browser_control", "description": "Sekme değiştirir veya kapatır.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["next_tab", "prev_tab", "close_tab"]}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "file_manager", "description": "Dosya kopyalar, taşır veya siler.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["copy", "move", "delete"]}, "path": {"type": "string"}, "destination": {"type": "string"}}, "required": ["action", "path"]}}},
    {"type": "function", "function": {"name": "software_manager", "description": "Sessizce program kurar veya kaldırır.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["install", "uninstall"]}, "app_name": {"type": "string"}}, "required": ["action", "app_name"]}}},
    {"type": "function", "function": {"name": "steam_search", "description": "Steam üzerinde oyun arar.", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "focus_window", "description": "İstenen pencereyi en öne getirir.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}}},
    {"type": "function", "function": {"name": "open_app", "description": "Uygulama, site veya Windows ayarlarını açar.", "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}}},
    {"type": "function", "function": {"name": "click_on_text", "description": "Ekranda gördüğü yazıya tıklar.", "parameters": {"type": "object", "properties": {"target_text": {"type": "string"}}, "required": ["target_text"]}}},
    {"type": "function", "function": {"name": "click_and_type", "description": "Yazıya tıklar ve metin yazar.", "parameters": {"type": "object", "properties": {"target_text": {"type": "string"}, "input_text": {"type": "string"}}, "required": ["target_text", "input_text"]}}},
    {"type": "function", "function": {"name": "type_text", "description": "Klavye ile yazı yazar veya kısayol gönderir.", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}},
    {"type": "function", "function": {"name": "read_screen", "description": "Ekranın fotoğrafını çeker ve metinleri okur.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_system_info", "description": "CPU, RAM ve GPU bilgilerini verir.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "system_control", "description": "Ses seviyesini ayarlar.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["ses_ac", "ses_kis", "ses_kapat"]}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "media_control", "description": "Müzik veya medya oynatıcıyı kontrol eder.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["play_pause", "next", "prev"]}}, "required": ["action"]}}},
    {"type": "function", "function": {"name": "save_memory", "description": "Gelecekte hatırlanması için not alır.", "parameters": {"type": "object", "properties": {"note": {"type": "string"}}, "required": ["note"]}}},
    {"type": "function", "function": {"name": "exit_system", "description": "Victus sistemini tamamen kapatır.", "parameters": {"type": "object", "properties": {}}}}
]

async def think_and_act(user_input):
    global memory
    memory.append({"role": "user", "content": user_input})
    
    # Hafıza Budama (400 Hatası Engelleyici)
    if len(memory) > 20:
        memory = [memory[0]] + memory[-10:]

    loop_count = 0
    while loop_count < 5:
        try:
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model="deepseek-chat", messages=memory, tools=tools_schema, tool_choice="auto", temperature=0.1
                ), timeout=30.0
            )
            
            msg = response.choices[0].message
            if not msg.tool_calls:
                memory.append({"role": "assistant", "content": msg.content})
                return msg.content
            
            memory.append(msg)
            for t in msg.tool_calls:
                f_name = t.function.name
                args = json.loads(t.function.arguments)
                print(f"[Victus İşlem]: {f_name} -> {args}")
                
                res = "Hata: Fonksiyon çalıştırılamadı."
                
                # TÜM FONKSİYONLARIN BAĞLANTISI
                if f_name == "self_update": res = self_update()
                elif f_name == "find_and_focus_tab": res = find_and_focus_tab(args["tab_name"])
                elif f_name == "log_error": res = log_error(args["error_message"])
                elif f_name == "browser_control": res = browser_control(args["action"])
                elif f_name == "file_manager": res = file_manager(args["action"], args["path"], args.get("destination"))
                elif f_name == "software_manager": res = software_manager(args["action"], args["app_name"])
                elif f_name == "steam_search": res = steam_search(args["query"])
                elif f_name == "focus_window": res = focus_window(args["app_name"])
                elif f_name == "open_app": res = open_app(args["app_name"])
                elif f_name == "click_on_text": res = click_on_text(args["target_text"])
                elif f_name == "click_and_type": res = click_and_type(args["target_text"], args["input_text"])
                elif f_name == "type_text": res = type_text(args["text"])
                elif f_name == "read_screen": res = read_screen()
                elif f_name == "get_system_info": res = get_system_info()
                elif f_name == "system_control": res = system_control(args["action"])
                elif f_name == "media_control": res = media_control(args["action"])
                elif f_name == "save_memory": res = save_memory(args["note"])
                elif f_name == "exit_system": res = exit_system()
                
                memory.append({"role": "tool", "tool_call_id": t.id, "content": str(res)})
            loop_count += 1
        except asyncio.TimeoutError: 
            return "Üstad, DeepSeek'ten cevap gelmedi (30sn). Tekrar dener misin?"
        except Exception as e: 
            return f"Üstad, beynimde bir pürüz çıktı: {e}"
    
    return "İşlem zinciri çok uzadı Paşam, burada duruyorum."
