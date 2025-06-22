import telebot
import flask
import os

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, f"Вы сказали: {message.text}")


@app.route(f"/{API_TOKEN}", methods=["POST"])
def webhook():
    json_str = flask.request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200


@app.route("/")
def index():
    return "Бот работает!"


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=10000)
