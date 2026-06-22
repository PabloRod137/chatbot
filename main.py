import os
from fastapi import FastAPI, Request, Response, HTTPException
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

# ... (añade esto al principio, justo después de app = FastAPI(title=APP_NAME))

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (al final del archivo, antes del bloque if __name__ == "__main__":)

@app.post("/chat-web")
async def chat_web(data: dict):
    mensaje = data.get("mensaje")
    # Usamos un ID fijo para usuarios de la web
    phone_number = "web_user" 
    
    # Guardamos y generamos respuesta (igual que en WhatsApp)
    save_message(phone_number, "user", mensaje)
    history = get_history(phone_number, limit=5)
    ai_response = generate_response(mensaje, history)
    save_message(phone_number, "assistant", ai_response)
    
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
        print("✅ WEBHOOK VALIDADO POR META")
        return Response(content=str(challenge), media_type="text/plain")
    
    return Response(content="Error de validación", status_code=403)

# --- BLOQUE PARA RECIBIR Y RESPONDER MENSAJES REALES ---
@app.post("/webhook")
async def receive_message(request: Request):
    try:
        body = await request.json()
        
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
                                print(f"📩 Mensaje recibido de {phone_number}: {content}")
                                
                                # 1. Guardar mensaje del usuario
                                save_message(phone_number, "user", content)
                                
                                # 2. Obtener historial (memoria del bot)
                                history = get_history(phone_number, limit=5)
                                
                                # 3. Generar respuesta con la IA de Gemini
                                print("🧠 Pensando respuesta con Gemini...")
                                ai_response = generate_response(content, history)
                                
                                # 4. Guardar respuesta de la IA
                                save_message(phone_number, "assistant", ai_response)
                                
                                # 5. Enviar mensaje de vuelta por WhatsApp
                                send_whatsapp_message(phone_number, ai_response)
            
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="No es un evento de WhatsApp")
            
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    # Si al final usaste el puerto 8050 en el paso anterior, cámbialo aquí también.
    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=True)