import sqlite3
import sounddevice as sd
import numpy as np
import time
import queue
import threading
import os

# -----------------------------
# Config
# -----------------------------
DB_PATH = "data/clean_music_data.db"  # your new DB
DEVICE_INDEX = 1
CHANNEL_INDEX = 1
SAMPLE_RATE = 48000
BLOCKSIZE = 1024
BATCH_SIZE = 50  # number of rows per commit
MIN_DB_FOR_WRITING = -45

# -----------------------------
# Queue for DB writes
# -----------------------------
data_queue = queue.Queue()

# -----------------------------
# DB writer thread
# -----------------------------
def db_writer():
    conn = sqlite3.connect(DB_PATH, timeout=5.0)
    cursor = conn.cursor()
    
    # WAL mode (only needed once, will silently succeed if already set)
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.OperationalError:
        print("[DB] WAL mode could not be set. Make sure no other processes are locking the DB.")

    buffer = []
    while True:
        item = data_queue.get()
        if item is None:  # sentinel to stop thread
            if buffer:
                cursor.executemany("""
                    INSERT INTO audio_features (
                        timestamp, rms_db, rms_delta, centroid, rolloff,
                        flatness, low, mid, high, spectral_flux, onset_strength
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, buffer)
                conn.commit()
            break

        buffer.append(item)
        if len(buffer) >= BATCH_SIZE:
            cursor.executemany("""
                INSERT INTO audio_features (
                    timestamp, rms_db, rms_delta, centroid, rolloff,
                    flatness, low, mid, high, spectral_flux, onset_strength
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, buffer)
            conn.commit()
            buffer.clear()
    
    conn.close()
    print("[DB] Writer stopped.")

threading.Thread(target=db_writer, daemon=True).start()

# -----------------------------
# Audio callback
# -----------------------------
def audio_callback(indata, frames, time_info, status):
    y = indata[:, CHANNEL_INDEX]
    eps = 1e-8

    # RMS
    rms = np.sqrt(np.mean(y**2))
    prev_rms = getattr(audio_callback, "prev_rms", rms)
    rms_delta = rms - prev_rms
    audio_callback.prev_rms = rms
    rms_db = 20 * np.log10(rms + eps)

    # FFT-based features
    fft = np.fft.rfft(y)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(len(y), 1 / SAMPLE_RATE)
    mag_sum = np.sum(mag) + eps

    centroid = np.sum(freqs * mag) / mag_sum
    cumulative = np.cumsum(mag)
    rolloff = freqs[np.where(cumulative >= 0.85 * cumulative[-1])[0][0]]
    flatness = np.exp(np.mean(np.log(mag + eps))) / (np.mean(mag) + eps)
    low = np.mean(mag[(freqs >= 20) & (freqs < 250)])
    mid = np.mean(mag[(freqs >= 250) & (freqs < 4000)])
    high = np.mean(mag[(freqs >= 4000)])
    prev_mag = getattr(audio_callback, "prev_mag", mag)
    spectral_flux = np.sqrt(np.mean((mag - prev_mag) ** 2))
    audio_callback.prev_mag = mag

    onset_strength = max(0.0, rms_delta)
    timestamp = time.time_ns()  # MATCHES MIDI timestamps

    if rms_db > MIN_DB_FOR_WRITING:  # threshold for logging
        data_queue.put((
        int(timestamp),
        float(rms_db),
        float(rms_delta),
        float(centroid),
        float(rolloff),
        float(flatness),
        float(low),
        float(mid),
        float(high),
        float(spectral_flux),
        float(onset_strength)
))

    print(f"[DB] Queued RMS:{rms_db:.1f} Centroid:{centroid:.1f}")

# -----------------------------
# Start audio stream
# -----------------------------
stream = sd.InputStream(
    device=DEVICE_INDEX,
    channels=2,
    samplerate=SAMPLE_RATE,
    blocksize=BLOCKSIZE,
    callback=audio_callback
)
stream.start()

print("[Sender] Audio feature logging started (Ctrl+C to stop)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stream.stop()
    stream.close()
    data_queue.put(None)  # signal DB thread to stop
    time.sleep(0.5)
    print("[Sender] Stopped.")
