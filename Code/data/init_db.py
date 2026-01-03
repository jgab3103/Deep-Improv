# init_wal.py
import sqlite3

DB_PATH = "data/clean_music_data.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

print("WAL mode enabled:", cursor.fetchone())

conn.close()
