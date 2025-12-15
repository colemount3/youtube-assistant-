import cv2
import mediapipe as mp
import math
import time

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

# ================= MEDIAPIPE =================
mp_hands = mp.solutions.hands
mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

cap = cv2.VideoCapture(0)

# ================= PARAMETERS =================
VOLUME_RATE = 0.4
SHOULDER_MARGIN = 0.03
DIST_THRESHOLD = 0.015

# ================= STATE =================
last_time = time.time()
last_dist = None
state = "IDLE"
motion_dir = None  # "UP" | "DOWN" | None

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# ================= LOOP =================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    now = time.time()
    dt = now - last_time
    last_time = now

    hand_result = hands.process(rgb)
    pose_result = pose.process(rgb)

    hand_lms = hand_result.multi_hand_landmarks or []

    # -------- POSE --------
    if pose_result.pose_landmarks:
        lm_pose = pose_result.pose_landmarks.landmark
        shoulder_y = (
            lm_pose[mp_pose.PoseLandmark.LEFT_SHOULDER].y +
            lm_pose[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        ) / 2
    else:
        shoulder_y = None

    # -------- VOLUME CORE --------
    if len(hand_lms) == 2 and shoulder_y is not None:
        lmA = hand_lms[0].landmark
        lmB = hand_lms[1].landmark

        if lmA[0].x > lmB[0].x:
            lmA, lmB = lmB, lmA

        yA = lmA[0].y
        yB = lmB[0].y

        both_above = (
            yA < shoulder_y - SHOULDER_MARGIN and
            yB < shoulder_y - SHOULDER_MARGIN
        )

        hand_dist = dist(lmA[0], lmB[0])

        if both_above:
            if last_dist is not None:
                delta = hand_dist - last_dist

                if abs(delta) > DIST_THRESHOLD:
                    motion_dir = "UP" if delta > 0 else "DOWN"

            if motion_dir == "UP":
                vol = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(
                    min(1.0, vol + VOLUME_RATE * dt), None)
                state = "VOLUME UP"

            elif motion_dir == "DOWN":
                vol = volume.GetMasterVolumeLevelScalar()
                volume.SetMasterVolumeLevelScalar(
                    max(0.0, vol - VOLUME_RATE * dt), None)
                state = "VOLUME DOWN"

            else:
                state = "ARMED"

            last_dist = hand_dist

        else:
            # Drop below shoulders → reset
            last_dist = None
            motion_dir = None
            state = "IDLE"

    else:
        last_dist = None
        motion_dir = None
        state = "IDLE"

    # -------- DRAW --------
    for h in hand_lms:
        mp_draw.draw_landmarks(frame, h, mp_hands.HAND_CONNECTIONS)

    if pose_result.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            pose_result.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    cv2.putText(frame, state, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 255), 2)

    cv2.imshow("Vision Control – Volume Latched", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
