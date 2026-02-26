import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

# Configuración de salida para Wuzapi
# Cambia localhost por la IP de tu server si Wuzapi está en otro contenedor/maquina
WUZAPI_SEND_URL = "http://localhost:8080/api/sendText" 

async def send_to_wuzapi(chat_id: str, text: str):
    """Envía el mensaje de vuelta a Wuzapi"""
    payload = {
        "chatId": chat_id,
        "text": text
    }
    async with httpx.AsyncClient() as client:
        try:
            # Enviamos la respuesta a Wuzapi
            await client.post(WUZAPI_SEND_URL, json=payload)
        except Exception as e:
            print(f"!! Error enviando a Wuzapi: {e}")




@router.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    try:
        # 1. Validar que el body no venga vacío (evita el error line 1 column 1)
        body = await request.body()
        if not body:
            return JSONResponse({"status": "ignored_empty_body"})
            
        data_json = await request.json()
        
        # 2. Wuzapi 3.0 mete la info dentro de la llave 'data'
        # Si 'data' no existe, usamos el dict principal por si acaso
        inner_data = data_json.get("data", data_json)
        
        # 3. Extraer remitente y mensaje con los nombres de campo de Wuzapi 3
        sender = inner_data.get("from") or inner_data.get("chatId")
        message = inner_data.get("body") or inner_data.get("text")
        
        print(f"\n--- 🟢 WUZAPI IN ---")
        print(f"-> FROM: {sender}")
        print(f"-> MSG:  '{message}'")

        if not message:
            return JSONResponse({"status": "event_received_no_text"})

        # RESPUESTA CERRADA
        reply_text = "Hola, soy Amelia. Recibí tu mensaje correctamente."
        
        import asyncio
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}")
        print(f"----------------------")
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        # Esto atrapará el error de "Expecting value" y te dirá qué pasó
        print(f"!! ERR WEBHOOK: {e}")
        return JSONResponse({"error": "check_logs"}, status_code=200) # Devolvemos 200 para que Wuzapi no reintente eternamente