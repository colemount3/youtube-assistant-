import pyautogui
import time
import math

# ================= PARAMETERS =================
HEAD_MARGIN = 0.05
CLICK_THRESHOLD = 0.03
CLICK_DEBOUNCE = 0.6
TOGGLE_DEBOUNCE = 2.0
SMOOTHING = 0.15

# ================= STATE =================
pointer_enabled = False
last_toggle_time = 0
last_click_time = 0
last_x = None
last_y = None
state = "POINTER OFF"

screen_w, screen_h = pyautogui.size()

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def reset_motion():
    global last_x, last_y
    last_x = None
    last_y = None

def update(hand_lms, head_y, nose_x, now):
    """
    Returns:
      (state_string, pointer_enabled)
    """
    global pointer_enabled, last_toggle_time, last_click_time, state

    if len(hand_lms) < 2 or head_y is None:
        return state, pointer_enabled

    # --- TOGGLE POINTER MODE ---
    above_head = [
        h.landmark[0].y < head_y - HEAD_MARGIN
        for h in hand_lms
    ]

    if (
        all(above_head) and
        now - last_toggle_time > TOGGLE_DEBOUNCE
    ):
        pointer_enabled = not pointer_enabled
        last_toggle_time = now
        reset_motion()
        state = "POINTER ON" if pointer_enabled else "POINTER OFF"
        return state, pointer_enabled

    # --- POINTER MODE OFF ---
    if not pointer_enabled:
        state = "POINTER OFF"
        return state, pointer_enabled

    # --- POINTER MODE ON ---
    # Use RIGHT hand (right of nose)
    right_hand = None
    for h in hand_lms:
        if h.landmark[0].x > nose_x:
            right_hand = h.landmark
            break

    if right_hand is None:
        reset_motion()
        return "POINTER ON", pointer_enabled

    wrist = right_hand[0]

    x = wrist.x * screen_w
    y = wrist.y * screen_h

    if last_x is None:
        last_x, last_y = x, y
        return "POINTER ON", pointer_enabled

    dx = (x - last_x) * SMOOTHING
    dy = (y - last_y) * SMOOTHING

    pyautogui.moveRel(dx, dy)

    last_x += dx
    last_y += dy

    # --- CLICK (FIST) ---
    thumb = right_hand[4]
    index = right_hand[8]

    if (
        dist(thumb, index) < CLICK_THRESHOLD and
        now - last_click_time > CLICK_DEBOUNCE
    ):
        pyautogui.click()
        last_click_time = now
        return "CLICK", pointer_enabled

    state = "POINTER ON"
    return state, pointer_enabled
