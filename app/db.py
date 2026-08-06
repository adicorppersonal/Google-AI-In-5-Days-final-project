import sqlite3
import csv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "articles.db")
CSV_PATH = os.path.join(BASE_DIR, "articles.csv")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            word_count INTEGER,
            timestamp TEXT,
            query TEXT
        )
    """)
    conn.commit()
    conn.close()

    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "content", "word_count", "timestamp", "query"])

def save_article_to_storage(article: dict, query: str):
    init_db()
    art_id = article.get("id", f"art-{int(datetime.now().timestamp())}")
    title = article.get("title", "")
    content = article.get("content", "")
    word_count = article.get("word_count", len(content.split()))
    timestamp = article.get("timestamp", datetime.utcnow().isoformat())

    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO articles (id, title, content, word_count, timestamp, query)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (art_id, title, content, word_count, timestamp, query))
    conn.commit()
    conn.close()

    # Save to CSV
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["id", "title", "content", "word_count", "timestamp", "query"])
        writer.writerow([art_id, title, content, word_count, timestamp, query])
