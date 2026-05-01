"""SQLite cache for character query results."""
import os, sqlite3, time, json, threading

_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.normpath(os.path.join(_HERE, "..", "char_cache.sqlite"))
TTL_SEC = 3600  # 1 hour

_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.execute(
        """CREATE TABLE IF NOT EXISTS characters(
            server_id    INTEGER NOT NULL,
            character_id TEXT    NOT NULL,
            fetched_at   INTEGER NOT NULL,
            source       TEXT,
            data_json    TEXT    NOT NULL,
            PRIMARY KEY(server_id, character_id))"""
    )
    return c


def get(server_id, character_id):
    with _lock, _conn() as c:
        row = c.execute(
            "SELECT fetched_at, source, data_json FROM characters "
            "WHERE server_id=? AND character_id=?",
            (server_id, character_id),
        ).fetchone()
    if not row:
        return None
    return {"fetchedAt": row[0], "source": row[1], "data": json.loads(row[2])}


def put(server_id, character_id, source, data):
    payload = json.dumps(data, ensure_ascii=False)
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO characters"
            "(server_id, character_id, fetched_at, source, data_json) "
            "VALUES (?,?,?,?,?)",
            (server_id, character_id, int(time.time()), source, payload),
        )
        c.commit()
