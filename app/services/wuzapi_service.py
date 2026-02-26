import json
import httpx
import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
# Importamos el servicio que crearemos a continuación
from app.services.ia_service import get_amelia_response

router = APIRouter()

WUZAPI_SEND_URL = "http://localhost:9010/chat/send/text" 
WUZAPI_TOKEN = "token**" 

async def send_to_wuzapi(phone: str, text: str):
    """Envía la respuesta final a WhatsApp"""
    if not phone: return
    clean_phone = phone.split('@')[0].split(':')[0]
    
    payload = {"Phone": clean_phone, "Body": text}
    headers = {"Token": WUZAPI_TOKEN, "Content-Type": "application/json"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(WUZAPI_SEND_URL, json=payload, headers=headers)
            print(f"<- RESPUESTA WUZAPI: {r.status_code}", flush=True)
        except Exception as e:
            print(f"!! ERROR ENVIO A WUZAPI: {e}", flush=True)

async def procesar_con_ia_y_responder(sender: str, message: str):
    """Tarea asíncrona: Pregunta a Llama y envía el resultado"""
    print(f"-> Amelia pensando respuesta para: {message}...", flush=True)
    
    # Llamada al servicio de Llama.cpp (puerto 9020)
    respuesta_ia = await get_amelia_response(message)
    
    # Enviar la respuesta generada a Wuzapi
    await send_to_wuzapi(sender, respuesta_ia)
    print(f"<- AMELIA RESPONDIÓ: {respuesta_ia}", flush=True)

@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    body = await request.body()
    if not body:
        return JSONResponse({"status": "empty"}, status_code=200)

    print("\n" + "="*40, flush=True)
    print("!!! PROCESANDO MENSAJE WUZAPI !!!", flush=True)
    
    try:
        form_data = await request.form()
        json_str = form_data.get("jsonData")

        if not json_str:
            return JSONResponse({"status": "no_jsondata"}, status_code=200)

        data = json.loads(json_str)
        event = data.get("event", {})
        
        # Extraer Mensaje y Remitente
        message = event.get("Message", {}).get("conversation")
        sender_alt = event.get("Info", {}).get("SenderAlt", "")
        
        if message and sender_alt:
            print(f"-> DE: {sender_alt}", flush=True)
            print(f"-> MSG: {message}", flush=True)

            # Lanzamos el proceso de la IA en segundo plano
            asyncio.create_task(procesar_con_ia_y_responder(sender_alt, message))
            print("<- PROCESO IA INICIADO", flush=True)
        
        print("="*40 + "\n", flush=True)
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"❌ ERROR PROCESANDO: {e}", flush=True)
        return JSONResponse({"status": "error"}, status_code=200)