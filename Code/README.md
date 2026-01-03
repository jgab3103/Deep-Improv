# Deep Improv

Deep Improv captures and analyses MIDI data in real time to enhance live improvised performance. The system records both note-on/note-off events and any changes in MIDI-enabled effects units (for example, an LFO filter knob on a synth, or a level change on a guitar pedal). All data is timestamped and used by deep learning models to create new MIDI events that can feed back to performers as musical stimulus during improvisation.

The goal is not to automate performance, but to enhance the improvisational environment by allowing performers to interact with emerging musical structures — creating a live feedback loop between musician, data, and sound. This multidisciplinary project combines improvisation, live sound design, computational modeling, and symbolic music representation.

The name Deep Improv references Pauline Oliveros’ Deep Listening project and extends it into live improvisation using MIDI and spectrogram data created in real time.

For more information, see [Deep Improv](https://jamiegabriel.org/deep-improv.html).

---

## Getting Started

Clone the repository and create a Python virtual environment:

```bash
git clone https://github.com/yourusername/deep-improv.git
cd deep-improv
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
