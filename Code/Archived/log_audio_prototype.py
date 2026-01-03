from pythonosc import dispatcher, osc_server
import threading
import time

# -----------------------------
# OSC handler
# -----------------------------
def amp_handler(addr, rms, centroid):
    print(f"[Listener] RMS: {rms:6.1f} dB | Centroid: {centroid:8.1f}")

# -----------------------------
# Setup dispatcher
# -----------------------------
disp = dispatcher.Dispatcher()
disp.map("/amp", amp_handler)

# -----------------------------
# Start server
# -----------------------------
server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9001), disp)
print("[Listener] Listening on port 9001")

server_thread = threading.Thread(
    target=lambda: server.serve_forever(poll_interval=0.1),
    daemon=True
)
server_thread.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("[Listener] Shutting down…")
    server.shutdown()
    server.server_close()
    server_thread.join()
    print("[Listener] Stopped.")
