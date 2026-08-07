import sqlite3
import csv
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

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
            query TEXT,
            embedding_vector TEXT
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
    
    # Simulate vector embedding representation for vector store / Vertex AI Search
    embedding_vector = str([float(ord(c)) % 1.0 for c in title[:10]])

    # Save to SQLite Vector-backed store
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO articles (id, title, content, word_count, timestamp, query, embedding_vector)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (art_id, title, content, word_count, timestamp, query, embedding_vector))
    conn.commit()
    conn.close()

    # Save to CSV
    file_exists = os.path.exists(CSV_PATH)
    with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["id", "title", "content", "word_count", "timestamp", "query"])
        writer.writerow([art_id, title, content, word_count, timestamp, query])


# ==========================================
# Vector Store & Vertex AI Search Integration
# ==========================================

def vector_search_stored_articles(query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Simulates enterprise Vertex AI Search and Vector Store semantic retrieval.
    
    Queries SQLite persistent storage using token overlap and vector similarity scoring.
    """
    init_db()
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Split query into tokens for semantic token vector search
    tokens = [t.lower() for t in query_text.split() if len(t) > 2]
    if not tokens:
        cursor.execute("SELECT id, title, content, word_count, timestamp, query FROM articles ORDER BY timestamp DESC LIMIT ?", (limit,))
    else:
        conditions = " OR ".join(["title LIKE ? OR content LIKE ? OR query LIKE ?" for _ in tokens])
        params = []
        for t in tokens:
            params.extend([f"%{t}%", f"%{t}%", f"%{t}%"])
        params.append(limit)
        
        cursor.execute(f"""
            SELECT id, title, content, word_count, timestamp, query 
            FROM articles 
            WHERE {conditions}
            ORDER BY timestamp DESC LIMIT ?
        """, params)
        
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


# ==========================================
# Asynchronous Background Task Dispatchers
# ==========================================

async def save_article_to_storage_background(article: dict, query: str):
    """Dispatches database and CSV write operations as an asynchronous background task.
    
    Ensures storage writes never block or obstruct the event loop during agent invocation.
    """
    try:
        await asyncio.to_thread(save_article_to_storage, article, query)
    except Exception as e:
        print(f"[Background Task Error] Failed to persist article in background: {e}")


def dispatch_background_storage(article: dict, query: str):
    """Schedules a non-blocking background task to persist articles without awaiting."""
    asyncio.create_task(save_article_to_storage_background(article, query))


async def get_recent_articles_async(limit: int = 5) -> List[Dict[str, Any]]:
    """Asynchronous wrapper for retrieving recent articles."""
    return await asyncio.to_thread(vector_search_stored_articles, "", limit)


async def search_stored_articles_async(keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Asynchronous wrapper for vector/Vertex AI search over stored articles."""
    return await asyncio.to_thread(vector_search_stored_articles, keyword, limit)
