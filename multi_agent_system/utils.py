import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from logger_setup import logger

SNAPSHOT_FILE = "debate_state_snapshots.jsonl"

def save_state_snapshot(state):
    """Append a JSON-line snapshot of full state for audit."""
    with open(SNAPSHOT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(state, ensure_ascii=False, default=str) + "\n")

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def tokenize(text):
    text = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return [t for t in text.split() if len(t) > 2]

STOPWORDS = {
    "the","and","for","with","are","was","that","this","from","have","has","but","not",
    "your","about","which","their","they","been","were","will","would","could","should",
    "like","such","is","in","on","of","to","a","an"
}

def topic_keywords(topic):
    """Return clean keywords from the topic (remove stopwords)."""
    kws = [t for t in tokenize(topic) if t not in STOPWORDS]
    # if no keywords extracted, fallback to tokens
    return kws or tokenize(topic) or [topic]

def now():
    return datetime.utcnow().isoformat()

def write_final_result(state, filename="final_debate_result.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    logger.info("Wrote final result to %s", filename)
