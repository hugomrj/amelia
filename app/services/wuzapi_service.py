import json
import httpx
import asyncio
from urllib.parse import unquote
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

WUZAPI_SEND_URL = "http://localhost:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    """Envía la respuesta a Wuzapi"""
    if not phone: return
    # Extraemos el número limpio (ej: 595994352968)
    clean_phone = phone.split('@')[0].split(':')[0]
    
    payload = {"Phone": clean_phone, "Body": text}
    headers = {"Token": WUZAPI_TOKEN, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers)
            print(f"<- RESPUESTA WUZAPI: {r.status_code}", flush=True)
        except Exception as e:
            print(f"!! ERROR ENVIO: {e}", flush=True)



@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    body = await request.body()
    if not body:
        return JSONResponse({"status": "empty"}, status_code=200)

    print("\n" + "="*40, flush=True)
    print("!!! PROCESANDO MENSAJE WUZAPI !!!", flush=True)
    
    try:
        # 1. Leer como formulario
        form_data = await request.form()
        json_str = form_data.get("jsonData")

        if not json_str:
            print("-> No se encontró 'jsonData' en el formulario.", flush=True)
            return JSONResponse({"status": "no_jsondata"}, status_code=200)

        # 2. Parsear el JSON interno
        data = json.loads(json_str)
        event = data.get("event", {})
        
        # 3. Extraer Mensaje y Remitente (según tu log)
        # El mensaje está en event['Message']['conversation']
        message = event.get("Message", {}).get("conversation")
        # El remitente real está en event['Info']['SenderAlt']
        sender_alt = event.get("Info", {}).get("SenderAlt", "")
        
        print(f"-> DE: {sender_alt}", flush=True)
        print(f"-> MSG: {message}", flush=True)

        if message and sender_alt:
            reply = "¡Hola! Soy Amelia. Tu mensaje ha sido procesado correctamente desde el puerto 4000."
            asyncio.create_task(send_to_wuzapi(sender_alt, reply))
            print("<- RESPUESTA PROGRAMADA", flush=True)
        
        print("="*40 + "\n", flush=True)
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR PROCESANDO: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)