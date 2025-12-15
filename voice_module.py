import queue
import json
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer


# ================= CONFIG =================
SAMPLE_RATE = 16000
BLOCK_SIZE = 4000   # smaller = lower latency

TRIGGER = "computer"

# ================= COMMAND PHRASES =================
# Keep these explicit and readable
def parse_command(text):
    if "computer mute" in text:
        return "MUTE"

    elif "computer play" in text or "computer pause" in text:
        return "PLAY_PAUSE"

    elif "computer skip" in text or "computer next" in text:
        return "SKIP"

    elif "computer volume up" in text:
        return "VOLUME_UP"

    elif "computer volume down" in text:
        return "VOLUME_DOWN"
    
    elif "computer change playlist" in text:
        return "CHANGE_PLAYLIST"

    return None


class VoiceListener:
    def __init__(self, model_path, event_queue, device=None):
        """
        model_path : path to Vosk model folder
        event_queue: queue.Queue() shared with master
        device     : optional microphone index
        """

        self.audio_q = queue.Queue()
        self.event_queue = event_queue

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.recognizer.SetWords(False)

        self.stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            device=device,
            callback=self._audio_callback
        )

    # ================= AUDIO CALLBACK =================
    def _audio_callback(self, indata, frames, time_info, status):
        self.audio_q.put(bytes(indata))

    # ================= START =================
    def start(self):
        print("[VOICE] Listening...")
        self.stream.start()

    # ================= UPDATE LOOP =================
    def update(self):
        """
        Call this once per master loop iteration.
        """

        while not self.audio_q.empty():
            data = self.audio_q.get()

            # ---- FINAL RESULT ----
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower().strip()

            # ---- PARTIAL RESULT ----
            else:
                partial = json.loads(self.recognizer.PartialResult())
                text = partial.get("partial", "").lower().strip()

            if not text:
                continue

            # DEBUG (optional)
            # print("[VOICE RAW]", text)

            # ---- COMMAND PARSING ----
            event = parse_command(text)
            if event:
                print(f"[VOICE CMD] {event}")
                self.event_queue.put(event)

                # Clear recognizer so old text doesn't repeat
                self.recognizer.Reset()
                return
