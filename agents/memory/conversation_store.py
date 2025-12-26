import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def save_conversation(user_id, message, response):
    file = DATA_DIR / f"{user_id}.json"

    history = []
    if file.exists():
        history = json.loads(file.read_text())

    history.append({
        "message": message,
        "response": response
    })

    file.write_text(json.dumps(history, indent=2))

def load_conversation(user_id):
    file = DATA_DIR / f"{user_id}.json"
    if file.exists():
        return json.loads(file.read_text())
    return []
