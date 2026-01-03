import sounddevice as sd
import numpy as np
from pythonosc import udp_client
import time

# -----------------------------
# CONFIG
# -----------------------------
DEVICE_INDEX = 1        # USB AUDIO CODEC
CHANNEL_INDEX = 1       # <-- CHANGE TO 0 IF NEEDED
SAMPLE_RATE = 48000     # MUST match device
BLOCKSIZE = 1024

OSC_IP = "127.0.0.1"
OSC_PORT = 9001

# -----------------------------
# OSC client
# -----------------------------
client = udp_client.SimpleUDPClient(OSC_IP, OSC_PORT)

# -----------------------------
# Audio callback
# -----------------------------
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

    # Select correct input channel
    y = indata[:, CHANNEL_INDEX]

    # RMS (linear)
    rms = np.sqrt(np.mean(y**2))

    # Smooth RMS
    alpha = 0.2
    prev = getattr(audio_callback, "rms_smooth", 0.0)
    rms_smooth = alpha * rms + (1 - alpha) * prev
    audio_callback.rms_smooth = rms_smooth

    # Convert to dB
    rms_db = 20 * np.log10(rms_smooth + 1e-8)

    # FFT → spectral centroid
    fft = np.fft.rfft(y)
    mag = np.abs(fft)
    centroid = np.sum(mag * np.arange(len(mag))) / (np.sum(mag) + 1e-6)

    # Threshold gate (ignore silence)
    if rms_db > -60:
        print(f"[Sender] RMS: {rms_db:6.1f} dB | Centroid: {centroid:8.1f}")
        client.send_message("/amp", [float(rms_db), float(centroid)])

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
print("[Sender] Audio feature stream started (Ctrl+C to stop)")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stream.stop()
    stream.close()
    print("[Sender] Stopped.")
