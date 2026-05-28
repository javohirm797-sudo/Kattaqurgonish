import os
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not BOT_TOKEN or "example" in BOT_TOKEN:
    print("OGOHLANTIRISH: .env faylida BOT_TOKEN to'g'ri kiritilmagan!")

if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        print("XATOLIK: ADMIN_ID faqat raqamlardan iborat bo'lishi kerak!")
        ADMIN_ID = 0
else:
    ADMIN_ID = 0

# Tizimga kirgan adminlarning IDlarini saqlash uchun to'plam
authenticated_admins = set()

