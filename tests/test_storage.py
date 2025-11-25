import os
import json
import pytest
from unittest.mock import patch, MagicMock
import storage

# Mock the data directory for tests
@pytest.fixture
def mock_data_dir(tmp_path):
    with patch('storage.DATA_DIR', str(tmp_path)):
        with patch('storage.GASTOS_FILE', str(tmp_path / 'gastos.json')):
            with patch('storage.PAGOS_FILE', str(tmp_path / 'pagos.json')):
                with patch('storage.CONFIG_FILE', str(tmp_path / 'config.json')):
                    yield tmp_path

def test_save_and_get_gasto(mock_data_dir):
    gasto = {
        "id": "test-1",
        "monto": 1000,
        "categoria": "test",
        "detalle": "prueba",
        "fecha": "2025-01-01T10:00:00"
    }
    assert storage.save_gasto(gasto) is True
    
    gastos = storage.get_gastos()
    assert len(gastos) == 1
    assert gastos[0]["id"] == "test-1"

def test_save_and_get_pago(mock_data_dir):
    pago = {
        "id": "p-1",
        "nombre": "luz",
        "monto": 50000,
        "vencimiento": "2025-12-31",
        "pagado": False
    }
    assert storage.save_pago(pago) is True
    
    pagos = storage.get_pagos()
    assert len(pagos) == 1
    assert pagos[0]["nombre"] == "luz"

def test_config_update(mock_data_dir):
    # Initial read should return default
    config = storage.get_config()
    assert config["presupuesto_mensual"] == 0
    
    # Update
    storage.update_config("presupuesto_mensual", 500000)
    
    # Read again
    config = storage.get_config()
    assert config["presupuesto_mensual"] == 500000

def test_file_rotation(mock_data_dir):
    # Mock os.path.getsize to return a large value
    gasto_file = mock_data_dir / 'gastos.json'
    
    # Create initial file
    storage.save_gasto({"id": "1"})
    assert os.path.exists(gasto_file)
    
    with patch('os.path.getsize', return_value=11 * 1024 * 1024): # 11 MB
        # Trigger save, which should trigger rotation
        storage.save_gasto({"id": "2"})
        
        # Check if rotation happened (new file is empty-ish, old file renamed)
        # Since we can't easily predict the timestamp in the filename, we check if there are 2 files
        files = list(mock_data_dir.glob("gastos_*.json"))
        assert len(files) == 1 # The rotated file
        
        # The current file should be reset (contains only the new item "2" or empty + new item)
        # In our implementation: rotate -> create empty -> append new.
        # So current file should have 1 item ("2")
        current_content = storage.get_gastos()
        assert len(current_content) == 1
        assert current_content[0]["id"] == "2"
