import datetime
import logging
import csv
import io
import os
from dateutil.relativedelta import relativedelta
import utils
import storage

logger = logging.getLogger(__name__)

def handle_gasto(args):
    """
    gasto <monto> <detalle>
    gasto <monto> <categoria> <detalle>
    """
    if not args:
        return "❌ Formato incorrecto. Usa: gasto <monto> <detalle>"

    try:
        monto_str = args[0]
        if not utils.is_valid_amount(monto_str):
            return "❌ El monto debe ser un número positivo."
        
        monto = utils.parse_amount(monto_str)
        
        remaining_args = args[1:]
        if not remaining_args:
             return "❌ Falta el detalle del gasto."

        categoria = "varios"
        detalle = ""

        if len(remaining_args) >= 2:
            categoria = remaining_args[0]
            detalle = " ".join(remaining_args[1:])
        else:
            detalle = remaining_args[0]

        config = storage.get_config()
        tz = utils.get_timezone(config.get("timezone", "America/Bogota"))
        now = datetime.datetime.now(tz)
        
        gasto = {
            "id": utils.generate_id("g"),
            "fecha": now.isoformat(),
            "monto": monto,
            "categoria": categoria,
            "detalle": detalle
        }
        
        storage.save_gasto(gasto)
        
        formatted_monto = utils.format_currency(monto, config.get("moneda", "COP"))
        date_str = now.strftime("%d %b %Y %H:%M")
        
        return f"✅ Registrado: {formatted_monto} — {detalle} ({date_str})."

    except Exception as e:
        logger.error(f"Error processing gasto: {e}")
        return "❌ Error interno al registrar el gasto."

def handle_hoy():
    config = storage.get_config()
    tz = utils.get_timezone(config.get("timezone", "America/Bogota"))
    now = datetime.datetime.now(tz)
    today_str = now.strftime("%Y-%m-%d")
    
    gastos = storage.get_gastos()
    total = 0
    items = []
    
    for g in gastos:
        # Parse stored date
        g_date = datetime.datetime.fromisoformat(g["fecha"])
        if g_date.strftime("%Y-%m-%d") == today_str:
            total += g["monto"]
            items.append(g)
            
    formatted_total = utils.format_currency(total, config.get("moneda", "COP"))
    
    if not items:
        return f"Hoy ({today_str}) no has gastado nada."
        
    return f"Hoy has gastado: {formatted_total}."

def handle_mes():
    config = storage.get_config()
    tz = utils.get_timezone(config.get("timezone", "America/Bogota"))
    now = datetime.datetime.now(tz)
    current_month = now.strftime("%Y-%m")
    
    gastos = storage.get_gastos()
    total = 0
    
    for g in gastos:
        g_date = datetime.datetime.fromisoformat(g["fecha"])
        if g_date.strftime("%Y-%m") == current_month:
            total += g["monto"]
            
    presupuesto = config.get("presupuesto_mensual", 0)
    moneda = config.get("moneda", "COP")
    
    formatted_total = utils.format_currency(total, moneda)
    formatted_presupuesto = utils.format_currency(presupuesto, moneda)
    
    msg = f"En {now.strftime('%B (%Y)')} has gastado: {formatted_total}. Presupuesto: {formatted_presupuesto}."
    
    if total > presupuesto:
        diff = total - presupuesto
        msg += f" Te has pasado {utils.format_currency(diff, moneda)}."
    else:
        left = presupuesto - total
        msg += f" Te quedan {utils.format_currency(left, moneda)}."
        
    return msg

def handle_semana():
    config = storage.get_config()
    tz = utils.get_timezone(config.get("timezone", "America/Bogota"))
    now = datetime.datetime.now(tz)
    # Start of week (Monday)
    start_of_week = now - datetime.timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    gastos = storage.get_gastos()
    total = 0
    
    for g in gastos:
        g_date = datetime.datetime.fromisoformat(g["fecha"])
        if g_date >= start_of_week:
            total += g["monto"]
            
    formatted_total = utils.format_currency(total, config.get("moneda", "COP"))
    return f"Esta semana (desde {start_of_week.strftime('%d/%m')}) has gastado: {formatted_total}."

def handle_presupuesto(args):
    if not args:
        return "❌ Indica el monto. Ej: presupuesto 200000"
    
    monto_str = args[0]
    if not utils.is_valid_amount(monto_str):
        return "❌ Monto inválido."
        
    monto = utils.parse_amount(monto_str)
    storage.update_config("presupuesto_mensual", monto)
    
    moneda = storage.get_config().get("moneda", "COP")
    return f"✅ Presupuesto mensual actualizado a: {utils.format_currency(monto, moneda)}"

def handle_cuanto_me_queda():
    # Reuse logic from handle_mes but focused on remaining
    config = storage.get_config()
    tz = utils.get_timezone(config.get("timezone", "America/Bogota"))
    now = datetime.datetime.now(tz)
    current_month = now.strftime("%Y-%m")
    
    gastos = storage.get_gastos()
    total = 0
    for g in gastos:
        g_date = datetime.datetime.fromisoformat(g["fecha"])
        if g_date.strftime("%Y-%m") == current_month:
            total += g["monto"]
            
    presupuesto = config.get("presupuesto_mensual", 0)
    remaining = presupuesto - total
    moneda = config.get("moneda", "COP")
    
    if remaining < 0:
        return f"⚠️ No te queda nada. Te has excedido en {utils.format_currency(abs(remaining), moneda)}."
    
    return f"Te quedan: {utils.format_currency(remaining, moneda)} del presupuesto de {utils.format_currency(presupuesto, moneda)}."

def handle_pagopendiente(args):
    if not args:
        return "Usa: pagopendiente agregar ... o pagopendiente listar"
    
    subcmd = args[0].lower()
    
    if subcmd == "agregar":
        if len(args) < 4:
            return "❌ Formato: pagopendiente agregar <nombre> <monto> <YYYY-MM-DD>"
            
        date_str = args[-1]
        monto_str = args[-2]
        nombre_parts = args[1:-2]
        nombre = " ".join(nombre_parts)
        
        if not utils.is_valid_amount(monto_str):
            return "❌ Monto inválido."
        
        dt = utils.parse_date_input(date_str)
        if not dt:
            return "❌ Fecha inválida."
            
        pago = {
            "id": utils.generate_id("p"),
            "nombre": nombre,
            "monto": utils.parse_amount(monto_str),
            "vencimiento": dt.strftime("%Y-%m-%d"),
            "pagado": False
        }
        storage.save_pago(pago)
        
        moneda = storage.get_config().get("moneda", "COP")
        return f"✅ Pago agregado: {nombre} - {utils.format_currency(pago['monto'], moneda)} - vence {pago['vencimiento']}."

    elif subcmd == "listar":
        pagos = storage.get_pagos()
        pendientes = [p for p in pagos if not p.get("pagado")]
        if not pendientes:
            return "No tienes pagos pendientes."
            
        # Sort by date
        pendientes.sort(key=lambda x: x["vencimiento"])
        
        msg = "📅 Pagos pendientes:\n"
        moneda = storage.get_config().get("moneda", "COP")
        for p in pendientes:
            msg += f"- {p['nombre']}: {utils.format_currency(p['monto'], moneda)} ({p['vencimiento']})\n"
        return msg.strip()
        
    else:
        return "Subcomando desconocido. Usa 'agregar' o 'listar'."

def handle_resumen():
    # Combine hoy, semana, mes, pagos proximos
    hoy_msg = handle_hoy()
    # We want compact, so let's strip prefixes maybe?
    # "Hoy has gastado: X" -> "Hoy: X"
    
    # Let's just call the functions and concatenate
    semana_msg = handle_semana()
    mes_msg = handle_mes()
    
    # Pagos proximos (next 7 days)
    pagos = storage.get_pagos()
    pendientes = [p for p in pagos if not p.get("pagado")]
    pendientes.sort(key=lambda x: x["vencimiento"])
    
    proximos_msg = ""
    if pendientes:
        next_pago = pendientes[0]
        moneda = storage.get_config().get("moneda", "COP")
        proximos_msg = f"\nPróximo pago: {next_pago['nombre']} ({utils.format_currency(next_pago['monto'], moneda)}) el {next_pago['vencimiento']}."

    return f"📊 Resumen:\n{hoy_msg}\n{semana_msg}\n{mes_msg}{proximos_msg}"

def handle_exportar(args):
    # exportar mes <YYYY-MM>
    if len(args) < 2 or args[0] != "mes":
        return "❌ Formato: exportar mes YYYY-MM"
    
    mes_str = args[1] 
    # Validate format YYYY-MM
    try:
        datetime.datetime.strptime(mes_str, "%Y-%m")
    except ValueError:
        return "❌ Formato de fecha inválido. Usa YYYY-MM (ej: 2025-11)."
        
    gastos = storage.get_gastos()
    filtered = [g for g in gastos if g["fecha"].startswith(mes_str)]
    
    if not filtered:
        return f"No hay gastos para {mes_str}."
        
    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["fecha", "monto", "categoria", "detalle", "id"])
    
    for g in filtered:
        writer.writerow([g["fecha"], g["monto"], g["categoria"], g["detalle"], g["id"]])
        
    csv_content = output.getvalue()
    
    filename = f"export_{mes_str}.csv"
    filepath = os.path.join("data", filename)
    with open(filepath, "w") as f:
        f.write(csv_content)
        
    return f"✅ Archivo exportado: {filepath}\n(Nota: Para enviar el archivo real por WhatsApp se requiere subirlo a la API de Medios, lo cual requiere pasos adicionales. Por ahora se ha guardado localmente)."

def handle_ayuda():
    return """🤖 Comandos disponibles:

- *gasto <monto> <detalle>*: Registrar gasto.
- *gasto <monto> <cat> <detalle>*: Registrar con categoría.
- *hoy* / *gastos hoy*: Resumen diario.
- *semana*: Resumen semanal.
- *mes*: Resumen mensual y estado del presupuesto.
- *presupuesto <monto>*: Definir presupuesto mensual.
- *cuanto me queda*: Ver saldo restante.
- *pagopendiente agregar <nombre> <monto> <fecha>*: Agendar pago.
- *pagopendiente listar*: Ver pagos pendientes.
- *resumen*: Reporte general.
- *exportar mes <YYYY-MM>*: Exportar a CSV.
"""

def parse(message_text):
    text = message_text.strip()
    if not text:
        return "Mensaje vacío."
        
    parts = text.split()
    cmd = parts[0].lower()
    args = parts[1:]
    
    if cmd == "gasto":
        return handle_gasto(args)
    elif cmd in ["hoy", "gastos"] and (len(parts) == 1 or parts[1].lower() == "hoy"):
        return handle_hoy()
    elif cmd in ["mes", "gastos"] and (len(parts) > 1 and parts[1].lower() == "mes") or cmd == "mes":
        return handle_mes()
    elif cmd in ["semana", "gastos"] and (len(parts) > 1 and parts[1].lower() == "semana") or cmd == "semana":
        return handle_semana()
    elif cmd == "presupuesto":
        return handle_presupuesto(args)
    elif cmd == "cuanto" and len(parts) >= 3 and parts[1] == "me" and parts[2] == "queda":
        return handle_cuanto_me_queda()
    elif cmd == "pagopendiente":
        return handle_pagopendiente(args)
    elif cmd == "resumen":
        return handle_resumen()
    elif cmd == "exportar":
        return handle_exportar(args)
    elif cmd == "ayuda":
        return handle_ayuda()
    else:
        return "❓ No entendí. Envía 'ayuda' para ver comandos."
