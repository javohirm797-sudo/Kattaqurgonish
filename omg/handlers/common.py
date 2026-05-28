from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

import database
import keyboards
from config import ADMIN_ID

router = Router(name="common")

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start buyrug'i kelganda ishlovchi handler"""
    user_id = message.from_user.id
    user = await database.get_user(user_id)

    welcome_text = (
        "🇺🇿 <b>Ish Topish Botiga xush kelibsiz!</b>\n\n"
        "Ushbu bot yordamida o'zingizga mos bo'lgan bo'sh ish o'rinlarini topishingiz "
        "yoki o'z mutaxassisligingiz bo'yicha ro'yxatdan o'tib qo'yishingiz mumkin.\n\n"
    )

    if user:
        welcome_text += f"Salom, <b>{user['full_name']}</b>! O'zingizga kerakli bo'limni tanlang:"
    else:
        welcome_text += "Botdan to'liq foydalanish uchun iltimos <b>Ro'yxatdan o'tish 📝</b> tugmasini bosing."

    await message.answer(
        welcome_text,
        reply_markup=keyboards.get_main_menu(is_registered=user is not None)
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam buyrug'i"""
    help_text = (
        "ℹ️ <b>Botdan foydalanish bo'yicha yordam:</b>\n\n"
        "• <b>Ro'yxatdan o'tish 📝</b> - Tizimda o'z ma'lumotlaringiz bilan ro'yxatdan o'tish.\n"
        "• <b>Mavjud ishlar 💼</b> - Hozirgi kunda faol bo'lgan bo'sh ish o'rinlarini ko'rish.\n"
        "• <b>Profilim 👤</b> - Kiritgan shaxsiy ma'lumotlaringizni ko'rish.\n"
        "• <b>Qayta ro'yxatdan o'tish 🔄</b> - Ma'lumotlaringiz o'zgargan bo'lsa, ularni yangilash.\n\n"
        "📞 <b>Aloqa va yordam:</b>\n"
        "• Telefon: +998 94 776 25 28\n"
        "• Telegram: @mvln_J"
    )
    await message.answer(help_text)

@router.message(F.text == "Aloqa 📞")
async def show_contact_info(message: Message):
    """Aloqa va yordam ma'lumotlarini ko'rsatish"""
    contact_text = (
        "📞 <b>Aloqa va qo'llab-quvvatlash:</b>\n\n"
        "Agar sizda biror muammo, taklif yoki savollar bo'lsa, quyidagi kontaktlarga murojaat qilishingiz mumkin:\n\n"
        "📱 <b>Telefon:</b> +998 94 776 25 28\n"
        "✈️ <b>Telegram:</b> @mvln_J\n\n"
        "<i>Sizga yordam berishdan mamnunmiz! 😊</i>"
    )
    await message.answer(contact_text)

@router.message(F.text == "Profilim 👤")
async def show_profile(message: Message):
    """Foydalanuvchi profil ma'lumotlarini ko'rsatish"""
    user_id = message.from_user.id
    user = await database.get_user(user_id)

    if not user:
        await message.answer(
            "Siz hali ro'yxatdan o'tmagansiz. Iltimos, avval ro'yxatdan o'ting:",
            reply_markup=keyboards.get_main_menu(is_registered=False)
        )
        return

    profile_text = (
        "👤 <b>Sizning profilingiz:</b>\n\n"
        f"💳 <b>ID:</b> <code>{user['telegram_id']}</code>\n"
        f"✍️ <b>Ism va familiya:</b> {user['full_name']}\n"
        f"📞 <b>Telefon raqam:</b> {user['phone_number']}\n"
        f"💼 <b>Mutaxassislik:</b> {user['profession']}\n"
        f"📅 <b>Ro'yxatdan o'tilgan sana:</b> {user['registered_at']}"
    )
    await message.answer(profile_text)
