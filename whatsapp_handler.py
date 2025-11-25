import os
import requests
import logging
import time
import json
from dotenv import load_dotenv
import commands

load_dotenv()

logger = logging.getLogger(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
BASE_URL = os.getenv("BASE_URL", "https://graph.facebook.com/v17.0")

def send_message(to_number, text_body):
    """
    Sends a text message to the specified number using WhatsApp Cloud API.
    Retries 3 times with exponential backoff.
    """
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text_body}
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed to send message: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt) # 1s, 2s, 4s
            else:
                logger.error(f"Failed to send message after {max_retries} attempts.")
                return False

def process_webhook_event(body):
    """
    Processes the incoming webhook JSON from WhatsApp.
    """
    try:
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return # No messages (could be a status update)

        message = messages[0]
        from_number = message.get("from")
        msg_type = message.get("type")
        
        if msg_type == "text":
            text_body = message.get("text", {}).get("body", "")
            logger.info(f"Received message from {from_number}: {text_body}")
            
            # Process command
            response_text = commands.parse(text_body)
            
            # Send response
            success = send_message(from_number, response_text)
            if not success:
                logger.error(f"Could not send response to {from_number}")
        else:
            logger.info(f"Received non-text message type: {msg_type}")
            send_message(from_number, "⚠️ Por ahora solo entiendo mensajes de texto.")

    except (IndexError, KeyError) as e:
        logger.error(f"Error parsing webhook body: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
