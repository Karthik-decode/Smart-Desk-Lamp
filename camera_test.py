import cv2


print("Starting camera test...")

cap = cv2.VideoCapture(0)

print("Camera opened:", cap.isOpened())

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

while True:

    ret, frame = cap.read()

    if not ret:
        print("ERROR: Could not read camera frame.")
        break

    cv2.imshow(
        "Camera Test",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


cap.release()

cv2.destroyAllWindows()

print("Camera test ended.")

