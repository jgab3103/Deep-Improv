import mido
import sqlite3
import time
import signal
import sys

# -----------------------------
# Config
# -----------------------------
DB_PATH = "data/clean_music_data.db"
PORT_NAME = "USB MIDI Interface"
BATCH_SIZE = 3

# -----------------------------
# Graceful shutdown handling
# -----------------------------
running = True

def shutdown_handler(sig, frame):
    global running
    print("\nShutting down cleanly...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# -----------------------------
# Helpers
# -----------------------------
def now_ns():
    # MUST match audio timestamping
    return time.time_ns()

def get_or_create_device(cursor, device_name):
    cursor.execute(
        "INSERT OR IGNORE INTO midi_devices (name) VALUES (?)",
        (device_name,)
    )
    cursor.execute(
        "SELECT id FROM midi_devices WHERE name = ?",
        (device_name,)
    )
    return cursor.fetchone()[0]

# -----------------------------
# Open DB (WAL-safe)
# -----------------------------
conn = sqlite3.connect(
    DB_PATH,
    timeout=5.0,
)
cursor = conn.cursor()

# Enable WAL mode (critical for concurrent writers)
cursor.execute("PRAGMA journal_mode=WAL;")
cursor.execute("PRAGMA synchronous=NORMAL;")

device_id = get_or_create_device(cursor, PORT_NAME)
conn.commit()

print(f"Recording MIDI from '{PORT_NAME}' (device_id={device_id})")

# -----------------------------
# MIDI listener
# -----------------------------
event_count = 0

with mido.open_input(PORT_NAME) as inport:
    while running:
        for msg in inport.iter_pending():
            ts = now_ns()

            cursor.execute("""
                INSERT INTO midi_events (
                    timestamp,
                    device_id,
                    channel,
                    note,
                    velocity,
                    cc_number,
                    cc_value,
                    program_number,
                    type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts,
                device_id,
                getattr(msg, "channel", None),
                getattr(msg, "note", None),
                getattr(msg, "velocity", None),
                getattr(msg, "control", None),
                getattr(msg, "value", None),
                getattr(msg, "program", None),
                msg.type
            ))

            event_count += 1

            if event_count >= BATCH_SIZE:
                print("COMMITTING")
                conn.commit()
                event_count = 0

            print(ts, msg)

        time.sleep(0.001)  # prevents CPU spin

# -----------------------------
# Final commit & cleanup
# -----------------------------
conn.commit()
conn.close()
print("MIDI recording stopped cleanly.")
