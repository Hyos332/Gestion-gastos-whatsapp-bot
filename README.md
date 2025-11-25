# WhatsApp Expense Bot 💰

Bot personal para registrar gastos y gestionar finanzas directamente desde WhatsApp. Desarrollado con Python y Flask, utilizando la API oficial de WhatsApp Cloud.

## 🚀 Características

- **Registro rápido**: `gasto 15000 almuerzo`
- **Resúmenes**: Consulta cuánto has gastado hoy, en la semana o en el mes.
- **Control de Presupuesto**: Define un límite mensual y recibe alertas si te excedes.
- **Pagos Pendientes**: Agrega recordatorios para facturas y servicios.
- **Exportación**: Genera un archivo CSV con tus movimientos del mes.
- **Persistencia**: Los datos se guardan localmente en archivos JSON (fácil de respaldar y leer).

## 🛠️ Tecnologías

- Python 3.10+
- Flask
- WhatsApp Cloud API
- Docker & Docker Compose

## 📦 Instalación

### Opción 1: Docker (Recomendada)

1. Clona el repositorio.
2. Crea tu archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
   Edita `.env` con tus credenciales de Meta (Token, Phone ID, etc).

3. Levanta el servicio:
   ```bash
   docker-compose up -d
   ```

El bot estará corriendo en el puerto `5000`.

### Opción 2: Manual

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Configura el `.env`.
3. Ejecuta la aplicación:
   ```bash
   python app.py
   ```

## 🔗 Conexión con WhatsApp

Para que WhatsApp pueda comunicarse con tu bot local, necesitas exponer el puerto 5000 a internet.

1. Usa **ngrok**:
   ```bash
   ngrok http 5000
   ```
2. Copia la URL HTTPS generada.
3. Ve a la consola de desarrolladores de Meta -> WhatsApp -> Configuración.
4. En **Webhook**, coloca tu URL + `/webhook` (ej: `https://tu-url.ngrok.io/webhook`) y tu token de verificación.

## 📝 Ejemplos de Uso

| Comando | Acción |
|---------|--------|
| `gasto 2000 café` | Registra un gasto de 2000 |
| `hoy` | Muestra el total gastado hoy |
| `mes` | Resumen del mes y presupuesto restante |
| `presupuesto 500000` | Establece el presupuesto mensual |
| `pagopendiente agregar luz 50000 2025-11-30` | Agrega un pago pendiente |
| `ayuda` | Muestra todos los comandos disponibles |

---
*Proyecto personal para gestión de gastos.*
