import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# --- CONFIGURACIÓN ACTUALIZADA SEGÚN TU CURL ---
WUZAPI_SEND_URL = "http://localhost:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    """Envía el mensaje de vuelta a Wuzapi con el formato Phone/Body"""
    # Limpiamos el sender por si trae el sufijo @s.whatsapp.net
    clean_phone = phone.split('@')[0] if phone else ""
    
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
            print(f"<- WUZAPI RESPONSE: {response.status_code} | {response.text}", flush=True)
        except Exception as e:
            print(f"!! Error enviando a Wuzapi: {e}", flush=True)

@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    try:
        try:
            data = await request.json()
        except Exception:
            return JSONResponse({"status": "ignored_non_json"}, status_code=200)

        # Wuzapi 3 suele envolver en 'data'
        inner_data = data.get("data", data)
        
        # Mapeo de entrada (lo que Amelia recibe)
        message = inner_data.get("message") or inner_data.get("body") or inner_data.get("text")
        sender = inner_data.get("sender") or inner_data.get("from") or inner_data.get("chatId")

        if not message:
            return JSONResponse({"status": "event_ignored"}, status_code=200)

        print(f"\n--- 🟢 WHATSAPP IN ---", flush=True)
        print(f"-> DE: {sender}", flush=True)
        print(f"-> MSG: '{message}'", flush=True)

        # Respuesta de Amelia
        reply_text = "Hola, soy Amelia. ¡Ahora sí te respondo usando el puerto 9010!"
        
        # Disparamos la tarea de envío
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: Intentando enviar respuesta...", flush=True)
        print(f"----------------------\n", flush=True)
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR EN WEBHOOK: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)