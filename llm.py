import os
import requests
from mock_calendar import check_availability

# Leer prompt del sistema
def get_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Eres el asistente de Escape Santander. Responde de forma breve y amable."

SYSTEM_PROMPT = get_system_prompt()

def generate_response(message: str, history: list) -> str:
    """
    Genera la respuesta usando la API REST directa (sin la librería obsoleta).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Lo siento, el servicio de IA no está configurado."

    # Detectar intención de disponibilidad
    if "disponible" in message.lower() or "reserva" in message.lower() or "fecha" in message.lower() or "hora" in message.lower():
        dispo = check_availability("consulta general", "hoy o en los próximos días")
        message += f"\n\n(Información interna: El sistema de disponibilidad indica: {dispo})"

    # Hablamos directamente con la API REST de Google
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    # Construimos el historial para que la IA tenga memoria
    contents = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
        
    # Añadimos el mensaje actual del cliente
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents
    }

    try:
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extraemos el texto de la respuesta de Google
        return data["candidates"][0]["content"]["parts"][0]["text"]
        
    except requests.exceptions.Timeout as te:
        import traceback
        print(f"[Timeout ERROR] Timeout conectando con Gemini (10s):\n{traceback.format_exc()}")
        return "Lo siento, ha ocurrido un error técnico procesando tu mensaje. Inténtalo de nuevo."
    except requests.exceptions.RequestException as re:
        import traceback
        print(f"[Request ERROR] Error de red conectando con Gemini:\n{traceback.format_exc()}")
        if re.response is not None:
            print(f"Detalles: {re.response.text}")
        return "Lo siento, ha ocurrido un error técnico procesando tu mensaje. Inténtalo de nuevo."
    except Exception as e:
        import traceback
        print(f"[Unexpected ERROR] Error inesperado conectando con Gemini:\n{traceback.format_exc()}")
        return "Lo siento, ha ocurrido un error técnico procesando tu mensaje. Inténtalo de nuevo."