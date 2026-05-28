from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

import database
import keyboards
from config import authenticated_admins

router = Router(name="jobs")

def get_jobs_markup(jobs_list):
    """Ishlar ro'yxati uchun inline klaviatura yaratish"""
    inline_keyboard = []
    for job in jobs_list:
        inline_keyboard.append([
            InlineKeyboardButton(text=f"📌 {job['title']}", callback_data=f"view_job:{job['id']}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

@router.message(F.text == "Mavjud ishlar 💼")
async def show_jobs(message: Message):
    """Mavjud ishlarni foydalanuvchiga inline tugmalar orqali ko'rsatish"""
    user_id = message.from_user.id
    user = await database.get_user(user_id)
    is_admin = (user_id in authenticated_admins)

    # Agar foydalanuvchi ro'yxatdan o'tmagan bo'lsa va tizimga kirgan admin bo'lmasa
    if not user and not is_admin:
        await message.answer(
            "Ish e'lonlarini ko'rish uchun avval ro'yxatdan o'tishingiz kerak. Iltimos, pastdagi tugmani bosing:",
            reply_markup=keyboards.get_main_menu(is_registered=False)
        )
        return

    jobs_list = await database.get_all_jobs()

    if not jobs_list:
        await message.answer(
            "Hozircha tizimda bo'sh ish o'rinlari mavjud emas. Keyinroq qayta urinib ko'ring! 🔄"
        )
        return

    markup = get_jobs_markup(jobs_list)
    await message.answer(
        "🔍 <b>Mavjud bo'sh ish o'rinlari ro'yxati:</b>\n\nBatafsil ma'lumot olish uchun kerakli ish nomi ustiga bosing:",
        reply_markup=markup
    )

@router.callback_query(F.data.startswith("view_job:"))
async def view_job_detail(callback: CallbackQuery):
    """Tanlangan ish bo'yicha batafsil ma'lumotni ko'rsatish"""
    job_id = int(callback.data.split(":")[1])
    job = await database.get_job(job_id)

    if not job:
        await callback.answer("Kechirasiz, ushbu ish e'loni topilmadi yoki o'chirilgan! ❌", show_alert=True)
        # Ro'yxatni yangilash
        jobs_list = await database.get_all_jobs()
        if jobs_list:
            await callback.message.edit_text(
                "🔍 <b>Mavjud bo'sh ish o'rinlari ro'yxati:</b>\n\nBatafsil ma'lumot olish uchun kerakli ish nomi ustiga bosing:",
                reply_markup=get_jobs_markup(jobs_list)
            )
        else:
            await callback.message.edit_text("Hozircha tizimda bo'sh ish o'rinlari mavjud emas. 🔄")
        return

    job_text = (
        f"📌 <b>Ish nomi:</b> {job['title']}\n\n"
        f"📋 <b>Tavsif:</b> {job['description']}\n\n"
        f"📞 <b>Aloqa:</b> {job['phone_number']}\n"
        f"📅 <i>Qo'shilgan sana: {job['created_at']}</i>"
    )

    back_markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Orqaga 🔙", callback_data="back_to_jobs_list")]
    ])

    await callback.message.edit_text(text=job_text, reply_markup=back_markup)
    await callback.answer()

@router.callback_query(F.data == "back_to_jobs_list")
async def back_to_jobs_list_handler(callback: CallbackQuery):
    """Ishlar ro'yxatiga qaytish"""
    jobs_list = await database.get_all_jobs()

    if not jobs_list:
        await callback.message.edit_text(
            "Hozircha tizimda bo'sh ish o'rinlari mavjud emas. Keyinroq qayta urinib ko'ring! 🔄"
        )
        await callback.answer()
        return

    markup = get_jobs_markup(jobs_list)
    await callback.message.edit_text(
        "🔍 <b>Mavjud bo'sh ish o'rinlari ro'yxati:</b>\n\nBatafsil ma'lumot olish uchun kerakli ish nomi ustiga bosing:",
        reply_markup=markup
    )
    await callback.answer()
