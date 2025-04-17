import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta
import os

# CONFIGURATIONS
BOT_TOKEN = "7935399123:AAGfLRXdKW-Zh8PCqUJ_mLnA1D7jEmdCIAY"
ADMIN_ID = 7935399123
START_BALANCE = 50
REF_BONUS = 100
WITHDRAW_OPEN_LEVEL = 5
MAX_LEVEL = 25
MIN_WITHDRAW_RUB = 15
RUB_TO_TANGA = 349
REQUIRED_REFERRALS = 5
REQUIRED_BONUS_DAYS = 15

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# LOAD OR INIT USERS DATA
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

with open("users.json") as f:
    users = json.load(f)

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def create_user(user_id, ref_id=None):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "balance": START_BALANCE,
            "ref": ref_id,
            "refs": [],
            "level": 1,
            "bonus_days": 0,
            "last_bonus": None
        }
        if ref_id and str(ref_id) in users:
            users[str(ref_id)]["refs"].append(user_id)
            users[str(ref_id)]["balance"] += REF_BONUS
        save_users()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    ref_id = int(args) if args.isdigit() else None
    create_user(user_id, ref_id)
    await message.answer("UZO SPACE o'yiniga xush kelibsiz! Sizda 50 tanga bor.")

@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    user = users.get(str(message.from_user.id))
    if user:
        await message.answer(f"Balansingiz: {user['balance']} tanga")

@dp.message_handler(commands=['bonus'])
async def daily_bonus(message: types.Message):
    user = users.get(str(message.from_user.id))
    if not user:
        return

    now = datetime.now().date()
    last = user.get("last_bonus")
    if last:
        last = datetime.strptime(last, "%Y-%m-%d").date()
        if last == now:
            await message.answer("Siz bugungi bonusni oldingiz.")
            return

    user["balance"] += 10
    user["bonus_days"] += 1
    user["last_bonus"] = now.strftime("%Y-%m-%d")
    save_users()
    await message.answer("Sizga 10 tanga bonus berildi!")

@dp.message_handler(commands=['levelup'])
async def level_up(message: types.Message):
    user = users.get(str(message.from_user.id))
    if user:
        if user['level'] < MAX_LEVEL:
            user['level'] += 1
            save_users()
            await message.answer(f"Tabriklaymiz! Siz {user['level']}-darajaga o'tdingiz.")
        else:
            await message.answer("Siz allaqachon maksimal darajadasiz.")

@dp.message_handler(commands=['withdraw'])
async def withdraw(message: types.Message):
    user = users.get(str(message.from_user.id))
    if not user:
        return

    if user['level'] < WITHDRAW_OPEN_LEVEL:
        await message.answer("Pul yechish uchun kamida 5-darajaga yeting.")
        return

    if len(user['refs']) < REQUIRED_REFERRALS:
        await message.answer("Pul yechish uchun 5 ta do‘stni taklif qiling.")
        return

    if user['bonus_days'] < REQUIRED_BONUS_DAYS:
        await message.answer("Pul yechish uchun 15 kun bonus oling.")
        return

    if user['balance'] < MIN_WITHDRAW_RUB * RUB_TO_TANGA:
        await message.answer(f"Minimal pul yechish uchun {MIN_WITHDRAW_RUB * RUB_TO_TANGA} tanga kerak.")
        return

    await message.answer("Pul yechish uchun ariza qabul qilindi. Admin bilan bog‘laning.")
    await bot.send_message(ADMIN_ID, f"Yangi pul yechish so‘rovi: {message.from_user.id} - {user['balance']} tanga")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
  
