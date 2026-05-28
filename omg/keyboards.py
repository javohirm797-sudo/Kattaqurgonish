from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu(is_registered=False):
    """Asosiy menyu klaviaturasi"""
    buttons = []
    
    # Ro'yxatdan o'tgan foydalanuvchilar va mehmonlar uchun tugmalar
    if is_registered:
        buttons.append([KeyboardButton(text="Mavjud ishlar 💼")])
        buttons.append([KeyboardButton(text="Profilim 👤"), KeyboardButton(text="Qayta ro'yxatdan o'tish 🔄")])
        buttons.append([KeyboardButton(text="Aloqa 📞")])
    else:
        buttons.append([KeyboardButton(text="Ro'yxatdan o'tish 📝")])
        buttons.append([KeyboardButton(text="Mavjud ishlar 💼"), KeyboardButton(text="Aloqa 📞")])
        
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        placeholder="Bo'limni tanlang..."
    )

def get_phone_keyboard():
    """Kontakt ulashish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Telefon raqamni yuborish 📞", request_contact=True)],
            [KeyboardButton(text="Bekor qilish ❌")]
        ],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    """Bekor qilish tugmasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Bekor qilish ❌")]
        ],
        resize_keyboard=True
    )

def get_admin_menu():
    """Admin panel klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Foydalanuvchilar ro'yxati 👥")],
            [KeyboardButton(text="Yangi ish qo'shish ➕"), KeyboardButton(text="Ishlarni o'chirish 🗑️")],
            [KeyboardButton(text="Foydalanuvchi menyusi 🔙")]
        ],
        resize_keyboard=True
    )
