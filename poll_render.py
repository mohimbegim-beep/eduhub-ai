import requests, time

for i in range(8):
    try:
        r = requests.get("https://eduhub-ai.onrender.com/health", timeout=12)
        data = r.json()
        uptime = data.get("uptime_seconds", 0)
        status = data.get("status", "?")
        print(f"[{i+1}] uptime={uptime}s status={status}")
        if uptime < 90 and i > 0:
            print(">>> Render restarted! New env vars are active.")
            break
    except Exception as e:
        print(f"[{i+1}] Server offline/restarting: {e}")
    time.sleep(12)

print("Done monitoring.")
