"""Best scores live in the current Windows user's application data folder."""
import json
import os
from pathlib import Path

LEVELS = {'简单': 180, '普通': 125, '困难': 80}


def score_path():
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'SnakeWin11' / 'scores.json'


def load_scores(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        return {level: value for level in LEVELS
                if type(value := data.get(level)) is int and value >= 0}
    except (OSError, ValueError, AttributeError):
        return {}


def save_scores(path, scores):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(scores, ensure_ascii=False), encoding='utf-8')
    temporary.replace(path)
