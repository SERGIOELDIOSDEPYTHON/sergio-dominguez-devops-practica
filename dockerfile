# Imagen base: Python 3.12 sobre Debian reducida
FROM python:3.12-slim

WORKDIR /app

# Primero las dependencias, para reutilizar la caché si solo cambia el código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente de la aplicación
COPY src/ .

# Usuario sin privilegios propietario del código
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app \
    && chmod -R u+rwX /app
USER appuser

EXPOSE 8000

# El servidor escucha en 0.0.0.0 para poder publicarse con -p
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
