import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# --- CONFIGURACIÓN SEGÚN TU CURL ---
WUZAPI_SEND_URL = "http://localhost:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    """Envía el mensaje de vuelta a Wuzapi con el formato Phone/Body"""
    if not phone:
        return
        
    # Limpiamos el número (quitamos @s.whatsapp.net si existe)
    clean_phone = phone.split('@')[0]
    
    payload = {
        "Phone": clean_phone,
        "Body": text
    }
    headers = {
        "Token": WUZAPI_TOKEN,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers, timeout=10.0)
            print(f"<- WUZAPI SEND STATUS: {response.status_code}", flush=True)
        except Exception as e:
            print(f"!! Error enviando a Wuzapi: {e}", flush=True)

@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    try:
        # 1. Obtener JSON de forma segura
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"status": "no_json"}, status_code=200)

        # 2. LOG DE DEBUG (Para ver la estructura real en el journalctl)
        print(f"\n--- 📥 DATA RECIBIDA: {data}", flush=True)

        # 3. Intentar extraer de 'data' o de la raíz
        inner = data.get("data", data)
        
        # Mapeo agresivo de todas las llaves posibles
        message = inner.get("message") or inner.get("body") or inner.get("Body") or inner.get("text")
        sender = inner.get("sender") or inner.get("from") or inner.get("Phone") or inner.get("chatId")

        if not message:
            print("-> Evento sin mensaje (visto/presencia) ignorado.", flush=True)
            return JSONResponse({"status": "no_message_content"}, status_code=200)

        print(f"--- 🟢 WHATSAPP IN ---", flush=True)
        print(f"-> DE: {sender}", flush=True)
        print(f"-> MSG: '{message}'", flush=True)

        # 4. Respuesta de Amelia
        reply_text = "Hola, soy Amelia. Recibí tu mensaje y te respondo al puerto 9010."
        
        # Tarea asíncrona para enviar
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: Respuesta programada", flush=True)
        print(f"----------------------\n", flush=True)
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)