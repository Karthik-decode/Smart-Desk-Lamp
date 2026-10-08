import cv2
from hand_tracking import HandTracker


tracker = HandTracker()

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Camera could not be opened.")
    exit()


while True:

    success, frame = camera.read()

    if not success:
        print("Error: Could not read camera frame.")
        break

    # Mirror the camera
    frame = cv2.flip(frame, 1)

    # Detect hand
    results = tracker.process(frame)

    # Draw landmarks
    frame = tracker.draw_landmarks(frame, results)

    # Title
    cv2.putText(
        frame,
        "Touchless Smart Desk Lamp",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 255, 0),
        2
    )

    # Show camera
    cv2.imshow(
        "Smart Lamp - Hand Tracking",
        frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()