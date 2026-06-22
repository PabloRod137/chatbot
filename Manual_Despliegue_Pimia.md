# 🤖 Manual de Despliegue: Chatbot WhatsApp (Pimia)

Este documento es la guía maestra para replicar y configurar el chatbot en nuevos clientes.

## 📂 1. Estructura de Personalización
El sistema es modular. Para cambiar de cliente, solo tocas:

* **`.env` (El Pasaporte):** Credenciales técnicas y claves de API.
* **`system_prompt.txt` (El Alma):** Identidad del bot, tono y datos del negocio.

---

## 🛠 2. Guía de Configuración Paso a Paso

### FASE A: Recopilación de "Llaves"
1. **Meta for Developers:** `WHATSAPP_TOKEN` y `WHATSAPP_PHONE_ID`.
2. **Google AI Studio:** `GEMINI_API_KEY`.
3. **Seguridad:** `VERIFY_TOKEN` (inventado por ti).

### FASE B: Preparación del Código
1. Crea el archivo `.env` rellenando las llaves.
2. Edita `system_prompt.txt` con la personalidad (Ej: "Eres Max...").
3. Verifica que en `llm.py` usas el modelo `gemini-1.5-flash`.

### FASE C: Lanzamiento en Local
1. Ejecuta: `python main.py`
2. Abre otra terminal y ejecuta: `ngrok http 8000`.
3. Configura el Webhook en Meta con la URL de Ngrok + `/webhook`.

---

## ⚠️ Troubleshooting
* **Puerto ocupado:** Cierra Docker o cambia el puerto en `main.py`.
* **Meta no valida:** Verifica que Ngrok está activo y la URL termina en `/webhook`.
* **Sin respuesta:** Suscríbete al campo `messages` en el panel de Meta.

---
*Manual generado para Pimia Automatitio Lab - Santander, 2026*
