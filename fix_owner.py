import requests

token = None
secret = None
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('TELEGRAM_BOT_TOKEN='):
            token = line.split('=',1)[1].strip()
        if line.startswith('TELEGRAM_WEBHOOK_SECRET='):
            secret = line.split('=',1)[1].strip()

# Use getUpdates to find real owner chat_id
r = requests.get(f'https://api.telegram.org/bot{token}/getUpdates?limit=10&offset=-10', timeout=10)
updates = r.json().get('result', [])
print(f'Found {len(updates)} updates')
owner_chat_id = None
for u in updates:
    msg = u.get('message', {})
    chat = msg.get('chat', {})
    frm = msg.get('from', {})
    uname = frm.get('username', '')
    fname = frm.get('first_name', '')
    cid = chat.get('id')
    text = msg.get('text', '')
    print(f"  chat_id={cid}  @{uname}  name={fname}  text={repr(text)}")
    if 'owner' in text.lower() or 'admin' in text.lower():
        owner_chat_id = cid
        print(f"  ^^^ OWNER CANDIDATE: {cid}")

if not updates:
    print("No updates found (webhook may have consumed them)")
    print("Try sending /owner to the bot and re-run this script quickly")

if owner_chat_id:
    print(f"\nReal owner chat_id: {owner_chat_id}")
    # Save it to owner_config.json directly
    import json
    from pathlib import Path
    config_path = Path('data/owner_config.json')
    config_path.parent.mkdir(exist_ok=True)
    existing = {}
    if config_path.exists():
        try:
            existing = json.loads(config_path.read_text(encoding='utf-8'))
        except:
            pass
    existing['owner_chat_id'] = owner_chat_id
    config_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Saved to data/owner_config.json")

    # Now send a test message directly
    r2 = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={
        'chat_id': owner_chat_id,
        'text': 'Mohimbegim! Bot is now secured and working. /owner command is ready.',
        'parse_mode': 'Markdown'
    }, timeout=10)
    print("Direct message result:", r2.json())
