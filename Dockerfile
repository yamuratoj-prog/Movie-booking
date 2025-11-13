FROM python:3.11-slim

# Установка сертификатов и openssl (необходимо для TLS при подключении к MongoDB Atlas)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates openssl \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Запуск FastAPI
CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
