import cv2
import time
import mediapipe as mp
from queue import Queue

import volume_module
import mute_module
import PLAY_PAUSE_module
from voice_module import VoiceListener
from player_controller import YouTubePlayer

# ================= PLAYER =================
player = YouTubePlayer(
    monitor_index=2
)
player.launch()

# ================= VOICE =================
event_queue = Queue()
voice = VoiceListener("models/vosk-en", event_queue)
voice.start()

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

# ================= TIMING =================
last_time = time.time()

INTENT_WINDOW = 1.0
ACTION_DEBOUNCE = 2.0

intent_hand = None
intent_start_time = None
last_action_time = 0

# ================= DEBUG =================
last_event = None
flash_text = None
flash_until = 0
FLASH_DURATION = 0.6

# ================= LOOP =================
while True:
    state = "IDLE"

    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    now = time.time()
    dt = now - last_time
    last_time = now

    # ---------- VOICE ----------
    voice.update()
    while not event_queue.empty():
        event = event_queue.get()
        print(f"[VOICE] {event}")

        if event == "SKIP":
            player.skip()
        elif event == "MUTE":
            player.mute()
        elif event == "PLAY_PAUSE":
            player.play_pause()
        elif event == "VOLUME_UP":
            player.volume_up()
        elif event == "VOLUME_DOWN":
            player.volume_down()

        state = event
        flash_text = event
        flash_until = now + FLASH_DURATION
        last_event = event

    # ---------- VISION ----------
    hand_result = hands.process(rgb)
    pose_result = pose.process(rgb)

    hand_lms = hand_result.multi_hand_landmarks or []

    if pose_result.pose_landmarks:
        lm = pose_result.pose_landmarks.landmark
        left_sh = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_sh = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        nose = lm[mp_pose.PoseLandmark.NOSE]

        shoulder_y = (left_sh.y + right_sh.y) / 2
        shoulder_width = abs(left_sh.x - right_sh.x)
        head_y = nose.y
        nose_x = nose.x
    else:
        shoulder_y = None
        shoulder_width = None
        head_y = None
        nose_x = None

    # ---------- VOLUME ----------
    vol_state = volume_module.update(
        hand_lms,
        shoulder_y,
        shoulder_width,
        dt
    )
    if vol_state:
        state = vol_state

    # ---------- GESTURES ----------
    left_up = mute_module.detect(hand_lms, head_y, nose_x)
    right_up = PLAY_PAUSE_module.detect(hand_lms, head_y, nose_x)

    event = None

    if left_up and right_up:
        if now - last_action_time > ACTION_DEBOUNCE:
            event = "SKIP"
            last_action_time = now
            intent_hand = None
            intent_start_time = None

    elif left_up or right_up:
        current_hand = "LEFT" if left_up else "RIGHT"

        if intent_hand is None:
            intent_hand = current_hand
            intent_start_time = now

        elif (
            intent_hand == current_hand and
            now - intent_start_time >= INTENT_WINDOW and
            now - last_action_time > ACTION_DEBOUNCE
        ):
            event = "MUTE" if intent_hand == "LEFT" else "PLAY_PAUSE"
            last_action_time = now
            intent_hand = None
            intent_start_time = None

    else:
        intent_hand = None
        intent_start_time = None

    # ---------- EXECUTE ----------
    if event == "SKIP":
        player.skip()
        state = "SKIP"
    elif event == "MUTE":
        player.mute()
        state = "MUTE"
    elif event == "PLAY_PAUSE":
        player.play_pause()
        state = "PLAY_PAUSE"

    # ---------- DEBUG ----------
    if event and event != last_event:
        print(f"[GESTURE] {event}")
        flash_text = event
        flash_until = now + FLASH_DURATION
        last_event = event

    # ---------- DRAW ----------
    for h in hand_lms:
        mp_draw.draw_landmarks(frame, h, mp_hands.HAND_CONNECTIONS)

    if pose_result.pose_landmarks:
        mp_draw.draw_landmarks(frame, pose_result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.putText(frame, state, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 255, 255), 2)

    if flash_text and now < flash_until:
        h, w, _ = frame.shape
        cv2.putText(frame, flash_text,
                    (w // 2 - 200, h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (0, 0, 255), 4)

    cv2.imshow("Vision Control – Master", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
f