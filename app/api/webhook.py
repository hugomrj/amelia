from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio

app = FastAPI()

# --- REPETIMOS LA CONFIGURACIÓN AQUÍ PARA NO FALLAR ---
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

@app.post("/whatsapp")
async def whatsapp_endpoint(request: Request):
    # LOG DE ENTRADA ABSOLUTO
    print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
    print("!!! RECIBIENDO PETICION EN /WHATSAPP !!!", flush=True)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
    
    try:
        data = await request.json()
        print(f"DEBUG DATA: {data}", flush=True)
        
        inner = data.get("data", data)
        message = inner.get("message") or inner.get("body") or inner.get("Body") or inner.get("text")
        sender = inner.get("sender") or inner.get("from") or inner.get("Phone") or inner.get("chatId")

        if message:
            print(f"-> MENSAJE: {message} | DE: {sender}", flush=True)
            asyncio.create_task(send_to_wuzapi(sender, "¡Amelia en linea!"))
        
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ ERROR: {e}", flush=True)
        return {"status": "error"}

@app.get("/")
def read_root():
    return {"status": "running"}