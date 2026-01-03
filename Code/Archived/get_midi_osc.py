import mido

print("Available MIDI input ports:")
for port in mido.get_input_names():
    print(port)



import mido
from datetime import datetime

PORT_NAME = "USB MIDI Interface"

with mido.open_input(PORT_NAME) as inport:
    print(f"Listening on {PORT_NAME}...")
    for msg in inport:
        timestamp = datetime.now().isoformat()
        print(timestamp, msg)
