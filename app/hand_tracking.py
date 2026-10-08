import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture_detector import detect_gesture

from gesture_controller import (
    GestureController,
    is_inside_zone
)


# ======================================================
# MODEL
# ======================================================

MODEL_PATH = "models/hand_landmarker.task"


# ======================================================
# CAMERA
# ======================================================

print("----------------------------------------")
print("TOUCHLESS SMART DESK LAMP")
print("----------------------------------------")
print("Opening camera...")

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()

print("Camera opened successfully.")


# ======================================================
# MEDIAPIPE
# ======================================================

print("Loading MediaPipe hand model...")

BaseOptions = python.BaseOptions

options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = (
    vision.HandLandmarker
    .create_from_options(options)
)

print("MediaPipe model loaded.")


# ======================================================
# GESTURE CONTROLLER
# ======================================================

controller = GestureController(
    hold_time=1.0,
    cooldown=2.0,
    stability_threshold=0.035,
    history_size=8,

    # Distance-adaptive swipe settings
    swipe_ratio=0.75,
    swipe_time=1.2,
    swipe_min_speed=0.08,
    swipe_history_size=12
)


# ======================================================
# VARIABLES
# ======================================================

timestamp = 0


print()
print("STATIC GESTURES:")
print("Open Palm   -> ON")
print("Fist        -> OFF")
print("Two Fingers -> READING")
print("Point       -> FOCUS")
print()
print("SWIPES:")
print("Swipe Left  -> BRIGHTNESS DOWN")
print("Swipe Right -> BRIGHTNESS UP")
print()
print("Gesture zone: CENTER 60%")
print("Static hold time: 1 second")
print("Press Q to quit.")
print("----------------------------------------")


# ======================================================
# MAIN LOOP
# ======================================================

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:

        print(
            "ERROR: Could not read frame."
        )

        break

    # --------------------------------------------------
    # Mirror camera
    # --------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )

    # --------------------------------------------------
    # MediaPipe
    # --------------------------------------------------

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    timestamp += 33

    result = (
        landmarker
        .detect_for_video(
            mp_image,
            timestamp
        )
    )

    # ==================================================
    # DEFAULT VALUES
    # ==================================================

    gesture = None
    confirmed_action = None
    in_zone = False


    # ==================================================
    # HAND DETECTION
    # ==================================================

    if result.hand_landmarks:

        hand = result.hand_landmarks[0]

        # ----------------------------------------------
        # Detect static gesture
        # ----------------------------------------------

        gesture = detect_gesture(
            hand
        )

        # ----------------------------------------------
        # Check gesture zone
        # ----------------------------------------------

        in_zone = is_inside_zone(
            hand
        )

        # ----------------------------------------------
        # Gesture controller
        # ----------------------------------------------

        confirmed_action = (
            controller.update(
                gesture,
                hand,
                in_zone
            )
        )

        # ----------------------------------------------
        # Draw landmarks
        # ----------------------------------------------

        h, w, _ = frame.shape

        for landmark in hand:

            x = int(
                landmark.x * w
            )

            y = int(
                landmark.y * h
            )

            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )


    # ==================================================
    # GESTURE ZONE
    # ==================================================

    h, w, _ = frame.shape

    x1 = int(w * 0.20)
    y1 = int(h * 0.20)

    x2 = int(w * 0.80)
    y2 = int(h * 0.80)

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (255, 255, 255),
        2
    )


    # ==================================================
    # STATUS
    # ==================================================

    if in_zone:

        zone_text = "ZONE: ACTIVE"

    else:

        zone_text = "ZONE: OUTSIDE"

    cv2.putText(
        frame,
        zone_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ==================================================
    # GESTURE
    # ==================================================

    gesture_text = (
        gesture
        if gesture
        else
        "NO HAND"
    )

    cv2.putText(
        frame,
        f"Gesture: {gesture_text}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # ==================================================
    # CONFIRMED ACTION
    # ==================================================

    if confirmed_action:

        print(
            f"CONFIRMED ACTION: "
            f"{confirmed_action}"
        )

        cv2.putText(
            frame,
            f"ACTION: {confirmed_action}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )


    # ==================================================
    # DISPLAY
    # ==================================================

    cv2.imshow(
        "Touchless Smart Desk Lamp",
        frame
    )


    # ==================================================
    # QUIT
    # ==================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        break


# ======================================================
# CLEANUP
# ======================================================

cap.release()

landmarker.close()

cv2.destroyAllWindows()

print("Program ended.")

