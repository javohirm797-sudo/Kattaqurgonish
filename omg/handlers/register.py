from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

import database
import keyboards

router = Router(name="register")

class Registration(StatesGroup):
    name = State()
    phone = State()
    profession = State()

@router.message(F.text.in_({"Ro'yxatdan o'tish 📝", "Qayta ro'yxatdan o'tish 🔄"}))
async def start_registration(message: Message, state: FSMContext):
    """Ro'yxatdan o'tishni boshlash"""
    await state.clear()
    await state.set_state(Registration.name)
    await message.answer(
        "Keling, ro'yxatdan o'tamiz!\n\n<b>Ism va familiyangizni</b> kiriting:",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(StateFilter(Registration), F.text == "Bekor qilish ❌")
async def cancel_registration(message: Message, state: FSMContext):
    """Ro'yxatdan o'tishni bekor qilish"""
    current_state = await state.get_state()
    if current_state is None:
        return
        
    await state.clear()
    user = await database.get_user(message.from_user.id)
    
    await message.answer(
        "Ro'yxatdan o'tish bekor qilindi.",
        reply_markup=keyboards.get_main_menu(is_registered=user is not None)
    )

@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    """Ismni qabul qilish"""
    name = message.text.strip()
    if len(name) < 3:
        await message.answer("Ism juda qisqa. Iltimos, to'liq ism va familiyangizni kiriting:")
        return
        
    await state.update_data(name=name)
    await state.set_state(Registration.phone)
    await message.answer(
        "Rahmat! Endi pastdagi <b>Telefon raqamni yuborish 📞</b> tugmasini bosing yoki raqamingizni yozib yuboring (Masalan: +998901234567):",
        reply_markup=keyboards.get_phone_keyboard()
    )

@router.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqamini qabul qilish"""
    phone_number = None
    
    if message.contact:
        phone_number = message.contact.phone_number
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number
    else:
        # Oddiy matn ko'rinishida yuborilgan bo'lsa
        text = message.text.strip()
        # Oddiy raqamlarni tekshirish (masalan +998...)
        if text.startswith("+") and text[1:].isdigit() and len(text) >= 9:
            phone_number = text
        elif text.isdigit() and len(text) >= 9:
            phone_number = "+" + text
        else:
            await message.answer(
                "Telefon raqami formati noto'g'ri. Iltimos, pastdagi tugmani bosing yoki raqamni to'g'ri kiriting (+998901234567):"
            )
            return

    await state.update_data(phone=phone_number)
    await state.set_state(Registration.profession)
    await message.answer(
        "Rahmat! Oxirgi bosqich:\n\n<b>Mutaxassisligingiz yoki qiziqayotgan sohangizni</b> yozing (Masalan: Quruvchi, Dasturchi, Sotuvchi, Tikuvchi va h.k.):",
        reply_markup=keyboards.get_cancel_keyboard()
    )

@router.message(Registration.profession)
async def process_profession(message: Message, state: FSMContext):
    """Mutaxassislikni qabul qilish va saqlash"""
    profession = message.text.strip()
    if len(profession) < 2:
        await message.answer("Mutaxassislik nomi juda qisqa. Iltimos, aniqroq yozing:")
        return

    data = await state.get_data()
    await database.add_user(
        telegram_id=message.from_user.id,
        full_name=data['name'],
        phone_number=data['phone'],
        profession=profession
    )
    
    await state.clear()
    
    await message.answer(
        "🎉 Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz.",
        reply_markup=keyboards.get_main_menu(is_registered=True)
    )
