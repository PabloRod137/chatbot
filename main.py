import os
import uuid
import hmac
import hashlib
import json
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from database import init_db, save_message, get_history
from llm import generate_response
from whatsapp import send_whatsapp_message

# Configuramos las variables usando lo que tienes en el .env
APP_NAME = os.getenv("APP_NAME", "Escape Room Santander")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "pimia_secret_santander_2026")

app = FastAPI(title=APP_NAME)

# Obtener y estructurar orígenes permitidos para CORS (evitando "*")
origins_raw = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
if not ALLOWED_ORIGINS:
    # Dominios de confianza por defecto (desarrollo y producción)
    ALLOWED_ORIGINS = ["https://escaperoomsantander.es", "http://localhost:3000", "http://localhost:8050"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constantes para la validación de entrada amigable
MSG_EMPTY_ERROR = "¡Hola! Parece que el mensaje está vacío. ¿En qué puedo ayudarte hoy? 🙂"
MSG_LONG_ERROR = "Tu mensaje es un poco largo, ¿puedes resumirlo en pocas frases? Así puedo ayudarte mejor 🙂"


# ... (al final del archivo, antes del bloque if __name__ == "__main__":)

@app.post("/chat-web")
async def chat_web(request: Request, response: Response, data: dict = None):
    if data is None:
        return PlainTextResponse(content=MSG_EMPTY_ERROR, status_code=400)
        
    mensaje = data.get("mensaje")
    
    # Validación de mensaje vacío, None o solo espacios
    if mensaje is None or not str(mensaje).strip():
        return PlainTextResponse(content=MSG_EMPTY_ERROR, status_code=400)
        
    # Validación de longitud máxima (1000 caracteres)
    if len(str(mensaje)) > 1000:
        return PlainTextResponse(content=MSG_LONG_ERROR, status_code=400)
        
    # Obtener o generar session_id
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="none"
        )
    
    # Guardamos y generamos respuesta (usando session_id)
    save_message(session_id, "user", mensaje)
    history = get_history(session_id, limit=5)
    ai_response = generate_response(mensaje, history)
    save_message(session_id, "assistant", ai_response)
    
    return {"respuesta": ai_response}


@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def read_root():
    return {"status": "online", "message": f"{APP_NAME} funcionando al 100%."}

# --- BLOQUE DE VERIFICACIÓN (Ya validado por Meta) ---
@app.get("/webhook")
def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[Webhook OK] WEBHOOK VALIDADO POR META")
        return Response(content=str(challenge), media_type="text/plain")
    
    return Response(content="Error de validación", status_code=403)

# --- BLOQUE PARA RECIBIR Y RESPONDER MENSAJES REALES ---
@app.post("/webhook")
async def receive_message(request: Request):
    try:
        # Validación de firma de Meta
        app_secret = os.getenv("APP_SECRET", "")
        signature_header = request.headers.get("X-Hub-Signature-256")
        
        # Obtener el cuerpo de la petición en bruto
        raw_body = await request.body()
        
        # Validar firma si falta o es inválida
        if not signature_header or not signature_header.startswith("sha256="):
            print("[Webhook ERROR] Webhook rechazado: Firma de Meta faltante o malformada.")
            raise HTTPException(status_code=403, detail="Firma de webhook faltante o malformada")
        
        expected_signature = signature_header.split("sha256=")[1]
        
        computed_signature = hmac.new(
            app_secret.encode('utf-8'),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(computed_signature, expected_signature):
            print("[Webhook ERROR] Webhook rechazado: Verificación de firma de Meta fallida.")
            raise HTTPException(status_code=403, detail="Verificación de firma de Meta fallida")
        
        # Parsear el cuerpo JSON
        try:
            body = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Cuerpo de petición JSON inválido")
        
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for message in value["messages"]:
                            phone_number = message.get("from")
                            msg_type = message.get("type")
                            
                            if msg_type == "text":
                                content = message.get("text", {}).get("body", "")
                                print(f"[Webhook msg] Mensaje recibido de {phone_number}: {content}")
                                
                                # 1. Guardar mensaje del usuario
                                save_message(phone_number, "user", content)
                                
                                # 2. Obtener historial (memoria del bot)
                                history = get_history(phone_number, limit=5)
                                
                                # 3. Generar respuesta con la IA de Gemini
                                print("[LLM] Pensando respuesta con Gemini...")
                                ai_response = generate_response(content, history)
                                
                                # 4. Guardar respuesta de la IA
                                save_message(phone_number, "assistant", ai_response)
                                
                                # 5. Enviar mensaje de vuelta por WhatsApp
                                send_whatsapp_message(phone_number, ai_response)
            
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="No es un evento de WhatsApp")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        print(f"[Webhook ERROR] Error procesando webhook:\n{traceback.format_exc()}")
        return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    # Si al final usaste el puerto 8050 en el paso anterior, cámbialo aquí también.
    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=True)