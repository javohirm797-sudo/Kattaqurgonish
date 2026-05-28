import aiosqlite
import datetime

DB_PATH = "bot_database.db"

async def init_db():
    """Ma'lumotlar bazasini va jadvallarni yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                profession TEXT NOT NULL,
                registered_at TEXT NOT NULL
            )
        ''')
        # Ish e'lonlari jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        await db.commit()

# --- Foydalanuvchilar bilan ishlash ---

async def add_user(telegram_id: int, full_name: str, phone_number: str, profession: str):
    """Yangi foydalanuvchini bazaga qo'shish yoki mavjud bo'lsa yangilash"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (telegram_id, full_name, phone_number, profession, registered_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, full_name, phone_number, profession, now))
        await db.commit()

async def get_user(telegram_id: int):
    """Foydalanuvchini Telegram ID si bo'yicha olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "telegram_id": row[0],
                    "full_name": row[1],
                    "phone_number": row[2],
                    "profession": row[3],
                    "registered_at": row[4]
                }
            return None

async def get_all_users():
    """Barcha ro'yxatdan o'tgan foydalanuvchilarni olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM users ORDER BY registered_at DESC') as cursor:
            rows = await cursor.fetchall()
            users = []
            for row in rows:
                users.append({
                    "telegram_id": row[0],
                    "full_name": row[1],
                    "phone_number": row[2],
                    "profession": row[3],
                    "registered_at": row[4]
                })
            return users

# --- Ish e'lonlari bilan ishlash ---

async def add_job(title: str, description: str, phone_number: str):
    """Yangi ish e'lonini bazaga qo'shish"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO jobs (title, description, phone_number, created_at)
            VALUES (?, ?, ?, ?)
        ''', (title, description, phone_number, now))
        await db.commit()

async def get_all_jobs():
    """Barcha faol ish e'lonlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM jobs ORDER BY id DESC') as cursor:
            rows = await cursor.fetchall()
            jobs = []
            for row in rows:
                jobs.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "phone_number": row[3],
                    "created_at": row[4]
                })
            return jobs

async def delete_job(job_id: int):
    """Ish e'lonini IDsi bo'yicha o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
        await db.commit()

async def get_job(job_id: int):
    """Ish e'lonini IDsi bo'yicha olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "phone_number": row[3],
                    "created_at": row[4]
                }
            return None
