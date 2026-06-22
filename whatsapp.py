import os
import requests
import logging

logger = logging.getLogger(__name__)

# La API versión puede variar, v18.0 o superior (Consulta en Meta For Developers)
API_VERSION = "v18.0" 

def send_whatsapp_message(to_phone: str, message: str):
    # 👇 AQUÍ SE LEEN TUS CREDENCIALES DE WHATSAPP:
    # Se leen aquí para asegurar que el archivo .env ya está cargado por FastAPI
    WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")

    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.error("Faltan las credenciales de WhatsApp en el .env")
        return False
        
    url = f"https://graph.facebook.com/{API_VERSION}/{WHATSAPP_PHONE_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Mensaje enviado con éxito a {to_phone}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error enviando mensaje a WhatsApp: {e}")
        if e.response is not None:
            logger.error(f"Detalles: {e.response.text}")
        return False
