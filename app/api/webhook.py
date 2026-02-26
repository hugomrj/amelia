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
        # En FastAPI, es mejor obtener el JSON directamente con un try/except
        try:
            data = await request.json()
        except Exception:
            # Si falla el JSON (cuerpo vacío o mal formado), salimos sin error 500
            return JSONResponse({"status": "ignored_non_json"}, status_code=200)

        # Usamos la misma lógica de extracción de tu código de Starlette
        # Pero añadimos .get() para que no explote si la llave no existe
        
        # Wuzapi 3 suele envolver en 'data', probamos ambas:
        inner_data = data.get("data", data)
        
        # Mapeo de campos que te funcionó (message y sender)
        message = inner_data.get("message") or inner_data.get("body") or inner_data.get("text")
        sender = inner_data.get("sender") or inner_data.get("from") or inner_data.get("chatId")

        print(f"\n--- 🟢 WHATSAPP IN ---")
        print(f"-> FROM: {sender}")
        print(f"-> MSG:  '{message}'")

        if not message:
            return JSONResponse({"status": "empty_msg_ignored"}, status_code=200)

        # Lógica de respuesta de Amelia
        reply_text = "Hola, soy Amelia. ¡Conexión establecida con FastAPI!"
        
        import asyncio
        asyncio.create_task(send_to_wuzapi(sender, reply_text))

        print(f"<- AMELIA: {reply_text}")
        print(f"----------------------")
        
        return JSONResponse({"status": "success"})

    except Exception as e:
        # Esto atrapará cualquier error y lo imprimirá para que lo veamos
        print(f"!! ERR WHATSAPP: {e}")
        return JSONResponse({"error": str(e)}, status_code=200) 