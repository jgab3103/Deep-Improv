import sounddevice as sd
import numpy as np
from pythonosc import udp_client
import time

# -----------------------------
# CONFIG
# -----------------------------
DEVICE_INDEX = 1
CHANNEL_INDEX = 1       # change to 0 if needed
SAMPLE_RATE = 48000
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

    y = indata[:, CHANNEL_INDEX]
    eps = 1e-8

    # -----------------------------
    # ENERGY FEATURES
    # -----------------------------
    rms = np.sqrt(np.mean(y**2))
    rms_db = 20 * np.log10(rms + eps)

    prev_rms = getattr(audio_callback, "prev_rms", rms)
    rms_delta = rms - prev_rms
    audio_callback.prev_rms = rms

    # -----------------------------
    # FFT
    # -----------------------------
    fft = np.fft.rfft(y)
    mag = np.abs(fft)
    freqs = np.fft.rfftfreq(len(y), 1 / SAMPLE_RATE)

    mag_sum = np.sum(mag) + eps

    # -----------------------------
    # SPECTRAL FEATURES
    # -----------------------------
    centroid = np.sum(freqs * mag) / mag_sum

    cumulative = np.cumsum(mag)
    rolloff = freqs[np.where(cumulative >= 0.85 * cumulative[-1])[0][0]]

    flatness = np.exp(np.mean(np.log(mag + eps))) / (np.mean(mag) + eps)

    # Band energies
    low = np.mean(mag[(freqs >= 20) & (freqs < 250)])
    mid = np.mean(mag[(freqs >= 250) & (freqs < 4000)])
    high = np.mean(mag[(freqs >= 4000)])

    # -----------------------------
    # TEMPORAL / CHANGE FEATURES
    # -----------------------------
    prev_mag = getattr(audio_callback, "prev_mag", mag)
    spectral_flux = np.sqrt(np.mean((mag - prev_mag) ** 2))
    audio_callback.prev_mag = mag

    onset_strength = max(0.0, rms_delta)

    # -----------------------------
    # TIMESTAMP
    # -----------------------------
    timestamp = time.time_ns()

    # -----------------------------
    # SEND (gate silence)
    # -----------------------------
    if rms_db > -60:
        features = [
            timestamp,
            rms_db,
            rms_delta,
            centroid,
            rolloff,
            flatness,
            low,
            mid,
            high,
            spectral_flux,
            onset_strength,
        ]

        print(
            f"[Sender] dB:{rms_db:6.1f} "
            f"Cent:{centroid:7.0f} "
            f"Flux:{spectral_flux:7.4f}"
        )

        client.send_message("/features", [float(x) for x in features])

        

# -----------------------------
# Start stream
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
