# 🤖 Chatbot de WhatsApp — Escape Room Santander

Sistema de atención automatizada por WhatsApp con Inteligencia Artificial (Gemini 2.5 Flash de Google), construido sobre **FastAPI** (Python). Responde preguntas sobre juegos, precios, horarios y disponibilidad de forma natural, 24 horas al día.

---

## 📋 Índice

1. [¿Cómo funciona el sistema?](#-cómo-funciona-el-sistema)
2. [Archivos del proyecto](#-archivos-del-proyecto)
3. [Requisitos previos](#-requisitos-previos)
4. [Cómo obtener las credenciales (paso a paso)](#-cómo-obtener-las-credenciales-paso-a-paso)
5. [Instalación y puesta en marcha local](#-instalación-y-puesta-en-marcha-local)
6. [Conectar con WhatsApp (Meta)](#-conectar-con-whatsapp-meta)
7. [Despliegue en producción (24/7)](#-despliegue-en-producción-247)
8. [Preguntas frecuentes](#-preguntas-frecuentes)

---

## ⚙️ ¿Cómo funciona el sistema?

El flujo completo cuando un cliente escribe por WhatsApp es el siguiente:

```
Cliente escribe en WhatsApp
        │
        ▼
  API de Meta (WhatsApp)
        │  envía el mensaje a tu servidor
        ▼
  Tu servidor (main.py / FastAPI)
        │  recupera el historial del cliente
        ▼
  Base de datos SQLite (database.py)
        │  devuelve el historial
        ▼
  IA Gemini 1.5 Pro (llm.py)
        │  genera una respuesta inteligente y natural
        ▼
  API de Meta (WhatsApp)
        │  envía la respuesta al cliente
        ▼
  Cliente recibe la respuesta
```

**Datos del negocio integrados en la IA:**
- 📍 Ubicación: Calle Narciso Cuevas 8, Santander
- 📞 Teléfono: 673 79 30 27
- 🎮 Juegos: Contagio, El Asesino, El Ladrón
- 💶 Precios: desde 55€ (2 pers.) hasta 96€ (6 pers.)

---

## 📁 Archivos del proyecto

| Archivo | ¿Para qué sirve? |
|---|---|
| `main.py` | Servidor principal. Recibe los mensajes de WhatsApp y orquesta todo el flujo. |
| `llm.py` | Cerebro del bot. Contiene el prompt del negocio y llama a la IA de Gemini. |
| `database.py` | Guarda y recupera el historial de cada conversación en SQLite. |
| `whatsapp.py` | Se encarga de enviar las respuestas de vuelta al cliente por WhatsApp. |
| `mock_calendar.py` | Simula respuestas de disponibilidad cuando el cliente pregunta por fechas. |
| `.env.example` | Plantilla con todas las variables de entorno que hay que rellenar. |
| `requirements.txt` | Lista de librerías de Python que necesita el proyecto. |
| `Dockerfile` | Instrucciones para empaquetar el proyecto y subirlo a la nube. |

---

## ✅ Requisitos previos

Antes de empezar necesitas tener instalado en tu ordenador:

- **Python 3.9 o superior** → [Descargar desde python.org](https://www.python.org/downloads/)
  - Durante la instalación en Windows, marca la casilla **"Add Python to PATH"**
  - Comprueba que está bien instalado abriendo la terminal y escribiendo: `python --version`

- **Git** (opcional, solo si clonas el proyecto desde un repositorio) → [Descargar desde git-scm.com](https://git-scm.com/)

Para el despliegue en la nube (para que funcione 24/7 sin tu ordenador):
- **Docker Desktop** → [Descargar desde docker.com](https://www.docker.com/products/docker-desktop/) *(opcional)*
- O una cuenta en **Render.com** *(gratuito, recomendado)*

---

## 🔑 Cómo obtener las credenciales (paso a paso)

Necesitas 4 datos clave. Aquí se explica cómo conseguir cada uno:

---

### 1. `GEMINI_API_KEY` — La clave de la Inteligencia Artificial

Es la clave para que el bot pueda "pensar" usando la IA de Google.

**Pasos:**
1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en el botón **"Get API Key"** (arriba a la izquierda)
4. Luego en **"Create API Key"** → **"Create API key in new project"**
5. Copia la clave que aparece (empieza por `AIza...`)
6. Pégala en tu archivo `.env` como: `GEMINI_API_KEY=AIza...`

> ⚠️ **Importante:** Esta clave tiene un plan gratuito generoso. Si el uso crece mucho, Google te avisará y podrás pasarte a un plan de pago.

---

### 2. `WHATSAPP_TOKEN` — El token de acceso de Meta

Es el "carnet de identidad" que Meta te da para poder enviar y recibir mensajes.

**Pasos:**
1. Ve a [Meta for Developers](https://developers.facebook.com/) e inicia sesión
2. Haz clic en **"Mis Apps"** → **"Crear App"**
3. Elige el tipo: **"Empresa"** (o Business)
4. Dale un nombre a tu app (ej. "Chatbot Escape Room")
5. Una vez creada, en el menú lateral busca **"WhatsApp"** → haz clic en **"Configurar"**
6. Ve a **WhatsApp > Configuración de la API**
7. Ahí verás el **Token de acceso temporal** (válido 24h para pruebas)
8. Para producción: sigue los pasos de Meta para generar un **Token permanente** (System User Token)

> 💡 Para pruebas iniciales, el token temporal de 24h es suficiente. Te lo regeneras cuando caduque.

---

### 3. `WHATSAPP_PHONE_ID` — El ID del número de teléfono

Es el identificador interno de Meta para el número desde el que enviará los mensajes el bot.

**Pasos:**
1. En la misma pantalla de **WhatsApp > Configuración de la API**
2. Justo encima del Token verás el campo **"Número de teléfono"** con un desplegable
3. Al lado del nombre del número verás el **ID** (un número largo como `123456789012345`)
4. Cópialo y pégalo en tu `.env` como: `WHATSAPP_PHONE_ID=123456789012345`

---

### 4. `VERIFY_TOKEN` — Tu contraseña secreta del Webhook

Este token **lo inventas tú**. Sirve como contraseña que Meta usará para verificar que el servidor al que se está conectando es realmente tuyo.

**Instrucciones:**
- Invéntate una cadena de texto sin espacios (ej. `escape_sdr_bot_2026`)
- Ponla en tu `.env` como: `VERIFY_TOKEN=escape_sdr_bot_2026`
- Cuando configures el Webhook en Meta (explicado más abajo), escribirás exactamente ese mismo valor

---

## 🚀 Instalación y puesta en marcha local

### Paso 1 — Abrir la terminal en la carpeta del proyecto

En Windows: Abre la carpeta del proyecto en el Explorador de archivos, haz clic en la barra de direcciones, escribe `cmd` y pulsa Enter.

### Paso 2 — Crear un entorno virtual (recomendado)

Esto aísla las librerías del proyecto para que no interfieran con otros proyectos de Python:

```bash
python -m venv venv
```

Activarlo en **Windows**:
```bash
venv\Scripts\activate
```

Activarlo en **Mac/Linux**:
```bash
source venv/bin/activate
```

> ✅ Sabrás que está activo porque verás `(venv)` al inicio de la línea en la terminal.

### Paso 3 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto descargará e instalará automáticamente todas las librerías necesarias (FastAPI, Gemini, etc.). Puede tardar 1-2 minutos.

### Paso 4 — Crear el archivo de configuración

Renombra el archivo `.env.example` a `.env`:

```bash
# En Windows (PowerShell):
copy .env.example .env

# En Mac/Linux:
cp .env.example .env
```

Ahora **abre el archivo `.env`** con cualquier editor de texto (Notepad, VS Code, etc.) y rellena las 4 claves que has obtenido anteriormente:

```env
WHATSAPP_TOKEN=tu_token_real_aqui
WHATSAPP_PHONE_ID=tu_phone_id_real_aqui
VERIFY_TOKEN=escape_sdr_bot_2026
GEMINI_API_KEY=tu_api_key_real_aqui
```

### Paso 5 — Arrancar el servidor

```bash
python main.py
```

Deberías ver en la terminal algo como:
```
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

¡El servidor ya está corriendo en tu ordenador en el puerto 8000! 🎉

---

## 📡 Conectar con WhatsApp (Meta)

Para que Meta pueda enviar mensajes a tu servidor, necesita una **URL pública de internet**. Tu ordenador en casa/oficina tiene una IP privada, por lo que usaremos **Ngrok** para crear un túnel temporal.

### Paso 1 — Instalar y arrancar Ngrok

1. Descarga Ngrok gratis desde [ngrok.com](https://ngrok.com/download) y crea una cuenta gratuita
2. Sigue sus instrucciones para autenticar tu cliente
3. Con el servidor del bot ya corriendo, **abre una segunda ventana de terminal** y ejecuta:

```bash
ngrok http 8000
```

Verás una salida similar a esta:
```
Forwarding   https://1a2b-3c4d-5e6f.ngrok-free.app -> http://localhost:8000
```

Copia esa URL `https://...ngrok-free.app`. La necesitarás en el siguiente paso.

### Paso 2 — Configurar el Webhook en Meta

1. Ve a tu app en [Meta for Developers](https://developers.facebook.com/)
2. En el menú lateral: **WhatsApp > Configuración**
3. Busca el apartado **"Webhook"** y haz clic en **"Editar"**
4. Rellena los campos:
   - **URL de devolución de llamada:** `https://tu-url-de-ngrok.ngrok-free.app/webhook`
   - **Token de verificación:** El mismo valor que pusiste como `VERIFY_TOKEN` en tu `.env`
5. Haz clic en **"Verificar y guardar"**
   - Si todo está bien, Meta enviará una petición a tu servidor y lo verificará automáticamente ✅
6. Después de guardar, haz clic en **"Administrar"** y suscríbete al campo **`messages`**

### Paso 3 — Primera prueba

1. En Meta for Developers, en la sección de **WhatsApp > Configuración de la API**, busca el número de teléfono de prueba
2. Añade tu número personal a la lista de números autorizados para pruebas
3. Envía un WhatsApp desde tu móvil al número de prueba de Meta
4. ¡El bot debería responder en segundos! 🎉

---

## ☁️ Despliegue en producción (24/7)

Para que el bot funcione permanentemente sin depender de tu ordenador, necesitas subirlo a un servidor en la nube. La opción más sencilla y gratuita es **Render**.

### Opción A — Render.com (Recomendado, gratuito)

1. Sube los archivos del proyecto a un repositorio de **GitHub** (privado o público)
2. Ve a [render.com](https://render.com/) y crea una cuenta gratuita
3. Haz clic en **"New"** → **"Web Service"**
4. Conecta tu repositorio de GitHub
5. Configura el servicio:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
6. En el apartado **"Environment Variables"**, añade una a una tus 4 variables (las mismas del `.env`)
7. Haz clic en **"Create Web Service"**
8. Render te dará una URL pública permanente (ej. `https://escape-chatbot.onrender.com`)
9. Usa esa URL para configurar el Webhook en Meta (mismos pasos que antes, pero sin Ngrok)

### Opción B — Docker (para servidores VPS o similares)

Si tienes un servidor propio o un VPS (DigitalOcean, Hetzner, etc.):

**Construir la imagen:**
```bash
docker build -t escape-chatbot .
```

**Ejecutar el contenedor:**
```bash
docker run -d -p 8000:8000 --env-file .env --name escape-chatbot escape-chatbot
```

- `-d` lo ejecuta en segundo plano (modo demonio)
- `-p 8000:8000` mapea el puerto
- `--env-file .env` carga tus variables de entorno

---

## ❓ Preguntas frecuentes

**¿Tiene coste usar este sistema?**
- La IA de Gemini tiene un plan gratuito muy generoso (millones de tokens/mes)
- La API Cloud de WhatsApp de Meta tiene conversaciones gratuitas
- Render.com tiene un tier gratuito (el servidor se "duerme" si no recibe tráfico)
- Para un negocio en producción, los costes serían mínimos (menos de 10€/mes)

**¿El bot mantiene el contexto de la conversación?**
Sí. Cada conversación se guarda en la base de datos SQLite y el bot recuerda los últimos mensajes del cliente para responder de forma coherente.

**¿Qué pasa si el cliente pregunta por juegos que no tenemos?**
El bot está instruido para aclarar amablemente que esos juegos no son suyos y redirigir al catálogo correcto (Contagio, El Asesino, El Ladrón).

**¿Puedo cambiar las respuestas del bot?**
Sí. Toda la personalidad, el conocimiento del negocio y las reglas de comportamiento del bot se definen en el **System Prompt** dentro del archivo `llm.py`. Puedes editarlo libremente.

**¿Qué hago si el token de WhatsApp caduca?**
Los tokens temporales de Meta duran 24 horas. Para producción, debes generar un **System User Token** permanente siguiendo la guía oficial de Meta. La variable en el `.env` es la misma (`WHATSAPP_TOKEN`).

---

*Proyecto desarrollado para Escape Room Santander — escaperoomsantander.es*
