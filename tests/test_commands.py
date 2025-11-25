import pytest
from unittest.mock import patch, MagicMock
import commands
import datetime

@pytest.fixture
def mock_storage():
    with patch('commands.storage') as mock:
        # Setup default config
        mock.get_config.return_value = {
            "presupuesto_mensual": 200000,
            "moneda": "COP",
            "timezone": "UTC"
        }
        mock.get_gastos.return_value = []
        mock.get_pagos.return_value = []
        yield mock

def test_parse_gasto_valid(mock_storage):
    response = commands.parse("gasto 15000 almuerzo")
    assert "✅ Registrado: 15.000 COP" in response
    assert "almuerzo" in response
    mock_storage.save_gasto.assert_called_once()

def test_parse_gasto_invalid_monto(mock_storage):
    response = commands.parse("gasto abc almuerzo")
    assert "❌" in response
    mock_storage.save_gasto.assert_not_called()

def test_parse_gasto_with_category(mock_storage):
    response = commands.parse("gasto 5000 transporte bus")
    assert "✅ Registrado" in response
    # Verify call args
    args = mock_storage.save_gasto.call_args[0][0]
    assert args["categoria"] == "transporte"
    assert args["detalle"] == "bus"

def test_presupuesto_update(mock_storage):
    response = commands.parse("presupuesto 300000")
    assert "actualizado a: 300.000 COP" in response
    mock_storage.update_config.assert_called_with("presupuesto_mensual", 300000)

def test_calculo_mes(mock_storage):
    # Mock expenses
    mock_storage.get_gastos.return_value = [
        {"fecha": datetime.datetime.now().isoformat(), "monto": 50000, "categoria": "x", "detalle": "y"},
        {"fecha": datetime.datetime.now().isoformat(), "monto": 10000, "categoria": "x", "detalle": "z"}
    ]
    
    response = commands.parse("mes")
    assert "60.000 COP" in response # Total
    assert "200.000 COP" in response # Presupuesto
    assert "Te quedan 140.000 COP" in response

def test_pagopendiente_agregar(mock_storage):
    response = commands.parse("pagopendiente agregar internet 80000 2025-12-01")
    assert "✅ Pago agregado: internet" in response
    mock_storage.save_pago.assert_called_once()
    args = mock_storage.save_pago.call_args[0][0]
    assert args["monto"] == 80000
    assert args["vencimiento"] == "2025-12-01"

def test_unknown_command():
    response = commands.parse("saltar 500")
    assert "No entendí" in response
