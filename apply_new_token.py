import requests, json

NEW_TOKEN = '8821505674:AAHM7PWcfC21jcBAYsUNavNnGLQtVYWP1fQ'
OWNER_ID  = 7905536993
PROD_URL  = 'https://eduhub-ai.onrender.com'

secret = None
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('TELEGRAM_WEBHOOK_SECRET='):
            secret = line.split('=',1)[1].strip()

# ── 1. Update .env ────────────────────────────────────────────────────────────
content = open('.env', 'r', encoding='utf-8').read()
lines = []
for l in content.splitlines():
    if l.startswith('TELEGRAM_BOT_TOKEN='):
        lines.append(f'TELEGRAM_BOT_TOKEN={NEW_TOKEN}')
    else:
        lines.append(l)
with open('.env', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('[1] .env updated with new token')

# ── 2. Register webhook with secret ──────────────────────────────────────────
payload = {
    'url': f'{PROD_URL}/api/v1/telegram/webhook',
    'allowed_updates': ['message', 'callback_query'],
    'drop_pending_updates': True,
    'max_connections': 40,
    'secret_token': secret
}
r = requests.post(f'https://api.telegram.org/bot{NEW_TOKEN}/setWebhook', json=payload, timeout=10)
print('[2] Webhook set:', r.json())

# ── 3. Verify webhook ─────────────────────────────────────────────────────────
r2 = requests.get(f'https://api.telegram.org/bot{NEW_TOKEN}/getWebhookInfo', timeout=10)
info = r2.json().get('result', {})
print('[3] Webhook URL:', info.get('url'))
print('[3] Pending:', info.get('pending_update_count'))

# ── 4. Send welcome message to owner ─────────────────────────────────────────
welcome = (
    "Mohimbegim! Token successfully replaced.\n\n"
    "A_ToolsX has been permanently cut off — old token is dead.\n\n"
    "Please add the new token to Render:\n"
    f"TELEGRAM_BOT_TOKEN = {NEW_TOKEN}\n\n"
    "Then type /owner to activate your owner dashboard."
)
r3 = requests.post(f'https://api.telegram.org/bot{NEW_TOKEN}/sendMessage', json={
    'chat_id': OWNER_ID,
    'text': welcome
}, timeout=10)
print('[4] Owner message sent:', r3.json().get('ok'))
