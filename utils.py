import uuid
import datetime
import pytz
import dateparser

def get_timezone(tz_name="America/Bogota"):
    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return pytz.UTC

def get_current_time(tz_name="America/Bogota"):
    tz = get_timezone(tz_name)
    return datetime.datetime.now(tz)

def format_currency(amount, currency="COP"):
    """
    Formats amount with thousands separator.
    Example: 15000 -> 15.000 COP
    """
    try:
        amount_int = int(amount)
        formatted = "{:,.0f}".format(amount_int).replace(",", ".")
        return f"{formatted} {currency}"
    except ValueError:
        return f"{amount} {currency}"

def parse_date_input(date_str, tz_name="America/Bogota"):
    """
    Parses natural language dates like 'hoy', 'ayer', '2025-11-12'.
    Returns a datetime object or None.
    """
    settings = {
        'TIMEZONE': tz_name,
        'RETURN_AS_TIMEZONE_AWARE': True
    }
    dt = dateparser.parse(date_str, settings=settings)
    return dt

def generate_id(prefix="g"):
    """
    Generates a unique ID.
    Format: prefix-YYYYMMDD-UUID_SHORT
    """
    now = datetime.datetime.now()
    date_part = now.strftime("%Y%m%d")
    unique_part = str(uuid.uuid4())[:8]
    return f"{prefix}-{date_part}-{unique_part}"

def is_valid_amount(amount_str):
    """
    Checks if the string is a valid positive integer.
    Accepts 15000, 15.000, 15,000.
    """
    clean_amount = str(amount_str).replace(".", "").replace(",", "")
    return clean_amount.isdigit() and int(clean_amount) > 0

def parse_amount(amount_str):
    clean_amount = str(amount_str).replace(".", "").replace(",", "")
    return int(clean_amount)
