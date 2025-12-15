import subprocess
import time
import pyautogui
import pygetwindow as gw
from screeninfo import get_monitors

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PLAYLIST_URL = "https://www.youtube.com/watch?v=wzZb8Ijjwds&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=1&pp=gAQBiAQB8AUB"

# UPDATE THESE
SHUFFLE_X = 2081
SHUFFLE_Y = 572
safe_x = 1883
safe_y = 659

class YouTubePlayer:
    def __init__(self, monitor_index=0):
        self.monitor_index = monitor_index

    # ================= LAUNCH =================
    def launch(self):
        print("[PLAYER] Launching playlist")

        subprocess.Popen([
            CHROME_PATH,
            "--new-window",
            PLAYLIST_URL
        ])

        time.sleep(8)
        #self._focus()

        # Click Shuffle
        #time.sleep(3)
        pyautogui.click(SHUFFLE_X, SHUFFLE_Y)
        print("[PLAYER] Shuffle clicked")

        pyautogui.press("m")        
        pyautogui.hotkey("shift", "n")

        time.sleep(0.5)
        self._move_to_monitor()

       # self.skip()

         # Fullscreen
        time.sleep(0.4)
        pyautogui.press("f")


        # Start muted + skip once
        time.sleep(1)
       
        #self.skip()

        print("[PLAYER] Ready")

    # ================= HELPERS =================
    def _focus(self):
       pyautogui.click(safe_x, safe_y)
       
                    

    def _move_to_monitor(self):
        monitors = get_monitors()
        if self.monitor_index >= len(monitors):
            return

        for w in gw.getAllWindows():
            if "youtube" in (w.title or "").lower():
                m = monitors[self.monitor_index]
                w.moveTo(m.x + 10, m.y + 10)
                w.resizeTo(m.width - 20, m.height - 20)
                return

    # ================= CONTROLS =================
    def play_pause(self):
        self._focus()
        pyautogui.press("k")

    def mute(self):
        self._focus()
        pyautogui.press("m")

    def volume_up(self):
        self._focus()
        pyautogui.press("up")

    def volume_down(self):
        self._focus()
        pyautogui.press("down")

    def skip(self):
        self._focus()
        pyautogui.hotkey("shift", "n")
