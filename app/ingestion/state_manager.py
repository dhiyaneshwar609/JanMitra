import json
from pathlib import Path
from threading import Lock

STATE_FILE = Path("crawler_state.json")
_state_lock = Lock()


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "current_source": 0,
        "queue": [],
        "visited": [],
        "failed": [],
        "pages_scraped": 0
    }


def save_state(state):
    with _state_lock:
        temp = STATE_FILE.with_suffix(".tmp")

        with open(temp, "w", encoding="utf-8") as f:
            json.dump(
                state,
                f,
                indent=2,
                ensure_ascii=False
            )

        temp.replace(STATE_FILE)