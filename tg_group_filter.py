import sys
import json
import subprocess
import importlib
from datetime import datetime, timedelta
import asyncio
import os

# ===  Автоустановка зависимостей ===
required_packages = ["telethon", "pytz"]
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        print(f" Устанавливаю {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Теперь можно импортировать после установки
from telethon import TelegramClient
import pytz

# ===  Конфигурация ===
CONFIG_FILE = "config.json"

def load_or_create_config():
    if not os.path.exists(CONFIG_FILE):
        print("  Файл config.json не найден. Создаю новый.")
        api_id = int(input("Введите ваш Telegram API ID: "))
        api_hash = input("Введите ваш Telegram API Hash: ").strip()
        group_link = input("Введите ссылку на Telegram-группу: ").strip()

        config = {"api_id": api_id, "api_hash": api_hash, "group_link": group_link}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ Файл config.json создан успешно!")
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    return config

# === Aнализ Telegram-группы ===
async def analyze_group(api_id, api_hash, group_link):
    client = TelegramClient("session_name", api_id, api_hash)
    await client.start()

    entity = await client.get_entity(group_link)
    tz = pytz.timezone("Asia/Tashkent")

    today = datetime.now(tz)
    start_date = today - timedelta(days=7)
    print(f" Анализ сообщений с {start_date.strftime('%Y-%m-%d')} по {today.strftime('%Y-%m-%d')}")

    messages = await client.get_messages(entity, limit=None)
    threads_by_day = {}

    for msg in messages:
        if msg.date.replace(tzinfo=pytz.UTC) < start_date.astimezone(pytz.UTC):
            continue
        date_str = msg.date.astimezone(tz).strftime("%Y-%m-%d")
        if date_str not in threads_by_day:
            threads_by_day[date_str] = {}

        thread_id = msg.reply_to_msg_id or msg.id
        user_id = msg.sender_id or 0

        if thread_id not in threads_by_day[date_str]:
            threads_by_day[date_str][thread_id] = {"topic": f"Thread {thread_id}", "messages": 0, "users": set()}

        threads_by_day[date_str][thread_id]["messages"] += 1
        threads_by_day[date_str][thread_id]["users"].add(user_id)

    output = {"timezone": "Asia/Tashkent", "days": []}
    for date_str, threads in threads_by_day.items():
        day_threads = []
        for thread in threads.values():
            day_threads.append({
                "topic": thread["topic"],
                "messages": thread["messages"],
                "users": len(thread["users"])
            })
        output["days"].append({"date": date_str, "threads": day_threads})

    with open("result.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(" Анализ завершён! Результаты сохранены в result.json")
    await client.disconnect()

# ===  Точка входа ===
if __name__ == "__main__":
    config = load_or_create_config()
    asyncio.run(analyze_group(config["api_id"], config["api_hash"], config["group_link"]))
