import asyncio
import uvicorn
import sqlite3
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8447546621:AAGGqV0YMPjcSJ3hkiZ7niFHo4LvAkNTjmg"
TUNNEL_URL = "https://8c6cde8bfadd4c.lhr.life/" # Не забудь обновить после перезапуска туннеля!

# --- БАЗА ДАННЫХ (SQLite) ---
def init_db():
    """Создает таблицы в файле game.db, если их еще нет"""
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            hp INTEGER,
            damage INTEGER,
            armor INTEGER,
            inventory TEXT,
            equipped_weapon TEXT,
            equipped_armor TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Шаблоны всех предметов в игре
ITEM_TEMPLATES = {
    "sword_1": {"id": "sword_1", "name": "Ржавый меч", "type": "weapon", "damage": 10, "armor": 0, "icon": "🗡"},
    "armor_1": {"id": "armor_1", "name": "Кожанка", "type": "armor", "damage": 0, "armor": 5, "icon": "🛡"},
    "potion_1": {"id": "potion_1", "name": "Зелье", "type": "consumable", "heal": 50, "icon": "🧪"}
}

def get_or_create_user(user_id: int):
    """Ищет игрока в базе. Если нет - создает нового."""
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        # Выдаем стартовый набор
        default_inv = ["sword_1", "armor_1", "potion_1"]
        cursor.execute('''
            INSERT INTO users (user_id, hp, damage, armor, inventory, equipped_weapon, equipped_armor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, 100, 5, 2, json.dumps(default_inv), None, None))
        conn.commit()
        row = (user_id, 100, 5, 2, json.dumps(default_inv), None, None)
        
    conn.close()
    return row

# --- WEB API (FastAPI) ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели запросов
class EquipRequest(BaseModel):
    user_id: int
    item_id: str

# Раздача файлов фронтенда
@app.get("/")
async def serve_index(): return FileResponse("index.html")
@app.get("/style.css")
async def serve_css(): return FileResponse("style.css")
@app.get("/app.js")
async def serve_js(): return FileResponse("app.js")

@app.get("/api/player")
async def get_player_data(user_id: int):
    """Отдает данные конкретного игрока по его user_id"""
    row = get_or_create_user(user_id)
    
    # Индексы: 0=id, 1=hp, 2=dmg, 3=armor, 4=inv, 5=eq_weapon, 6=eq_armor
    base_dmg = row[2]
    base_armor = row[3]
    weapon_id = row[5]
    armor_id = row[6]
    
    # Собираем данные надетых вещей
    weapon_data = ITEM_TEMPLATES.get(weapon_id) if weapon_id else None
    armor_data = ITEM_TEMPLATES.get(armor_id) if armor_id else None
    
    # Пересчет статов
    if weapon_data: base_dmg += weapon_data["damage"]
    if armor_data: base_armor += armor_data["armor"]
    
    # Собираем инвентарь
    inv_ids = json.loads(row[4])
    inv_data = [ITEM_TEMPLATES[i] for i in inv_ids if i in ITEM_TEMPLATES]
    
    return {
        "stats": {"hp": row[1], "damage": base_dmg, "armor": base_armor},
        "inventory": inv_data,
        "equipped": {"weapon": weapon_data, "armor": armor_data}
    }

@app.post("/api/equip")
async def equip_item(req: EquipRequest):
    """Надевает предмет, обновляя запись в БД"""
    row = get_or_create_user(req.user_id)
    inv_ids = json.loads(row[4])
    
    # Проверка: есть ли предмет у игрока в рюкзаке?
    if req.item_id not in inv_ids:
        return {"status": "error", "message": "Предмет не найден"}
        
    item = ITEM_TEMPLATES.get(req.item_id)
    if not item: return {"status": "error"}
    
    conn = sqlite3.connect("game.db")
    cursor = conn.cursor()
    
    if item["type"] == "weapon":
        cursor.execute("UPDATE users SET equipped_weapon = ? WHERE user_id = ?", (req.item_id, req.user_id))
    elif item["type"] == "armor":
        cursor.execute("UPDATE users SET equipped_armor = ? WHERE user_id = ?", (req.item_id, req.user_id))
    else:
        conn.close()
        return {"status": "error", "message": "Это нельзя надеть"}
        
    conn.commit()
    conn.close()
    return {"status": "success"}

# --- ТЕЛЕГРАМ БОТ (Aiogram) ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎒 Открыть инвентарь", web_app=WebAppInfo(url=TUNNEL_URL))]
    ])
    await message.answer("Добро пожаловать в Мультиплеер! Твой прогресс теперь сохраняется.", reply_markup=markup)

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.create_task(server.serve())
    loop.run_until_complete(start_bot())
