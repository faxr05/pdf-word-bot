FROM python:3.10-slim

# Tizim paketlarini o'rnatishni optimallashtirish
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Avval faqat requirements.txt ni ko'chiramiz (keshdan foydalanish uchun)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keyin qolgan hamma fayllarni ko'chiramiz
COPY . .

CMD ["python", "bot.py"]
