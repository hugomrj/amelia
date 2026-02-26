from fastapi import FastAPI
from app.services.wuzapi_service import router as webhook_router

app = FastAPI(title="Amelia API")

app.include_router(webhook_router)

@app.get("/")
def read_root():
    return {"status": "online", "service": "API is running"}