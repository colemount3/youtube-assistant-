HEAD_MARGIN = 0.05

def detect(hand_lms, head_y, nose_x):
    """
    Returns True if TRUE LEFT hand is above head
    """
    if not hand_lms or head_y is None or nose_x is None:
        return False

    for h in hand_lms:
        wrist = h.landmark[0]
        if wrist.x < nose_x and wrist.y < head_y - HEAD_MARGIN:
            return True

    return False
