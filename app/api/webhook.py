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
        # 1. Protección contra cuerpos vacíos
        raw_body = await request.body()
        if not raw_body:
            return JSONResponse({"status": "ignored_empty_body"}, status_code=200)

        # 2. Parsear JSON
        data = await request.json()
        
        # 3. USAR LAS ETIQUETAS QUE TE FUNCIONAN EN EL OTRO SERVIDOR
        # Si Wuzapi 3.0 los mete en 'data', lo extraemos, si no, del raíz
        inner_data = data.get("data", data)
        
        message = inner_data.get("message") or inner_data.get("body")
        sender = inner_data.get("sender") or inner_data.get("from")
        
        # Log para ver qué llega exactamente (Ayuda a depurar)
        print(f"\n--- 🟢 WHATSAPP IN ---")
        print(f"-> FROM: {sender}")
        print(f"-> MSG:  '{message}'")

        if not message:
            return JSONResponse({"status": "empty_ignored"}, status_code=200)

        # 4. Lógica de respuesta (Prueba de conexión)
        reply_text = "Hola, soy Amelia. Conexión establecida con éxito."
        
        import asyncio
        # Asegúrate de que la función 'send_to_wuzapi' use el token correcto
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}")
        print(f"----------------------")
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"!! ERR WEBHOOK: {e}")
        return JSONResponse({"error": str(e)}, status_code=200)