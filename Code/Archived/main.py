from pythonosc import dispatcher, osc_server
import threading
import time

# -------------------------------
# Handler for incoming messages
# -------------------------------
def print_handler(addr, *args):
    print("Received:", addr, args)

# -------------------------------
# Function to start OSC server
# -------------------------------
def start_server(host="127.0.0.1", port=9001):
    disp = dispatcher.Dispatcher()
    disp.map("/amp", print_handler)

    server = osc_server.ThreadingOSCUDPServer((host, port), disp)
    print(f"[Python] OSC server listening on {host}:{port}")

    # Run server in a thread
    server_thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=0.1))
    server_thread.start()

    return server, server_thread

# -------------------------------
# Function to stop OSC server
# -------------------------------
def stop_server(server, server_thread):
    print("[Python] Shutting down OSC server...")
    server.shutdown()       # tell server to stop
    server_thread.join()    # wait for thread to finish
    print("[Python] Server stopped.")

# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    # Start the server
    server, thread = start_server()

    try:
        print("[Python] Press Ctrl+C to stop...")
        while True:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        # Stop safely
        stop_server(server, thread)
