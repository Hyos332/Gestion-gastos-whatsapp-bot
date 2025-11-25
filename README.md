# 🤖 WhatsApp Expense Bot

Bot de WhatsApp para registro y gestión de gastos personales, construido con Python, Flask y la WhatsApp Cloud API. Almacena datos en archivos JSON locales.

## 📋 Características

- **Registro de gastos**: `gasto 15000 almuerzo`
- **Resúmenes**: Diario (`hoy`), Semanal (`semana`), Mensual (`mes`).
- **Presupuesto**: Control de presupuesto mensual y alertas de exceso.
- **Pagos Pendientes**: Recordatorios de pagos futuros.
- **Exportación**: Generación de CSV mensual.
- **Almacenamiento Local**: JSON con rotación de logs y locking básico.

## 🛠 Tech Stack

- **Lenguaje**: Python 3.10+
- **Servidor Web**: Flask
- **API**: WhatsApp Cloud API (Meta)
- **Almacenamiento**: JSON (sin base de datos SQL)
- **Herramientas**: ngrok (túnel local), pytest (pruebas), python-dotenv (configuración)

## 🚀 Instalación y Configuración

### 1. Prerrequisitos
- Python 3.10 o superior instalado.
- Cuenta de desarrollador en Meta (Facebook).
- Una app creada en el panel de Meta con el producto "WhatsApp" habilitado.

### 2. Clonar y preparar entorno
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crea un archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```
Edita `.env` con tus credenciales:
- `WHATSAPP_TOKEN`: Token de acceso temporal o permanente (System User).
- `PHONE_NUMBER_ID`: ID del número de teléfono de prueba o real.
- `VERIFY_TOKEN`: Una cadena secreta que tú inventas (ej. `mi_secreto_seguro`).

### 4. Ejecutar el servidor
```bash
python app.py
```
El servidor correrá en `http://localhost:5000`.

### 5. Exponer con ngrok
Para que WhatsApp pueda enviar mensajes a tu servidor local, necesitas un túnel HTTPS.
```bash
ngrok http 5000
```
Copia la URL HTTPS generada (ej. `https://a1b2c3d4.ngrok.io`).

### 6. Configurar Webhook en Meta
1. Ve a la consola de desarrolladores de Meta -> Tu App -> WhatsApp -> Configuración.
2. En **URL de devolución de llamada**, pega tu URL de ngrok + `/webhook` (ej. `https://a1b2c3d4.ngrok.io/webhook`).
3. En **Token de verificación**, pega el `VERIFY_TOKEN` que pusiste en tu `.env`.
4. Haz clic en "Verificar y guardar".
5. Suscríbete al evento `messages`.

## 🧪 Pruebas

### Ejecutar tests automatizados
```bash
pytest
```
Esto ejecutará las pruebas unitarias para `storage` y `commands`.

### Prueba manual con cURL
Puedes simular un mensaje de WhatsApp enviando un POST a tu webhook local:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "1234567890",
          "phone_number_id": "1234567890"
        },
        "contacts": [{
          "profile": {
            "name": "NAME"
          },
          "wa_id": "PHONE_NUMBER"
        }],
        "messages": [{
          "from": "573001234567",
          "id": "wamid.HBgM...",
          "timestamp": "1600000000",
          "text": {
            "body": "gasto 15000 almuerzo"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}' http://localhost:5000/webhook
```

## 📚 Documentación de API Webhook

### Endpoint: `POST /webhook`
Recibe notificaciones de mensajes entrantes.

**Payload simplificado:**
```json
{
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "from": "573001234567",
          "text": { "body": "mensaje del usuario" },
          "type": "text"
        }]
      }
    }]
  }]
}
```

### Endpoint: `GET /webhook`
Usado por Meta para verificar la URL. Requiere parámetros `hub.mode`, `hub.verify_token`, `hub.challenge`.

## 🔒 Seguridad y Privacidad

- **Tokens**: Nunca subas el archivo `.env` al repositorio.
- **Datos**: Los archivos JSON en `data/` contienen información financiera. Asegúrate de que esta carpeta no sea accesible públicamente si despliegas en un servidor real.
- **Validación**: El bot valida que los montos sean positivos y maneja errores de formato.

## 📂 Estructura del Proyecto

- `app.py`: Servidor Flask.
- `whatsapp_handler.py`: Lógica de comunicación con API de WhatsApp.
- `commands.py`: Lógica de negocio de cada comando.
- `storage.py`: Manejo de archivos JSON (lectura/escritura/locking).
- `utils.py`: Funciones auxiliares (fechas, monedas).
- `data/`: Almacenamiento de datos.
- `tests/`: Tests unitarios.

## ⚠️ Modo sin WhatsApp Cloud API
Si no puedes usar la API oficial, este código base puede adaptarse para usar librerías como `pywhatkit` (solo envío) o `selenium` (envío/recepción), pero requiere modificar `whatsapp_handler.py` para no depender de webhooks y usar un loop de polling o automatización de navegador, lo cual es menos estable y no recomendado para producción.
