import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8447546621:AAGGqV0YMPjcSJ3hkiZ7niFHo4LvAkNTjmg"

# ВАЖНО: Вставь сюда свежую ссылку из Termux (со слешем / на конце!)
TUNNEL_URL = "https://8c6cde8bfadd4c.lhr.life/" 

# --- ИМИТАЦИЯ БАЗЫ ДАННЫХ ---
player_db = {
    "base_stats": {"hp": 100, "damage": 5, "armor": 2},
    "inventory": [
        {"id": "sword_1", "name": "Ржавый меч", "type": "weapon", "damage": 10, "armor": 0, "icon": "🗡"},
        {"id": "armor_1", "name": "Кожанка", "type": "armor", "damage": 0, "armor": 5, "icon": "🛡"},
        {"id": "potion_1", "name": "Зелье", "type": "consumable", "heal": 50, "icon": "🧪"}
    ],
    "equipped": {
        "weapon": None,
        "armor": None
    }
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EquipRequest(BaseModel):
    item_id: str

# --- РАЗДАЧА ФАЙЛОВ ФРОНТЕНДА (GitHub больше не нужен!) ---
@app.get("/")
async def serve_index():
    return FileResponse("index.html")

@app.get("/style.css")
async def serve_css():
    return FileResponse("style.css")

@app.get("/app.js")
async def serve_js():
    return FileResponse("app.js")

# --- WEB API ---
@app.get("/api/player")
async def get_player_data():
    total_damage = player_db["base_stats"]["damage"]
    total_armor = player_db["base_stats"]["armor"]
    
    if player_db["equipped"]["weapon"]:
        total_damage += player_db["equipped"]["weapon"]["damage"]
    if player_db["equipped"]["armor"]:
        total_armor += player_db["equipped"]["armor"]["armor"]
        
    return {
        "stats": {
            "hp": player_db["base_stats"]["hp"], 
            "damage": total_damage, 
            "armor": total_armor
        },
        "inventory": player_db["inventory"],
        "equipped": player_db["equipped"]
    }

@app.post("/api/equip")
async def equip_item(req: EquipRequest):
    item = next((i for i in player_db["inventory"] if i["id"] == req.item_id), None)
    if not item:
        return {"status": "error", "message": "Предмет не найден"}
    
    if item["type"] in ["weapon", "armor"]:
        player_db["equipped"][item["type"]] = item
        return {"status": "success"}
    
    return {"status": "error", "message": "Это нельзя надеть"}

# --- ТЕЛЕГРАМ БОТ ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎒 Открыть инвентарь", web_app=WebAppInfo(url=TUNNEL_URL))]
    ])
    await message.answer("Добро пожаловать. Проверь свое снаряжение!", reply_markup=markup)

async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    loop = asyncio.get_event_loop()
    loop.create_task(server.serve())
    loop.run_until_complete(start_bot())
