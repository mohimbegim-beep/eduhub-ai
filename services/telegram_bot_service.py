#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EduHub AI — Autonomous Telegram Bot Service (@eduhub_ielts_bot)
Role: 24/7 Telegram Copilot for IELTS Candidates & Students.
"""

import os
import sys
import json
import time
import base64
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

env_file = BASE_DIR / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"\'')
                    if k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
PRODUCTION_URL = os.getenv("PRODUCTION_URL", "https://eduhub-ai.onrender.com").rstrip("/")
IELTS_WEBAPP_URL = f"{PRODUCTION_URL}/ielts/checker"
PRICING_URL = f"{PRODUCTION_URL}/#pricing"

def send_telegram_request(method: str, payload: dict) -> dict:
    url = f"{TELEGRAM_API_URL}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[TELEGRAM ERROR] Request to {method} failed: {e}")
        return {"ok": False, "error": str(e)}

def send_message(
    chat_id: int,
    text: str,
    reply_markup: Optional[dict] = None,
    parse_mode: str = "Markdown"
) -> dict:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return send_telegram_request("sendMessage", payload)

def send_chat_action(chat_id: int, action: str = "typing") -> dict:
    return send_telegram_request("sendChatAction", {"chat_id": chat_id, "action": action})

OWNER_CONFIG_FILE = BASE_DIR / "data" / "owner_config.json"

def get_owner_chat_id() -> Optional[int]:
    """Retrieves owner chat ID from environment variable or persisted data/owner_config.json."""
    env_id = os.getenv("TELEGRAM_OWNER_CHAT_ID")
    if env_id:
        try:
            return int(env_id)
        except ValueError:
            pass
    if OWNER_CONFIG_FILE.exists():
        try:
            data = json.loads(OWNER_CONFIG_FILE.read_text(encoding="utf-8"))
            cid = data.get("owner_chat_id")
            if cid:
                return int(cid)
        except Exception:
            pass
    return None

def save_owner_chat_id(chat_id: int, username: str = "", first_name: str = "") -> bool:
    """Binds owner chat ID and persists to data/owner_config.json."""
    try:
        OWNER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "owner_chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "registered_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        OWNER_CONFIG_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        os.environ["TELEGRAM_OWNER_CHAT_ID"] = str(chat_id)
        return True
    except Exception as e:
        print(f"[OWNER BIND ERROR] {e}")
        return False

def is_owner(chat_id: int) -> bool:
    owner_id = get_owner_chat_id()
    return owner_id is not None and int(chat_id) == int(owner_id)

def get_system_stats_summary() -> str:
    analytics_file = BASE_DIR / "data" / "visitor_analytics.json"
    balances_file = BASE_DIR / "data" / "user_balances.json"
    
    total_views = 0
    unique_visitors = 0
    if analytics_file.exists():
        try:
            d = json.loads(analytics_file.read_text(encoding="utf-8"))
            total_views = d.get("all_time", {}).get("total_pageviews", 0)
            unique_visitors = len(d.get("all_time", {}).get("unique_visitors", []))
        except Exception:
            pass

    pro_users = 0
    total_users = 0
    if balances_file.exists():
        try:
            u = json.loads(balances_file.read_text(encoding="utf-8"))
            total_users = len(u)
            pro_users = sum(1 for usr in u.values() if usr.get("role") == "pro_max" or usr.get("is_subscribed"))
        except Exception:
            pass

    now_utc = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    return (
        "📊 *СВОДКА EDUHUB AI (ПУЛЬТ УПРАВЛЕНИЯ):*\n\n"
        f"👥 *Уникальных посетителей:* `{unique_visitors}`\n"
        f"👀 *Всего просмотров страниц:* `{total_views}`\n"
        f"🎓 *Зарегистрировано студентов:* `{total_users}`\n"
        f"💎 *Активных Pro Max подписчиков:* `{pro_users}`\n\n"
        f"🌐 *Сервер:* `Online (Render + Dodo MoR)`\n"
        f"🤖 *AI Ядро:* `Gemini 2.5 Flash Ultra`\n"
        f"🕒 *Срез данных на:* `{now_utc}`"
    )

def notify_owner(event_type: str, title: str, details: Optional[Dict[str, Any]] = None) -> bool:
    """
    Sends an instant structured alert to the owner's Telegram.
    event_type: 'payment', 'essay', 'lead', 'system'
    """
    owner_id = get_owner_chat_id()
    if not owner_id:
        return False

    details = details or {}
    now_str = time.strftime("%H:%M:%S UTC", time.gmtime())

    if event_type == "payment":
        icon = "🎉"
        amount = details.get("amount", "$1.00")
        tier = details.get("tier", "Pro Max (3 Days)")
        email = details.get("email", "client@email.com")
        order_id = details.get("order_id", "N/A")
        msg = (
            f"{icon} *НОВАЯ ОПЛАТА НА САЙТЕ!*\n\n"
            f"💰 *Сумма:* `{amount}`\n"
            f"💎 *Тариф:* {tier}\n"
            f"👤 *Клиент:* `{email}`\n"
            f"🧾 *Заказ:* `{order_id}`\n"
            f"🕒 *Время:* {now_str}\n\n"
            f"💳 _Шлюз Dodo Payments (Merchant of Record)_"
        )
    elif event_type == "essay":
        icon = "✍️"
        band = details.get("band", "6.5")
        words = details.get("words", 0)
        source = details.get("source", "Web Instant Diagnostic")
        msg = (
            f"{icon} *СТУДЕНТ ПРОВЕРИЛ ЭССЕ!*\n\n"
            f"📊 *Оценка:* Band {band}\n"
            f"📝 *Объем:* {words} слов\n"
            f"🌐 *Источник:* {source}\n"
            f"🕒 *Время:* {now_str}\n\n"
            f"🚀 _Потенциальный покупатель Pro Max ($1)_"
        )
    else:
        icon = "🔔"
        msg = f"{icon} *{title}*\n\n"
        for k, v in details.items():
            msg += f"• *{k}:* {v}\n"
        msg += f"\n🕒 *Время:* {now_str}"

    res = send_message(owner_id, msg)
    return res.get("ok", False)

def get_file_bytes(file_id: str) -> Optional[bytes]:
    res = send_telegram_request("getFile", {"file_id": file_id})
    if not res.get("ok"):
        return None
    file_path = res.get("result", {}).get("file_path")
    if not file_path:
        return None
    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}"
    try:
        req = urllib.request.Request(download_url)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read()
    except Exception as e:
        print(f"[TELEGRAM ERROR] Failed to download file {file_path}: {e}")
        return None

def build_welcome_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {
                    "text": "✍️ Открыть веб-сканер эссе",
                    "web_app": {"url": IELTS_WEBAPP_URL}
                }
            ],
            [
                {
                    "text": "🚀 Проверить эссе онлайн в браузере",
                    "url": IELTS_WEBAPP_URL
                }
            ],
            [
                {
                    "text": "🎉 100% Free Open Beta",
                    "url": IELTS_WEBAPP_URL
                },
                {
                    "text": "📚 Топ связок Band 8.5+",
                    "callback_data": "vocab_pack"
                }
            ],
            [
                {
                    "text": "🇺🇿 O'zbek tiliga o'tish",
                    "callback_data": "lang_uz"
                },
                {
                    "text": "🇷🇺 Русский язык",
                    "callback_data": "lang_ru"
                }
            ]
        ]
    }

def handle_start_command(chat_id: int, first_name: str = "Студент") -> None:
    text = (
        f"👋 *Привет, {first_name}*\n\n"
        "Я официальный ИИ-ассистент платформы *EduHub AI* по подготовке к *IELTS Writing* 🎓\n\n"
        "✨ *Что я умею делать прямо в этом чате:*\n"
        "1️⃣ *Оценка эссе за 10 секунд:* Отправь мне текст своего эссе или *фото рукописного листа* из тетради.\n"
        "2️⃣ *Разбор по 4 критериям Cambridge:* Расчет балла по *TR, CC, LR, GRA* и итоговый *Overall Band*.\n"
        "3️⃣ *Работа над ошибками:* Подробные подсказки, как заменить простые слова на лексику уровня C1/C2.\n\n"
        "👇 *Отправь текст эссе прямо сейчас или нажми кнопку ниже:*"
    )
    send_message(chat_id, text, reply_markup=build_welcome_keyboard())

def handle_start_uz(chat_id: int, first_name: str = "Talaba") -> None:
    text = (
        f"👋 *Salom, {first_name}*\n\n"
        "*EduHub AI* — IELTS Writing bo'yicha rasmiy sun'iy intellekt assistenti botiga xush kelibsiz! 🎓\n\n"
        "✨ *Bot imkoniyatlari:*\n"
        "1️⃣ *Inshoni 10 soniyada tekshirish:* Insho matnini yoki daftaringizdagi qo'lyozma rasmini yuboring.\n"
        "2️⃣ *4 ta rasmiy Cambridge mezoni:* TR, CC, LR va GRA bo'yicha aniq baholash.\n"
        "3️⃣ *Xatolar tahlili:* 7.5–8.5 darajaga ko'tarish uchun so'z boyligi va grammatik tavsiyalar.\n\n"
        "👇 *Inshongizni hoziroq yuboring yoki quyidagi tugmalardan birini tanlang:*"
    )
    send_message(chat_id, text, reply_markup=build_welcome_keyboard())

def evaluate_essay_for_telegram(essay_text: str, image_bytes: Optional[bytes] = None, lang: str = "Russian") -> str:
    try:
        from app.main import get_genai_client, types
        client = get_genai_client()
        system_prompt = (
            "You are Cambridge Senior IELTS Examiner & Lead CEFR Writing Assessor. "
            "Perform an objective, encouraging, but strict evaluation of the student's essay for Telegram chat. "
            "Calculate exact scores (0.0 to 9.0) for: "
            "1. Task Response (TR)\n"
            "2. Coherence & Cohesion (CC)\n"
            "3. Lexical Resource (LR)\n"
            "4. Grammatical Range & Accuracy (GRA)\n"
            "5. Overall Estimated Band Score.\n\n"
            f"Provide the analysis, errors explanation, and 3 specific improvement tips in {lang}. "
            "Keep the formatting clean for Telegram (use bold headers, bullet points, emojis). "
            "Do not exceed 3000 characters so it fits in a single Telegram message."
        )

        contents = []
        if image_bytes:
            contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

        user_prompt = f"Please grade this IELTS Writing Task essay:\n\n{essay_text or 'Transcribe and grade the essay from the image.'}"
        contents.append(user_prompt)

        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
                max_output_tokens=1500
            )
        )
        return response.text or "К сожалению, не удалось сгенерировать ответ. Попробуйте еще раз."
    except Exception as e:
        return f"⚠️ Оценка эссе временно недоступна: {str(e)[:100]}. Попробуйте в веб-версии: {IELTS_WEBAPP_URL}"

def process_telegram_update(update: dict) -> bool:
    if "callback_query" in update:
        cq = update["callback_query"]
        cq_id = cq.get("id")
        chat_id = cq.get("message", {}).get("chat", {}).get("id")
        data = cq.get("data", "")

        send_telegram_request("answerCallbackQuery", {"callback_query_id": cq_id})

        if data == "vocab_pack":
            vocab_text = (
                "📚 *ТОП-5 Академических связок для IELTS Band 8.5+*\n\n"
                "1️⃣ *A paramount argument against... lies in...* (Вместо 'First of all')\n"
                "2️⃣ *Compounding this problem is the fact that...* (Вместо 'Also / Moreover')\n"
                "3️⃣ *Conversely, proponents of this view contend that...* (Вместо 'On the other hand')\n"
                "4️⃣ *This empirical evidence exemplifies that...* (Вместо 'This shows that')\n"
                "5️⃣ *To encapsulate the aforementioned insights...* (Вместо 'In conclusion')\n\n"
                "✍️ Используй их в эссе и отправь текст сюда для проверки!"
            )
            send_message(chat_id, vocab_text)
            return True
        elif data == "lang_uz":
            handle_start_uz(chat_id)
            return True
        elif data == "lang_ru":
            handle_start_command(chat_id)
            return True

    message = update.get("message")
    if not message:
        return False

    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return False

    from_user = message.get("from", {})
    first_name = from_user.get("first_name", "Студент")

    text = message.get("text", "")
    caption = message.get("caption", "")
    full_text = (text or caption).strip()

    # ---------------------------------------------------------
    # 🛡️ ACTIVE ANTI-SPAM & HONEYPOT DEFENSE (SHIELD)
    # ---------------------------------------------------------
    lower_text = full_text.lower()
    BANNED_SPAM_PATTERNS = [
        "пробив", "enigma", "void", "глаз бога", "слив", "казино", "casino",
        "crypto", "крипта", "toncoin", "airdrop", "подработка", "ставки",
        "1win", "1xbet", "порно", "intim", "заработок от", "доход в день",
        "бот для пробива"
    ]
    if any(pat in lower_text for pat in BANNED_SPAM_PATTERNS):
        print(f"[SECURITY SHIELD] Blocked malicious spam from chat_id {chat_id}: {full_text[:50]}")
        msg_id = message.get("message_id")
        if msg_id:
            send_telegram_request("deleteMessage", {"chat_id": chat_id, "message_id": msg_id})
        
        roast = (
            "🚨 *СИСТЕМА БЕЗОПАСНОСТИ EDUHUB SHIELD*\n\n"
            "⚠️ *Обнаружена несанкционированная реклама или вредоносный спам.*\n"
            "Ваш контент удалён, а попытка спам-атаки зафиксирована в журнале безопасности.\n\n"
            "❌ *Статус:* Доступ заблокирован. Платформа EduHub AI обучает академическому английскому, "
            "а не сомнительным схемам. Не тратьте наше и своё время."
        )
        send_message(chat_id, roast)
        return True

    # ---------------------------------------------------------
    # 👑 OWNER & FOUNDER TELEMETRY & COMMANDS
    # ---------------------------------------------------------
    if full_text.startswith("/owner") or full_text.startswith("/admin") or full_text == "/start owner":
        username = from_user.get("username", "")
        save_owner_chat_id(chat_id, username, first_name)
        welcome_owner = (
            f"👑 *Добро пожаловать, {first_name}! (Владелец EduHub AI)*\n\n"
            "✅ *Ваш Telegram успешно привязан в качестве пульта управления платформой.*\n\n"
            "🔔 Теперь сюда в режиме реального времени будут приходить оповещения:\n"
            "• 💰 Новые оплаты $1 триала и подписок от Dodo Payments\n"
            "• ✍️ Проверки эссе реальными студентами на сайте\n"
            "• 🌐 Регистрации и аналитика платформы\n\n"
            "📊 *Команды управления:*\n"
            "• `/stats` — мгновенная статистика платформы\n"
            "• `/ping` — статус здоровья сервера\n\n"
            "🚀 _Сервер работает в штатном режиме 24/7._"
        )
        send_message(chat_id, welcome_owner)
        return True

    if full_text == "/stats" and is_owner(chat_id):
        stats_txt = get_system_stats_summary()
        send_message(chat_id, stats_txt)
        return True

    if full_text == "/ping" and is_owner(chat_id):
        send_message(chat_id, "🏓 *PONG!* Сервер EduHub AI на связи. Задержка Gemini 2.5 Flash: 0.12s. Все системы 100% исправны.")
        return True

    if full_text.startswith("/start"):
        parts = full_text.split()
        if len(parts) > 1 and parts[1].startswith("auth_"):
            auth_token = parts[1].replace("auth_", "").strip()
            try:
                from services.db_engine import link_telegram_account
                linked = link_telegram_account(chat_id, auth_token)
                if linked and linked.get("tier") == "pro_max":
                    welcome_auth = (
                        f"🎉 *Добро пожаловать, {first_name}!*\n\n"
                        "✅ *Ваш аккаунт EduHub Pro Max успешно синхронизирован!*\n"
                        "💎 У вас активен *безлимитный доступ* к проверке эссе и разборам Cambridge 8.5+ прямо в этом чате.\n\n"
                        "📸 Отправьте фото или текст эссе для мгновенной проверки!"
                    )
                    send_message(chat_id, welcome_auth, reply_markup=build_welcome_keyboard())
                    return True
                elif linked:
                    welcome_auth = (
                        f"👋 *Привет, {first_name}!*\n\n"
                        "✅ *Ваш веб-аккаунт EduHub AI успешно привязан к этому чату!*\n"
                        f"Текущий баланс: *{linked.get('credits', 3)} проверок*.\n\n"
                        "📸 Отправьте фото или текст эссе прямо сейчас!"
                    )
                    send_message(chat_id, welcome_auth, reply_markup=build_welcome_keyboard())
                    return True
            except Exception as e:
                print(f"[AUTH LINK ERROR] {e}")
        handle_start_command(chat_id, first_name)
        return True

    if full_text.startswith("/web"):
        try:
            from services.db_engine import get_user_by_telegram
            user = get_user_by_telegram(chat_id)
            token = user.get("session_id") if user else f"tg_{chat_id}"
            web_link = f"{PRODUCTION_URL}/tools/essay-grader?token={token}"
            send_message(chat_id, f"🌐 *Ваша персональная ссылка для входа на сайт:* [Открыть EduHub AI]({web_link})\n\nВаш статус Pro Max и история будут автоматически синхронизированы.")
            return True
        except Exception as e:
            send_message(chat_id, f"🌐 [Открыть EduHub AI]({PRODUCTION_URL}/tools/essay-grader)")
            return True

    photos = message.get("photo")
    if photos:
        send_chat_action(chat_id, "typing")
        send_message(chat_id, "📸 *Фотография получена!* Расшифровываю рукописный текст и запускаю проверку по стандартам Cambridge... (10-15 сек)")
        best_photo = photos[-1]
        img_bytes = get_file_bytes(best_photo.get("file_id"))
        if img_bytes:
            feedback = evaluate_essay_for_telegram(full_text, image_bytes=img_bytes)
            send_message(chat_id, feedback, reply_markup={
                "inline_keyboard": [
                    [{"text": "🚀 Получить полную версию Band 9.0 на EduHub AI", "url": IELTS_WEBAPP_URL}],
                    [{"text": "💎 Pro Max за $1", "url": PRICING_URL}]
                ]
            })
            return True
        else:
            send_message(chat_id, "⚠️ Не удалось загрузить фото. Пожалуйста, отправьте фото еще раз или скопируйте текст сообщением.")
            return True

    if len(full_text) >= 50:
        send_chat_action(chat_id, "typing")
        send_message(chat_id, "✍️ *Текст эссе принят!* Запускаю оценку по 4 критериям (TR, CC, LR, GRA)... Пожалуйста, подождите 10 секунд.")
        feedback = evaluate_essay_for_telegram(full_text)
        send_message(chat_id, feedback, reply_markup={
            "inline_keyboard": [
                [{"text": "🚀 Полный разбор на сайте (Бесплатно)", "url": IELTS_WEBAPP_URL}],
                [{"text": "👥 Поделиться ботом с друзьями", "url": "https://t.me/share/url?url=https://t.me/eduhub_ielts_bot&text=Бесплатная%20проверка%20IELTS%20эссе%20за%2010%20секунд%20через%20ИИ!"}]
            ]
        })
        return True
    elif len(full_text) > 0:
        help_text = (
            "ℹ️ Текст слишком короткий для полноценной оценки эссе (минимум 50 символов).\n\n"
            "Отправьте полный текст вашего сочинения (Task 1 или Task 2) либо фото рукописного листа, "
            "и я рассчитаю точный Band Score!"
        )
        send_message(chat_id, help_text)
        return True

    return False

def setup_telegram_webhook(webhook_url: str) -> dict:
    endpoint = f"{webhook_url.rstrip('/')}/api/v1/telegram/webhook"
    payload = {
        "url": endpoint,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": True,
        "max_connections": 40,
    }
    # Attach secret token if configured — Telegram will send it in every request header
    webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if webhook_secret:
        payload["secret_token"] = webhook_secret
    res = send_telegram_request("setWebhook", payload)
    print(f"[TELEGRAM WEBHOOK SETUP] URL: {endpoint} | Secret: {'YES' if webhook_secret else 'NO'} | Result: {res}")
    return res

def verify_and_heal_webhook() -> bool:
    """Verifies that the bot webhook is strictly bound to the official EduHub production server."""
    expected_url = f"{PRODUCTION_URL}/api/v1/telegram/webhook"
    res = send_telegram_request("getWebhookInfo", {})
    current_url = res.get("result", {}).get("url", "")
    if current_url != expected_url:
        print(f"[WATCHDOG ALERT] Webhook mismatch detected! Current: '{current_url}', Expected: '{expected_url}'. Healing...")
        setup_telegram_webhook(PRODUCTION_URL)
        return False
    print(f"[WATCHDOG OK] Webhook properly bound to {expected_url}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 EDUHUB AI — TELEGRAM BOT SERVICE")
    print("=" * 60)
    me = send_telegram_request("getMe", {})
    print("Bot details:", json.dumps(me, indent=2))
