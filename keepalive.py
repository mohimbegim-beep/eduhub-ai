"""
EduHub AI — Локальный скрипт-будильник (Keep-Alive Pinger).
Пингует эндпоинт https://eduhub-ai.onrender.com/health каждые 12 минут,
чтобы Render никогда не засыпал и открывался за 50 мс.
"""
import time
import urllib.request
from datetime import datetime

TARGET_URL = "https://eduhub-ai.onrender.com/health"
INTERVAL_SECONDS = 720  # 12 минут (меньше 15-минутного таймаута Render)

print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск будильника EduHub для {TARGET_URL}")
print(f"Интервал пинга: каждые {INTERVAL_SECONDS // 60} минут. Нажмите Ctrl+C для остановки.\n")

count = 1
while True:
    try:
        req = urllib.request.Request(TARGET_URL, headers={"User-Agent": "EduHub-WakeUp-Agent/1.0"})
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=15) as resp:
            latency = (time.time() - start_time) * 1000
            status_code = resp.getcode()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Пинг #{count}: Статус HTTP {status_code} | Отклик: {latency:.1f} мс — Сервер активен!")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка пинга #{count}: {e}")
    
    count += 1
    time.sleep(INTERVAL_SECONDS)
