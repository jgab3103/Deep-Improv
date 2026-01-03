from pythonosc import dispatcher, osc_server
import threading
import time

# -----------------------------
# OSC handler for 12 features
# -----------------------------
def feature_handler(
    addr,
    timestamp,
    rms_db,
    rms_delta,
    centroid,
    rolloff,
    flatness,
    low_energy,
    mid_energy,
    high_energy,
    spectral_flux,
    onset_strength
):
    print(
        f"[Listener] Timestamp:{timestamp:.3f} "
        f"RMS(dB):{rms_db:.2f} Δ:{rms_delta:.4f} "
        f"Centroid:{centroid:.1f} "
        f"Rolloff:{rolloff:.1f} "
        f"Flatness:{flatness:.4f} "
        f"Low:{low_energy:.3f} Mid:{mid_energy:.3f} High:{high_energy:.3f} "
        f"Flux:{spectral_flux:.4f} Onset:{onset_strength:.4f}"
    )

# -----------------------------
# Setup dispatcher
# -----------------------------
disp = dispatcher.Dispatcher()
disp.map("/features", feature_handler)

# -----------------------------
# Start server
# -----------------------------
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9001), disp)
print("[Listener] Listening on port 9001")

server_thread = threading.Thread(
    target=server.serve_forever,
    kwargs={"poll_interval": 0.1},
    daemon=True
)
server_thread.start()

# -----------------------------
# Keep alive
# -----------------------------
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[Listener] Shutting down…")
    server.shutdown()
    server.server_close()
    server_thread.join()
    print("[Listener] Stopped.")
