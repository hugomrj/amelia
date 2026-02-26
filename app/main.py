from fastapi import FastAPI
from app.api.webhook import router as webhook_router

app = FastAPI()

# Incluimos el router que acabamos de crear
app.include_router(webhook_router)

@app.get("/")
def read_root():
    return {"message": "API is running"}