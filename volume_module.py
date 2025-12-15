import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ================= AUDIO =================
device = AudioUtilities.GetSpeakers()
interface = device._dev.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# ================= PARAMETERS =================
VOLUME_RATE = 0.4
SHOULDER_MARGIN = 0.03
WIDTH_TOLERANCE = 0.05  # dead zone around shoulder width

# ================= STATE =================
state = "IDLE"

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def update(hand_lms, shoulder_y, shoulder_width, dt):
    """
    hand_lms: list of 2 MediaPipe hand landmarks
    shoulder_y: average shoulder y
    shoulder_width: distance between shoulders
    dt: seconds since last frame
    """
    global state

    if len(hand_lms) != 2 or shoulder_y is None or shoulder_width is None:
        state = "IDLE"
        return state

    lmA = hand_lms[0].landmark
    lmB = hand_lms[1].landmark

    # sort left/right for consistency
    if lmA[0].x > lmB[0].x:
        lmA, lmB = lmB, lmA

    yA = lmA[0].y
    yB = lmB[0].y

    both_above_shoulders = (
        yA < shoulder_y - SHOULDER_MARGIN and
        yB < shoulder_y - SHOULDER_MARGIN
    )

    if not both_above_shoulders:
        state = "IDLE"
        return state

    hand_width = dist(lmA[0], lmB[0])
    vol = volume.GetMasterVolumeLevelScalar()

    if hand_width > shoulder_width * (1 + WIDTH_TOLERANCE):
        volume.SetMasterVolumeLevelScalar(
            min(1.0, vol + VOLUME_RATE * dt), None)
        state = "VOLUME UP"

    elif hand_width < shoulder_width * (1 - WIDTH_TOLERANCE):
        volume.SetMasterVolumeLevelScalar(
            max(0.0, vol - VOLUME_RATE * dt), None)
        state = "VOLUME DOWN"

    else:
        state = "ARMED"

    return state
