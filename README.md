
Instalación
Crear y activar entorno virtual:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

Instalar librerías base:
```bash
pip install fastapi uvicorn sqlalchemy mysql-connector-python python-dotenv httpx llama-cpp-python
```

Configuración
Crea un archivo .env en la raíz con lo siguiente:

Fragmento de código
```bash
DB_URL=mysql+mysqlconnector://user:pass@localhost:3306/dbname
MODEL_PATH=path/to/model.gguf
```
Ejecución
```bash
uvicorn app.main:app --reload --port 4000
```