import httpx
import json

# Configuración de tu Llama.cpp en Docker
LLAMA_URL = "http://localhost:9020/v1/chat/completions"

async def get_amelia_response(user_message: str):
    """Envía el mensaje a Llama.cpp y devuelve la respuesta de la IA"""
    
    payload = {
        "messages": [
            {"role": "system", "content": "Eres Amelia, una asistente inteligente, amable y concisa."},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    async with httpx.AsyncClient() as client:
        try:
            # Aumentamos el timeout porque la IA puede tardar unos segundos en pensar
            response = await client.post(LLAMA_URL, json=payload, timeout=60.0)
            
            if response.status_code == 200:
                result = response.json()
                # Extraemos el texto de la respuesta (formato estándar OpenAI)
                return result['choices'][0]['message']['content'].strip()
            else:
                return f"Error de IA (Status {response.status_code}): {response.text}"
                
        except Exception as e:
            return f"No pude conectar con mi cerebro (Llama): {str(e)}"