from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import database
import keyboards
from config import authenticated_admins

router = Router(name="admin")

class AddJob(StatesGroup):
    title = State()
    description = State()
    phone_number = State()

class AdminLogin(StatesGroup):
    username = State()
    password = State()

def is_admin_filter(message: Message) -> bool:
    return message.from_user.id in authenticated_admins

# --- Admin Panelga kirish (FSM orqali) ---

@router.message(Command("Paneladmin"))
async def start_admin_login(message: Message, state: FSMContext):
    """Admin panelga kirish FSM jarayonini boshlash"""
    await state.clear()
    await state.set_state(AdminLogin.username)
    await message.answer(
        "🔑 Admin panelga kirish.\n\n<b>Loginni kiriting:</b>",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(AdminLogin.username, F.text != "Bekor qilish ❌")
async def process_admin_username(message: Message, state: FSMContext):
    """Loginni tekshirish"""
    username = message.text.strip()
    if username == "Java2528":
        await state.set_state(AdminLogin.password)
        await message.answer(
            "🔒 To'g'ri! Endi <b>Parolni kiriting:</b>",
            reply_markup=keyboards.get_cancel_keyboard()
        )
    else:
        await state.clear()
        user = await database.get_user(message.from_user.id)
        await message.answer(
            "❌ Login xato! Admin panelga kirish rad etildi.",
            reply_markup=keyboards.get_main_menu(is_registered=user is not None)
        )

@router.message(AdminLogin.password, F.text != "Bekor qilish ❌")
async def process_admin_password(message: Message, state: FSMContext):
    """Parolni tekshirish"""
    password = message.text.strip()
    if password == "Java2323":
        authenticated_admins.add(message.from_user.id)
        await state.clear()
        await message.answer(
            "👨‍💻 Xush kelibsiz, Admin!\nTizimga muvaffaqiyatli kirdingiz.",
            reply_markup=keyboards.get_admin_menu()
        )
    else:
        await state.clear()
        user = await database.get_user(message.from_user.id)
        await message.answer(
            "❌ Parol xato! Admin panelga kirish rad etildi.",
            reply_markup=keyboards.get_main_menu(is_registered=user is not None)
        )

@router.message(F.text == "Foydalanuvchi menyusi 🔙")
async def back_to_user_menu(message: Message):
    if not is_admin_filter(message):
        return
    
    # Sessiyadan o'chirish (tizimdan chiqish)
    authenticated_admins.discard(message.from_user.id)
    user = await database.get_user(message.from_user.id)
    await message.answer(
        "Admin paneldan chiqdingiz va foydalanuvchi menyusiga qaytdingiz.",
        reply_markup=keyboards.get_main_menu(is_registered=user is not None)
    )

# --- 1. Foydalanuvchilar Ro'yxati ---

@router.message(F.text == "Foydalanuvchilar ro'yxati 👥")
async def show_registered_users(message: Message):
    if not is_admin_filter(message):
        return

    users = await database.get_all_users()
    if not users:
        await message.answer("Hozircha hech kim ro'yxatdan o'tmagan. 👥")
        return

    response = "👥 <b>Ro'yxatdan o'tgan foydalanuvchilar:</b>\n\n"
    for idx, user in enumerate(users, 1):
        response += (
            f"{idx}. <b>Ism:</b> {user['full_name']}\n"
            f"   📞 <b>Tel:</b> {user['phone_number']}\n"
            f"   💼 <b>Kasb:</b> {user['profession']}\n"
            f"   📅 <b>Sana:</b> {user['registered_at']}\n"
            f"──────────────────\n"
        )
        if len(response) > 3500:
            await message.answer(response)
            response = ""

    if response:
        await message.answer(response)

# --- 2. Yangi Ish Qo'shish (FSM) ---

@router.message(F.text == "Yangi ish qo'shish ➕")
async def start_add_job(message: Message, state: FSMContext):
    if not is_admin_filter(message):
        return
        
    await state.set_state(AddJob.title)
    await message.answer(
        "Yangi ish e'lonini qo'shish jarayoni boshlandi.\n\n<b>Ish nomini kiriting:</b> (Masalan: Avtoservis ustasi, Ofis menejeri)",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(AddJob.title, F.text != "Bekor qilish ❌")
async def process_job_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 3:
        await message.answer("Ish nomi juda qisqa. Iltimos, batafsilroq kiriting:")
        return

    await state.update_data(title=title)
    await state.set_state(AddJob.description)
    await message.answer(
        "Rahmat! Endi <b>ish bo'yicha batafsil tavsif (sharoitlar, maosh, talablar)</b> yozib yuboring:",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(AddJob.description, F.text != "Bekor qilish ❌")
async def process_job_desc(message: Message, state: FSMContext):
    description = message.text.strip()
    if len(description) < 10:
        await message.answer("Tavsif juda qisqa. Iltimos, ish haqida batafsilroq ma'lumot bering:")
        return

    await state.update_data(description=description)
    await state.set_state(AddJob.phone_number)
    await message.answer(
        "Rahmat! Endi <b>bog'lanish uchun telefon raqamini</b> kiriting (Masalan: +998901234567):",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(AddJob.phone_number, F.text != "Bekor qilish ❌")
async def process_job_phone(message: Message, state: FSMContext):
    phone_number = message.text.strip()
    if len(phone_number) < 7:
        await message.answer("Telefon raqami noto'g'ri. Iltimos, to'g'ri raqam kiriting:")
        return

    data = await state.get_data()
    await database.add_job(
        title=data['title'],
        description=data['description'],
        phone_number=phone_number
    )
    
    await state.clear()
    await message.answer(
        "✅ Yangi ish e'loni muvaffaqiyatli saqlandi va barcha foydalanuvchilarga ko'rinadigan bo'ldi!",
        reply_markup=keyboards.get_admin_menu()
    )

# --- 3. Ishlarni O'chirish ---

@router.message(F.text == "Ishlarni o'chirish 🗑️")
async def show_jobs_to_delete(message: Message):
    if not is_admin_filter(message):
        return

    jobs_list = await database.get_all_jobs()
    if not jobs_list:
        await message.answer("Hozircha tizimda o'chirish uchun ish e'lonlari yo'q.")
        return

    await message.answer("🗑️ O'chirmoqchi bo'lgan ish e'loningiz ostidagi tugmani bosing:")

    for job in jobs_list:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="O'chirish ❌", callback_data=f"delete_job:{job['id']}")]
        ])
        job_text = (
            f"📌 <b>{job['title']}</b>\n"
            f"📞 <b>Aloqa:</b> {job['phone_number']}\n"
            f"📅 <i>Kiritilgan sana: {job['created_at']}</i>"
        )
        await message.answer(job_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete_job:"))
async def process_delete_job(callback: CallbackQuery):
    if callback.from_user.id not in authenticated_admins:
        await callback.answer("Ruxsat yo'q!", show_alert=True)
        return

    job_id = int(callback.data.split(":")[1])
    await database.delete_job(job_id)
    await callback.answer("Ish e'loni o'chirildi! ✅", show_alert=True)
    await callback.message.delete()

# --- FSMni bekor qilish ---
@router.message(StateFilter(AdminLogin, AddJob), F.text == "Bekor qilish ❌")
async def cancel_admin_fsm(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
        
    await state.clear()
    user_id = message.from_user.id
    if user_id in authenticated_admins:
        await message.answer(
            "Jarayon bekor qilindi.",
            reply_markup=keyboards.get_admin_menu()
        )
    else:
        user = await database.get_user(user_id)
        await message.answer(
            "Jarayon bekor qilindi.",
            reply_markup=keyboards.get_main_menu(is_registered=user is not None)
        )
