import os
import json
import requests
import telebot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-opus")
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE", "Ты профессиональный психолог.")

HISTORY_FILE = "history.json"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def load_history(chat_id):
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        all_history = json.load(f)
    return all_history.get(str(chat_id), [])

def save_message(chat_id, role, content):
    if not os.path.exists(HISTORY_FILE):
        all_history = {}
    else:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            all_history = json.load(f)

    history = all_history.get(str(chat_id), [])
    history.append({"role": role, "content": content})
    all_history[str(chat_id)] = history[-10:]  # Ограничиваем контекст до 10 сообщений

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(all_history, f, indent=2, ensure_ascii=False)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    chat_id = message.chat.id

    save_message(chat_id, "user", user_input)

    history = [{"role": "system", "content": SYSTEM_MESSAGE}]
    history += load_history(chat_id)

    payload = {
        "model": MODEL_NAME,
        "messages": history
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://t.me/your_bot_username",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=20
        )

        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = "⚠️ Ошибка от OpenRouter: " + response.text

    except Exception as e:
        reply = f"❌ Ошибка при запросе: {e}"

    save_message(chat_id, "assistant", reply)
    bot.reply_to(message, reply)

print("🧠 Бот с памятью запущен!")
bot.infinity_polling()
