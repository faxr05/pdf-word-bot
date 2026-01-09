import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import FSInputFile
from pdf2docx import Converter

# Tizimdan tokenni olyapmiz
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Bot va Dispatcher obyektlarini yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message(F.document)
async def handle_pdf(message: types.Message):
    if not message.document.file_name.lower().endswith('.pdf'):
        return await message.answer("Iltimos, PDF yuboring 📄")

    file_id = message.document.file_id
    file_name = message.document.file_name
    doc_name = file_name.rsplit('.', 1)[0] + ".docx"
    
    status_msg = await message.answer("🛠 **Professional tahlil ketmoqda...**\n(Betlar soni va joylashuv optimallashtirilmoqda)")

    try:
        # Faylni yuklab olish
        file = await bot.get_file(file_id)
        pdf_path = f"{file_id}.pdf"
        word_path = f"{file_id}.docx"
        await bot.download_file(file.file_path, pdf_path)

        # Konvertatsiya sozlamalari (Pullik servislar darajasida)
        cv = Converter(pdf_path)
        
        cv.convert(
            word_path, 
            start=0, 
            end=None,
            # --- MUHIM SOZLAMALAR ---
            is_split_at_line_break=False, # Matnni qator oxirida majburan kesmaydi
            is_arrange_text=True,         # Matn bloklarini mantiqiy tartiblaydi
            is_fit_table=True,            # Jadvallarni sahifa kengligiga moslaydi
            is_merge_text_block=True,     # Bo'lingan matn qismlarini birlashtiradi
            line_margin=0.05,             # Qatorlar orasidagi masofani qisqartiradi (Bet ortib ketmasligi uchun)
            force_page_size=True          # PDF sahifa o'lchamini Word'da majburan saqlaydi
        )
        cv.close()

        # Natijani yuborish
        output_file = FSInputFile(word_path, filename=doc_name)
        await message.answer_document(output_file, caption="✅ Optimizatsiya qilindi.")
        
        # Tozalash
        os.remove(pdf_path)
        os.remove(word_path)
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ Xatolik: {str(e)}")

@dp.message()
async def start(message: types.Message):
    await message.answer("Salom! PDF yuboring, men uni Word'ga **eng yuqori aniqlikda** o'girib beraman.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    await main()
