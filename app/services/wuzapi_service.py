import json
import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.ia_service import get_amelia_response

router = APIRouter()

WUZAPI_SEND_URL = "http://127.0.0.1:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    if not phone: return
    
    # Aseguramos el formato JID puro
    clean_number = phone.split('@')[0].split(':')[0]
    jid = f"{clean_number}@s.whatsapp.net"
    
    payload = {"Phone": jid, "Body": text}
    headers = {"Token": WUZAPI_TOKEN, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers)
            print(f"<- RESPUESTA WUZAPI: {r.status_code} | {r.text}", flush=True)
        except Exception as e:
            print(f"!! ERROR ENVIO A WUZAPI: {e}", flush=True)

async def procesar_con_ia_y_responder(sender: str, message: str):
    print(f"-> Amelia pensando respuesta para: {message}...", flush=True)
    respuesta_ia = await get_amelia_response(message)
    await send_to_wuzapi(sender, respuesta_ia)
    print(f"<- AMELIA RESPONDIÓ: {respuesta_ia}", flush=True)

@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    try:
        form_data = await request.form()
        json_str = form_data.get("jsonData")

        if not json_str:
            return JSONResponse({"status": "no_jsondata"}, status_code=200)

        data = json.loads(json_str)
        event = data.get("event", {})
        info = event.get("Info", {})
        
        # 1. Filtro IsFromMe
        if info.get("IsFromMe"):
            return JSONResponse({"status": "ignored_self"})

        # 2. CAPTURA DE MENSAJE MEJORADA (Soporta conversación simple y texto extendido)
        msg_obj = event.get("Message", {})
        message = (
            msg_obj.get("conversation") or 
            msg_obj.get("extendedTextMessage", {}).get("text")
        )
        
        # 3. CAPTURA DE JID MEJORADA
        sender_jid = info.get("RemoteJid") or info.get("Sender")
        
        if message and sender_jid:
            print("\n" + "="*40, flush=True)
            print(f"!!! MENSAJE RECIBIDO DE: {sender_jid} !!!", flush=True)
            print(f"-> MSG: {message}", flush=True)

            asyncio.create_task(procesar_con_ia_y_responder(sender_jid, message))
            
            print("<- PROCESO IA INICIADO", flush=True)
            print("="*40 + "\n", flush=True)
        else:
            # Esto nos dirá en el log si recibimos un evento sin texto (como un check de lectura)
            print(f"DEBUG: Evento ignorado (sin texto o sin JID). EventKeys: {msg_obj.keys()}", flush=True)
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR PROCESANDO: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)