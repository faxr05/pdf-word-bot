# Barqaror Bullseye versiyasidan foydalanamiz
FROM python:3.10-slim-bullseye

# Tizim paketlarini yangilangan nomlar bilan o'rnatamiz
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodni nusxalash
COPY . .

CMD ["python", "bot.py"]
