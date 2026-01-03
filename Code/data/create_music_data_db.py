import sqlite3

# -----------------------------
# Config
# -----------------------------
DB_PATH = "data/clean_music_data.db"

# -----------------------------
# Connect / Create DB
# -----------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# 1. Audio features table
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS audio_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,          -- nanoseconds
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
    timestamp INTEGER NOT NULL,          -- nanoseconds
    device_id INTEGER,
    channel INTEGER,
    note INTEGER,
    velocity INTEGER,
    cc_number INTEGER,
    cc_value INTEGER,
    program_number INTEGER,
    type TEXT
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

# -----------------------------
# Example device insertion
# -----------------------------
devices = [
    "Strymon Cloudburst",
    "Strymon Timeline",
    "Chase Bliss Mood MK II",
    "Chase Bliss Blooper",
    "Chase Bliss Lost And Found",
    "Source Audio EQ2",
    "GT 1000 Core"
]

for device in devices:
    cursor.execute("INSERT OR IGNORE INTO midi_devices (name) VALUES (?)", (device,))

# -----------------------------
# Commit and close
# -----------------------------
conn.commit()
conn.close()

print(f"Clean database created at {DB_PATH} with 3 tables: audio_features, midi_events, midi_devices")
