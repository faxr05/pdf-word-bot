import asyncio
import os
from dotenv import load_dotenv
import logging
import sys
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import FSInputFile
from pdf2docx import Converter
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# 1. Loggingni sozlash (Faqat bir marta)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 2. Tokenni olish
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("BOT_TOKEN topilmadi! Render Environment Variables qismini tekshiring.")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.document)
async def handle_pdf(message: types.Message):
    # Faqat PDF fayllarni tekshirish
    if not message.document.file_name.lower().endswith('.pdf'):
        return await message.answer("Iltimos, faqat PDF formatidagi fayl yuboring 📄")

    file_id = message.document.file_id
    file_name = message.document.file_name
    # Word fayl nomi (asl nomi bilan bir xil qilish)
    doc_name = file_name.rsplit('.', 1)[0] + ".docx"
    
    # Vaqtinchalik yo'llar (Render/Linux uchun /tmp ishlatish xavfsizroq)
    pdf_path = f"/tmp/{file_id}.pdf"
    word_path = f"/tmp/{file_id}.docx"
    
    status_msg = await message.answer("🛠 **Professional tahlil ketmoqda...**\n(Betlar soni va joylashuv optimallashtirilmoqda)")
    logger.info(f"Fayl ishlovga olindi: {file_name}")

    try:
        # Faylni yuklab olish
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, pdf_path)

        # Konvertatsiya sozlamalari
        cv = Converter(pdf_path)
        cv.convert(
            word_path, 
            start=0, 
            end=None,
            is_split_at_line_break=False,
            is_arrange_text=True,
            is_fit_table=True,
            is_merge_text_block=True,
            line_margin=0.05,
            force_page_size=True
        )
        cv.close()

        # Natijani yuborish
        if os.path.exists(word_path):
            output_file = FSInputFile(word_path, filename=doc_name)
            await message.answer_document(output_file, caption="✅ Optimizatsiya qilindi.")
            logger.info(f"Fayl muvaffaqiyatli o'girildi: {doc_name}")
        
        # Fayllarni tozalash
        for path in [pdf_path, word_path]:
            if os.path.exists(path):
                os.remove(path)
        
        await status_msg.delete()

    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {str(e)}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {str(e)}")


# --- SHU YERDAN BOSHLAB O'ZGARTIRING ---
# Render port talab qilgani uchun kichik soxta server
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running...")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, DummyHandler)
    logger.info(f"Soxta server {port}-portda ishga tushdi...")
    httpd.serve_forever()

@dp.message()
async def start(message: types.Message):
    await message.answer("Salom! PDF yuboring, men uni Word'ga **eng yuqori aniqlikda** o'girib beraman. 🚀")

async def main():
    # Soxta serverni alohida oqimda (thread) yurgizish
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    logger.info("Bot polling rejimi ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
