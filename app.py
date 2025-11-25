import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import whatsapp_handler

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

@app.route("/", methods=["GET"])
def index():
    return "WhatsApp Expense Bot is running! 🚀"

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Verification endpoint for WhatsApp Cloud API.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return challenge, 200
        else:
            logger.warning("Webhook verification failed. Tokens do not match.")
            return "Forbidden", 403
    return "Bad Request", 400

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """
    Endpoint to receive messages.
    """
    try:
        body = request.get_json()
        logger.info(f"Received webhook: {body}")
        
        whatsapp_handler.process_webhook_event(body)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
