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
        # 1. Leer el cuerpo crudo primero
        raw_body = await request.body()
        
        # Si el cuerpo está vacío, salir sin error
        if not raw_body:
            return JSONResponse({"status": "ignored_empty_body"}, status_code=200)

        # 2. Intentar parsear el JSON
        try:
            data_json = await request.json()
        except Exception:
            return JSONResponse({"status": "invalid_json_ignored"}, status_code=200)

        # 3. Extraer datos (Wuzapi 3 suele usar la llave 'data')
        inner_data = data_json.get("data", data_json)
        
        sender = inner_data.get("from") or inner_data.get("chatId")
        message = inner_data.get("body") or inner_data.get("text")
        
        # Si no hay mensaje (es un evento de 'visto' o 'presencia'), ignorar
        if not message:
            return JSONResponse({"status": "not_a_message_event"}, status_code=200)

        print(f"\n--- 🟢 WUZAPI IN ---")
        print(f"-> FROM: {sender}")
        print(f"-> MSG:  '{message}'")

        # RESPUESTA DE PRUEBA
        reply_text = "Hola, soy Amelia. ¡Conexión exitosa!"
        
        import asyncio
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}")
        print(f"----------------------")
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        # Ya no explotará con "Expecting value"
        print(f"!! ERR WEBHOOK: {e}")
        return JSONResponse({"status": "error_handled"}, status_code=200)