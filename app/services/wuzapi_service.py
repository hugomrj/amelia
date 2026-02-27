import json
import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.ia_service import get_amelia_response

router = APIRouter()

# Cambiamos localhost por 127.0.0.1 para evitar problemas de resolución de nombres
WUZAPI_SEND_URL = "http://127.0.0.1:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    """Envía la respuesta final a WhatsApp usando el formato JID correcto"""
    if not phone: return
    
    # Limpiamos el ID del dispositivo (:44) si existe y aseguramos el sufijo @s.whatsapp.net
    clean_number = phone.split('@')[0].split(':')[0]
    jid = f"{clean_number}@s.whatsapp.net"
    
    payload = {"Phone": jid, "Body": text}
    headers = {"Token": WUZAPI_TOKEN, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers)
            # Imprimimos el r.text para ver errores de Wuzapi si llegara a fallar
            print(f"<- RESPUESTA WUZAPI: {r.status_code} | {r.text}", flush=True)
        except Exception as e:
            print(f"!! ERROR ENVIO A WUZAPI: {e}", flush=True)

async def procesar_con_ia_y_responder(sender: str, message: str):
    """Tarea asíncrona: Pregunta a Llama y envía el resultado"""
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
        
        # --- FILTROS DE SEGURIDAD ---
        # 1. Ignorar si el mensaje es enviado por nosotros (evita bucle infinito)
        if info.get("IsFromMe"):
            return JSONResponse({"status": "ignored_self"})

        # 2. Extraer Mensaje (solo si es tipo conversación de texto)
        message = event.get("Message", {}).get("conversation")
        
        # 3. Usar RemoteJid para identificar al cliente
        sender_jid = info.get("RemoteJid")
        
        if message and sender_jid:
            print("\n" + "="*40, flush=True)
            print(f"!!! MENSAJE RECIBIDO DE: {sender_jid} !!!", flush=True)
            print(f"-> MSG: {message}", flush=True)

            # Lanzamos el proceso de la IA en segundo plano
            asyncio.create_task(procesar_con_ia_y_responder(sender_jid, message))
            
            print("<- PROCESO IA INICIADO", flush=True)
            print("="*40 + "\n", flush=True)
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR PROCESANDO: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)