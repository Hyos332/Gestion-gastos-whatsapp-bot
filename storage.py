import json
import os
import fcntl
import shutil
from datetime import datetime
import logging

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
GASTOS_FILE = os.path.join(DATA_DIR, 'gastos.json')
PAGOS_FILE = os.path.join(DATA_DIR, 'pagos.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _ensure_file_exists(filepath, default_content):
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump(default_content, f, indent=2)

def _rotate_file_if_needed(filepath):
    if not os.path.exists(filepath):
        return
    
    try:
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE_BYTES:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(filepath)
            name, ext = os.path.splitext(filename)
            new_name = f"{name}_{timestamp}{ext}"
            new_path = os.path.join(os.path.dirname(filepath), new_name)
            
            # Rename current file
            shutil.move(filepath, new_path)
            logger.info(f"Rotated file {filepath} to {new_path} due to size limit.")
            
            # Create new empty file
            _ensure_file_exists(filepath, [])
    except Exception as e:
        logger.error(f"Error rotating file {filepath}: {e}")

def load_json(filepath, default=None):
    if default is None:
        default = []
    
    _ensure_file_exists(filepath, default)
    
    try:
        with open(filepath, 'r') as f:
            # Shared lock for reading
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
                return data
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except json.JSONDecodeError:
        logger.error(f"JSON corrupted in {filepath}. Recreating empty file.")
        # Backup corrupted file
        if os.path.exists(filepath):
            shutil.copy(filepath, filepath + ".corrupted")
        save_json(filepath, default) # Reset
        return default
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return default

def save_json(filepath, data):
    try:
        # Check rotation before writing if it's the expenses file
        if filepath == GASTOS_FILE:
            _rotate_file_if_needed(filepath)

        with open(filepath, 'w') as f:
            # Exclusive lock for writing
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f, indent=2, ensure_ascii=False)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return True
    except Exception as e:
        logger.error(f"Error writing to {filepath}: {e}")
        return False

# --- Specific Accessors ---

def get_gastos():
    return load_json(GASTOS_FILE, [])

def save_gasto(gasto):
    try:
        with open(GASTOS_FILE, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    content = []
                
                content.append(gasto)
                
                f.seek(0)
                json.dump(content, f, indent=2, ensure_ascii=False)
                f.truncate()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return True
    except FileNotFoundError:
        return save_json(GASTOS_FILE, [gasto])
    except Exception as e:
        logger.error(f"Error saving gasto: {e}")
        return False

def get_pagos():
    return load_json(PAGOS_FILE, [])

def save_pago(pago):
    try:
        with open(PAGOS_FILE, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    content = []
                
                content.append(pago)
                
                f.seek(0)
                json.dump(content, f, indent=2, ensure_ascii=False)
                f.truncate()
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        return True
    except FileNotFoundError:
        return save_json(PAGOS_FILE, [pago])

def get_config():
    default_config = {
        "presupuesto_mensual": 0,
        "moneda": "COP",
        "timezone": "America/Bogota"
    }
    return load_json(CONFIG_FILE, default_config)

def update_config(key, value):
    config = get_config()
    config[key] = value
    save_json(CONFIG_FILE, config)
    return config
