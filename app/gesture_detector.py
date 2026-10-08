import math


def distance(p1, p2):
    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def finger_up(landmarks, tip, pip):
    return landmarks[tip].y < landmarks[pip].y


def detect_gesture(hand_landmarks):

    # Finger tips
    thumb_tip = 4
    index_tip = 8
    middle_tip = 12
    ring_tip = 16
    pinky_tip = 20

    # Finger PIP joints
    index_pip = 6
    middle_pip = 10
    ring_pip = 14
    pinky_pip = 18

    index = finger_up(hand_landmarks, index_tip, index_pip)
    middle = finger_up(hand_landmarks, middle_tip, middle_pip)
    ring = finger_up(hand_landmarks, ring_tip, ring_pip)
    pinky = finger_up(hand_landmarks, pinky_tip, pinky_pip)

    # Open palm
    if index and middle and ring and pinky:
        return "OPEN_PALM"

    # Fist
    if not index and not middle and not ring and not pinky:
        return "FIST"

    # Two fingers
    if index and middle and not ring and not pinky:
        return "TWO_FINGERS"

    # Pointing
    if index and not middle and not ring and not pinky:
        return "POINT"

    return "UNKNOWN"