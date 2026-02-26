import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# --- CONFIGURACIÓN ACTUALIZADA ---
# Usamos el puerto 9010 y la IP de la puerta de enlace de Docker
WUZAPI_SEND_URL = "http://172.17.0.1:9010/api/sendText" 
WUZAPI_TOKEN = "token**" # Asegúrate de que este sea tu token real

async def send_to_wuzapi(chat_id: str, text: str):
    """Envía el mensaje de vuelta a Wuzapi"""
    payload = {
        "chatId": chat_id,
        "text": text
    }
    # En Wuzapi 3.0, el header suele ser 'Token'
    headers = {"Token": WUZAPI_TOKEN}
    
    async with httpx.AsyncClient() as client:
        try:
            # Aumentamos el timeout a 10 segundos por si el contenedor tarda en despertar
            response = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers, timeout=10.0)
            print(f"<- WUZAPI RESPONSE: {response.status_code} | {response.text}", flush=True)
        except Exception as e:
            print(f"!! Error enviando a Wuzapi en puerto 9010: {e}", flush=True)

@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"status": "ignored_non_json"}, status_code=200)

        inner_data = data.get("data", data)
        
        # Mapeo de campos
        message = inner_data.get("message") or inner_data.get("body") or inner_data.get("text")
        sender = inner_data.get("sender") or inner_data.get("from") or inner_data.get("chatId")

        if not message:
            return JSONResponse({"status": "event_ignored"}, status_code=200)

        print(f"\n--- 🟢 WHATSAPP IN ---", flush=True)
        print(f"-> DE: {sender}", flush=True)
        print(f"-> MSG: '{message}'", flush=True)

        reply_text = "Hola, soy Amelia. ¡Te escucho en el puerto 9010!"
        
        # Ejecución asíncrona para no bloquear el recibo del webhook
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}", flush=True)
        print(f"----------------------\n", flush=True)
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {e}", flush=True)
        return JSONResponse({"status": "error", "detail": str(e)}, status_code=200)