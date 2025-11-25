FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema si fueran necesarias
# RUN apt-get update && apt-get install -y ...

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear directorio de data si no existe (aunque se montará como volumen)
RUN mkdir -p data

EXPOSE 5000

# Usar gunicorn para producción
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
