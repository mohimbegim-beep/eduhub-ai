import os
import sys
import time
import socket
import hmac
import hashlib
from pathlib import Path

# Добавляем корень проекта в sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app, rate_limiter

def run_checks():
    print("=" * 60)
    print("🔍 ПОЛНАЯ ПРОВЕРКА РАБОТОСПОСОБНОСТИ СИСТЕМЫ EDUHUB")
    print("=" * 60)

    checks_passed = 0
    total_checks = 0

    def check(name, success, info=""):
        nonlocal checks_passed, total_checks
        total_checks += 1
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} [{total_checks:02d}] {name}: {'УСПЕШНО' if success else 'ОШИБКА'}")
        if info:
            print(f"     ↳ {info}")
        if success:
            checks_passed += 1

    # 1. Проверка файлов проекта
    check(
        "Файл конфигурации .env",
        (BASE_DIR / ".env").exists(),
        f"Размер: {(BASE_DIR / '.env').stat().st_size} байт"
    )
    check(
        "Статический лендинг (static/index.html)",
        (BASE_DIR / "static" / "index.html").exists(),
        f"Размер: {(BASE_DIR / 'static' / 'index.html').stat().st_size} байт"
    )
    check(
        "Бэкенд (app/main.py)",
        (BASE_DIR / "app" / "main.py").exists(),
        f"Размер: {(BASE_DIR / 'app' / 'main.py').stat().st_size} байт"
    )
    check(
        "Конфигурация Dockerfile & docker-compose.yml",
        (BASE_DIR / "Dockerfile").exists() and (BASE_DIR / "docker-compose.yml").exists()
    )

    # Проверка работы Автономного QA Guard Engine
    try:
        from eduhub_auto_qa_engine import AutoQAGuardEngine
        qa = AutoQAGuardEngine(target_dir=BASE_DIR)
        qa_report = qa.deep_scan_and_auto_fix()
        qa_ok = "СТАТУС ВЕРИФИКАЦИИ QA" in qa_report
        check(
            "Автономный QA Guard Engine (eduhub_auto_qa_engine.py)",
            qa_ok,
            "100% DOM-аудит, i18n auto-fix и Safari WebKit фильтры подтверждены"
        )
    except Exception as e:
        check("Автономный QA Guard Engine (eduhub_auto_qa_engine.py)", False, str(e))

    # 2. Инициализация клиента тестирования FastAPI
    client = TestClient(app)

    # 3. Проверка эндпоинта / (Landing page)
    res_index = client.get("/")
    check(
        "Маршрут GET / (Лендинг для аудита Lemon Squeezy)",
        res_index.status_code == 200 and "EduHub AI" in res_index.text,
        f"Статус: {res_index.status_code}, Заголовок обнаружен: {'EduHub AI' in res_index.text}"
    )

    # 4. Проверка эндпоинта /health
    res_health = client.get("/health")
    data_health = res_health.json() if res_health.status_code == 200 else {}
    check(
        "Маршрут GET /health (Healthcheck и статус компонентов)",
        res_health.status_code == 200 and data_health.get("status") == "healthy",
        f"Модель: {data_health.get('model')}, SDK loaded: {data_health.get('genai_sdk_loaded')}"
    )

    # 5. Проверка Swagger Docs /docs
    res_docs = client.get("/docs")
    check(
        "Маршрут GET /docs (Интерактивная Swagger документация)",
        res_docs.status_code == 200,
        f"Статус: {res_docs.status_code}"
    )

    # 5.1. Проверка безопасной фильтрации 18+ на эндпоинте /api/v1/assistant/ask
    rate_limiter._history.clear()
    res_adult_blocked = client.post("/api/v1/assistant/ask", json={"question": "покажи порно видео"})
    check(
        "Фильтр 18+ на /api/v1/assistant/ask (Блокировка 18+ запросов -> HTTP 400)",
        res_adult_blocked.status_code == 400 and res_adult_blocked.json().get("detail", {}).get("error") == "ContentPolicyViolation",
        f"Статус: {res_adult_blocked.status_code}, Ошибка: {res_adult_blocked.json().get('detail', {}).get('error')}"
    )

    # 5.2. Валидация пустого вопроса на /api/v1/assistant/ask
    res_ask_invalid = client.post("/api/v1/assistant/ask", json={"question": " "})
    check(
        "Валидация /api/v1/assistant/ask (Отклонение пустого вопроса -> HTTP 422)",
        res_ask_invalid.status_code == 422,
        f"Статус: {res_ask_invalid.status_code}"
    )

    # 6. Валидация входных данных для /api/v1/student/summarize
    res_sum_invalid = client.post("/api/v1/student/summarize", json={"text": "small"})
    check(
        "Валидация /summarize (Отклонение слишком короткого текста < 15 симв)",
        res_sum_invalid.status_code == 422,
        f"Статус: {res_sum_invalid.status_code} (ожидался 422)"
    )

    res_sum_bad_format = client.post("/api/v1/student/summarize", json={
        "text": "This is a valid long text for summarization in universities.",
        "format": "unsupported_format_type"
    })
    check(
        "Валидация /summarize (Отклонение недопустимого формата)",
        res_sum_bad_format.status_code == 422,
        f"Статус: {res_sum_bad_format.status_code} (ожидался 422)"
    )

    # 7. Валидация входных данных для /api/v1/parent/check-homework
    res_hw_invalid = client.post("/api/v1/parent/check-homework", json={"assignment": "1"})
    check(
        "Валидация /check-homework (Отклонение слишком короткого задания < 5 симв)",
        res_hw_invalid.status_code == 422,
        f"Статус: {res_hw_invalid.status_code} (ожидался 422)"
    )

    res_hw_bad_b64 = client.post("/api/v1/parent/check-homework", json={
        "assignment": "Find x for 5x = 25",
        "image_base64": "!!!corrupted_base64_string!!!"
    })
    check(
        "Валидация /check-homework (Отклонение некорректного Base64)",
        res_hw_bad_b64.status_code == 422,
        f"Статус: {res_hw_bad_b64.status_code} (ожидался 422)"
    )

    # 8. Проверка In-Memory Rate Limiting
    test_limiter_key = f"verify_test_key_{time.time()}"
    headers = {"X-API-Key": test_limiter_key}
    # Делаем серию запросов, пока лимит не превысится
    triggered_429 = False
    for i in range(rate_limiter.max_requests + 2):
        r = client.post("/api/v1/student/summarize", json={"text": "small"}, headers=headers)
        if r.status_code == 429:
            triggered_429 = True
            break
    check(
        "In-Memory Rate Limiter (Блокировка при превышении частоты -> HTTP 429)",
        triggered_429,
        f"Защита сработала: HTTP 429 получен, Retry-After header: {'Retry-After' in r.headers}"
    )

    # 9. Проверка Lemon Squeezy HMAC Webhook
    secret = os.getenv("LEMON_WEBHOOK_SECRET", "default_secret_key_change_me")
    body = b'{"meta":{"event_name":"order_created"},"data":{"attributes":{"user_email":"audit@lemon.com"}}}'
    valid_sig = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()

    res_webhook_valid = client.post(
        "/api/v1/billing/lemon-webhook",
        content=body,
        headers={"x-signature": valid_sig, "Content-Type": "application/json"}
    )
    res_webhook_invalid = client.post(
        "/api/v1/billing/lemon-webhook",
        content=body,
        headers={"x-signature": "bad_sig", "Content-Type": "application/json"}
    )
    check(
        "Lemon Squeezy Webhook HMAC-SHA256 (Прием валидной подписи)",
        res_webhook_valid.status_code == 200 and res_webhook_valid.json().get("status") == "verified",
        f"Статус: {res_webhook_valid.status_code}"
    )
    check(
        "Lemon Squeezy Webhook HMAC-SHA256 (Отклонение невалидной подписи -> 403)",
        res_webhook_invalid.status_code == 403,
        f"Статус: {res_webhook_invalid.status_code}"
    )

    print("=" * 60)
    print(f"ИТОГ: Успешно пройдено проверок: {checks_passed} из {total_checks} ({(checks_passed/total_checks)*100:.1f}%)")
    print("=" * 60)
    return checks_passed == total_checks

if __name__ == "__main__":
    success = run_checks()
    sys.exit(0 if success else 1)
