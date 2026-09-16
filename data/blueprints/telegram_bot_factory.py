"""
=============================================================================
🤖 EduHub Telegram Bot Factory: Automated 24/7 Sales, Catalog & Lead Machine
=============================================================================
Zero-dependency, production-ready Python Telegram bot.
Supports: Interactive Inline Buttons, Catalog Navigation, Lead Collection,
FAQ responder, and instant forwarding of customer leads to Admin chat ID.

QUICK 3-STEP START:
1. Open @BotFather in Telegram, send /newbot, and copy your BOT_TOKEN.
2. Put your token and Telegram ID in the configuration below.
3. Run: python telegram_bot_factory.py
"""

import urllib.request
import json
import time

# --- CONFIGURATION (FILL YOUR DETAILS) ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # e.g., "1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ"
ADMIN_CHAT_ID = "YOUR_CHAT_ID_HERE"  # Your personal Telegram ID to receive leads

API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Catalog items & prices
CATALOG = [
    {"id": "prod_1", "name": "🎓 Cambridge IELTS 3-Day Examiner Pass", "price": "$1.00"},
    {"id": "prod_2", "name": "💼 ATS Resume & Job Tailor", "price": "$1.00"},
    {"id": "prod_3", "name": "⚡ 30-Day Viral Content Factory", "price": "$1.00"},
    {"id": "prod_4", "name": "🤖 Telegram Lead Bot Template", "price": "$1.00"}
]

# FAQ Answers
FAQ = {
    "faq_payment": "💳 We accept Visa, Mastercard, Humo/Uzcard, and international cards via Dodo Payments ($1 each).",
    "faq_delivery": "⚡ All products and access tokens are delivered instantly right inside this chat and via email.",
    "faq_support": "👨‍💻 Support team: Contact @MohimbegimUsmonova or email support@eduhub.ai."
}

user_states = {}

def api_call(method, payload):
    url = f"{API_BASE}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[ERROR] API {method}: {e}")
        return None

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def main():
    print("🤖 EduHub Telegram Bot Factory is running! Waiting for customers...")
    offset = 0
    while True:
        try:
            updates = api_call("getUpdates", {"offset": offset, "timeout": 30})
            if updates and updates.get("ok"):
                for u in updates.get("result", []):
                    offset = u["update_id"] + 1
                    handle_update(u)
        except Exception as e:
            print(f"[LOOP ERROR] {e}")
            time.sleep(2)

def handle_update(update):
    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        username = msg.get("from", {}).get("username", "anonymous")

        if text == "/start":
            welcome_text = (
                f"👋 <b>Добро пожаловать в EduHub AI Store!</b>

"
                f"Мы автоматизируем учебу, карьеру и бизнес с помощью ИИ-полуфабрикатов по $1.
"
                f"Выберите интересующий раздел меню ниже:"
            )
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📦 Каталог товаров ($1)", "callback_data": "menu_catalog"}],
                    [{"text": "❓ Частые вопросы (FAQ)", "callback_data": "menu_faq"}],
                    [{"text": "📞 Оставить заявку менеджеру", "callback_data": "menu_contact"}]
                ]
            }
            send_message(chat_id, welcome_text, keyboard)

        elif user_states.get(chat_id) == "waiting_for_lead":
            # Forward lead to admin
            lead_info = f"🔥 <b>Новая заявка от клиента!</b>\n\nПользователь: @{username}\nКонтакты / Запрос: {text}"
            send_message(ADMIN_CHAT_ID, lead_info)
            send_message(chat_id, "✅ <b>Спасибо!</b> Ваша заявка принята. Менеджер свяжется с вами в течение 10 минут.")
            user_states[chat_id] = None

    elif "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        api_call("answerCallbackQuery", {"callback_query_id": cb["id"]})

        if data == "menu_catalog":
            cat_text = "🛍️ <b>Каталог готовых ИИ-полуфабрикатов по $1:</b>\n\n"
            keyboard_buttons = []
            for item in CATALOG:
                cat_text += f"• <b>{item['name']}</b> — {item['price']}\n"
                keyboard_buttons.append([{"text": f"Купить {item['name']} ({item['price']})", "callback_data": f"buy_{item['id']}"}])
            keyboard_buttons.append([{"text": "« Назад в меню", "callback_data": "menu_main"}])
            send_message(chat_id, cat_text, {"inline_keyboard": keyboard_buttons})

        elif data.startswith("buy_"):
            prod_id = data.replace("buy_", "")
            send_message(chat_id, f"💳 Для оплаты $1 перейдите по защищенной ссылке Dodo Payments:\nhttps://eduhub.ai/blueprints\n\nПосле оплаты файл откроется моментально!")

        elif data == "menu_contact":
            user_states[chat_id] = "waiting_for_lead"
            send_message(chat_id, "✍️ Напишите ваше имя и номер телефона (или вопрос), и менеджер свяжется с вами:")

        elif data == "menu_faq":
            faq_text = f"❓ <b>Ответы на частые вопросы:</b>\n\n{FAQ['faq_payment']}\n\n{FAQ['faq_delivery']}\n\n{FAQ['faq_support']}"
            keyboard = {"inline_keyboard": [[{"text": "« Назад", "callback_data": "menu_main"}]]}
            send_message(chat_id, faq_text, keyboard)

        elif data == "menu_main":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "📦 Каталог товаров ($1)", "callback_data": "menu_catalog"}],
                    [{"text": "❓ Частые вопросы (FAQ)", "callback_data": "menu_faq"}],
                    [{"text": "📞 Оставить заявку менеджеру", "callback_data": "menu_contact"}]
                ]
            }
            send_message(chat_id, "Главное меню:", keyboard)

if __name__ == "__main__":
    main()