from fastapi import APIRouter, Request # <--- Cambiado a APIRouter
from fastapi.responses import JSONResponse
import httpx
import asyncio

router = APIRouter() # <--- Esto es lo que main.py está buscando

WUZAPI_SEND_URL = "http://localhost:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    clean_phone = phone.split('@')[0] if phone else ""
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
    # 1. Verificamos si hay contenido antes de intentar leerlo
    body = await request.body()
    if not body:
        return JSONResponse({"status": "ignored_empty_body"}, status_code=200)

    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
    print("!!! RECIBIENDO PETICION EN /WHATSAPP !!!", flush=True)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
    
    try:
        # 2. Convertimos el body que ya leímos a JSON
        import json
        try:
            data = json.loads(body)
        except Exception:
            print("-> Petición no es JSON válido, ignorando.", flush=True)
            return JSONResponse({"status": "invalid_json"}, status_code=200)

        print(f"DEBUG DATA: {data}", flush=True)
        
        inner = data.get("data", data)
        message = inner.get("message") or inner.get("body") or inner.get("Body") or inner.get("text")
        sender = inner.get("sender") or inner.get("from") or inner.get("Phone") or inner.get("chatId")

        if message:
            print(f"-> MENSAJE: {message} | DE: {sender}", flush=True)
            asyncio.create_task(send_to_wuzapi(sender, "¡Amelia en linea! Recibí tu mensaje."))
        else:
            print("-> Evento sin texto (visto/presencia) ignorado.", flush=True)
        
        return {"status": "ok"}

    except Exception as e:
        print(f"❌ ERROR INTERNO: {e}", flush=True)
        return JSONResponse({"status": "error_handled"}, status_code=200)