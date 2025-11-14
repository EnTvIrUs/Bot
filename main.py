import json
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ---------------------------------------
# КОНФИГ
# ---------------------------------------
BOT_TOKEN = "8513948065:AAFBcJoQjsJPp4tRLk01FLzV5XVSA9F34Kc"

ADMIN_ID = 8406397454
ORDERS_GROUP = -1003270554063
SUB_CHANNEL = -1003475444185
CRYPTO_WALLET = "0x5bb542b163f7d9545b16d18e85619401102e88e4"

MONTH_PRICE = 10  # 10 USDT


# ---------------------------------------
# ФАЙЛЫ ДАННЫХ
# ---------------------------------------
DATA_FILE = "users.json"
ITEMS_FILE = "items.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(ITEMS_FILE):
    with open(ITEMS_FILE, "w") as f:
        json.dump({}, f)


# ---------------------------------------
# ФУНКЦИИ
# ---------------------------------------
def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_items():
    with open(ITEMS_FILE, "r") as f:
        return json.load(f)

def save_items(data):
    with open(ITEMS_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------
# BOT
# ---------------------------------------
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# ---------------------------------------
# СТАРТ
# ---------------------------------------
@dp.message(Command("start"))
async def start(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Каталог", callback_data="catalog")
    kb.button(text="Заказ на заказ", callback_data="order_custom")
    kb.button(text="Подписка", callback_data="subscription")

    await msg.answer(
        "Добро пожаловать. Выбери действие.",
        reply_markup=kb.as_markup()
    )


# ---------------------------------------
# КАТАЛОГ
# ---------------------------------------
@dp.callback_query(F.data == "catalog")
async def catalog_menu(call):
    items = load_items()
    if not items:
        await call.message.edit_text("Каталог пуст.")
        return

    kb = InlineKeyboardBuilder()
    for item_id, item in items.items():
        kb.button(text=item["name"], callback_data=f"buy_{item_id}")

    await call.message.edit_text("Каталог товаров:", reply_markup=kb.as_markup())


# ---------------------------------------
# ПОКУПКА
# ---------------------------------------
@dp.callback_query(F.data.startswith("buy_"))
async def buy_item(call):
    item_id = call.data.split("_")[1]
    items = load_items()

    if item_id not in items:
        await call.answer("Товар не найден.")
        return

    item = items[item_id]

    await call.message.edit_text(
        f"Товар: {item['name']}\n"
        f"Цена: {item['price']} USDT\n\n"
        f"Оплатите на кошелёк:\n`{CRYPTO_WALLET}`\n\n"
        f"После оплаты нажмите кнопку ниже.",
        parse_mode="Markdown"
    )


# ---------------------------------------
# ЗАКАЗ НА ЗАКАЗ
# ---------------------------------------
@dp.callback_query(F.data == "order_custom")
async def custom_order(call):
    await call.message.edit_text(
        "Напиши требования для заказа."
    )


@dp.message(F.text & ~Command("start"))
async def custom_order_msg(msg: Message):
    if msg.chat.id == ADMIN_ID:
        return

    user = msg.from_user.username or msg.from_user.id

    await bot.send_message(
        ORDERS_GROUP,
        f"НОВЫЙ ЗАКАЗ:\n\n"
        f"От: @{user}\n"
        f"ID: {msg.from_user.id}\n"
        f"Сообщение:\n{msg.text}"
    )

    await msg.answer("Заказ отправлен. Ожидайте ответа.")


# ---------------------------------------
# ПОДПИСКА
# ---------------------------------------
@dp.callback_query(F.data == "subscription")
async def subscription_menu(call):
    await call.message.edit_text(
        f"Цена подписки: {MONTH_PRICE} USDT / месяц\n\n"
        f"Кошелёк для оплаты:\n`{CRYPTO_WALLET}`\n\n"
        f"После оплаты напишите /check",
        parse_mode="Markdown"
    )


@dp.message(Command("check"))
async def check_sub(msg: Message):
    user_id = msg.from_user.id

    # Здесь должна быть реальная проверка транзакции
    # Шаблонный ответ:
    await msg.answer("Оплата пока не найдена. Если ты точно оплатил — подожди 1–10 минут.")


# ---------------------------------------
# АДМИН: ДОБАВЛЕНИЕ ТОВАРА
# ---------------------------------------
@dp.message(Command("add") & (F.from_user.id == ADMIN_ID))
async def admin_add(msg: Message):
    text = msg.text.split(maxsplit=3)

    if len(text) < 4:
        await msg.answer("Использование:\n/add id название цена")
        return

    item_id = text[1]
    name = text[2]
    price = text[3]

    items = load_items()
    items[item_id] = {"name": name, "price": price}
    save_items(items)

    await msg.answer("Товар добавлен.")


# ---------------------------------------
# RUN
# ---------------------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.run_polling(bot))
