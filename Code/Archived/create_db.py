import sqlite3

DB_FILE = "music_data.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# -----------------------------
# 1. Audio features table
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    rms_db REAL,
    rms_delta REAL,
    centroid REAL,
    rolloff REAL,
    flatness REAL,
    low REAL,
    mid REAL,
    high REAL,
    spectral_flux REAL,
    onset_strength REAL
)
""")

# -----------------------------
# 2. MIDI events table
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS midi_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    device_id INTEGER,
    channel INTEGER,
    note INTEGER,
    velocity INTEGER,
    type TEXT,
    FOREIGN KEY(device_id) REFERENCES midi_devices(id)
)
""")

# -----------------------------
# 3. MIDI devices lookup
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS midi_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

conn.commit()
conn.close()
print("Database and tables initialized.")
