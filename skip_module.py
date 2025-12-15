# ================= PARAMETERS =================
HEAD_MARGIN = 0.05
CLAP_DIST = 0.08
HOLD_TIME = 0.3
DEBOUNCE_TIME = 2.0

# ================= STATE =================
armed_time = None
last_trigger_time = 0
state = "IDLE"

def reset():
    global armed_time
    armed_time = None

def update(hand_lms, head_y, now):
    """
    Skip gesture:
    - BOTH hands visible
    - BOTH wrists above head
    - Hands move close together (clap)
    """

    global armed_time, last_trigger_time, state

    if len(hand_lms) != 2 or head_y is None:
        reset()
        return None

    w1 = hand_lms[0].landmark[0]
    w2 = hand_lms[1].landmark[0]

    # Both hands must be above head
    if w1.y > head_y - HEAD_MARGIN or w2.y > head_y - HEAD_MARGIN:
        reset()
        return None

    dist = abs(w1.x - w2.x)

    if dist < CLAP_DIST:
        if armed_time is None:
            armed_time = now
            return None

        if (
            now - armed_time >= HOLD_TIME and
            now - last_trigger_time >= DEBOUNCE_TIME
        ):
            last_trigger_time = now
            reset()
            state = "SKIP"
            print("[SKIP DEBUG] clap skip triggered")
            return state

    else:
        armed_time = None

    return None
