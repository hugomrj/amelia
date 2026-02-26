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
        data = await request.json()
        
        # Extraer datos según estructura típica de Wuzapi
        sender = data.get("chatId") or data.get("from")
        message = data.get("text") or data.get("body")
        
        print(f"\n--- 🟢 WUZAPI IN ---")
        print(f"-> FROM: {sender}")
        print(f"-> MSG:  '{message}'")

        if not message:
            return JSONResponse({"status": "empty_ignored"})

        # RESPUESTA CERRADA (Prueba de conexión)
        reply_text = "Hola, soy Amelia. Recibí tu mensaje correctamente. Próximamente estaré conectada a mi cerebro de IA."
        
        # Enviamos la respuesta asíncrona para no bloquear el webhook
        import asyncio
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}")
        print(f"----------------------")
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        print(f"!! ERR WEBHOOK: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)