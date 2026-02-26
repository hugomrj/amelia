from fastapi import FastAPI
from app.api.webhook import router as webhook_router

app = FastAPI(title="Amelia API")

# Incluimos el router sin prefijo para que escuche en /whatsapp directamente
app.include_router(webhook_router)

@app.get("/")
def read_root():
    return {"status": "online", "service": "API is running"}