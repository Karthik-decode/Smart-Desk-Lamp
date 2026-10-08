import time
import math
from collections import deque


class GestureController:

    def __init__(
        self,
        hold_time=1.0,
        cooldown=2.0,
        stability_threshold=0.035,
        history_size=8,

        # Swipe settings
        swipe_ratio=0.75,
        swipe_time=1.2,
        swipe_min_speed=0.08,
        swipe_history_size=12
    ):

        self.hold_time = hold_time
        self.cooldown = cooldown
        self.stability_threshold = stability_threshold

        # Swipe configuration
        self.swipe_ratio = swipe_ratio
        self.swipe_time = swipe_time
        self.swipe_min_speed = swipe_min_speed

        self.current_gesture = None
        self.gesture_start_time = None

        self.last_command = None
        self.last_command_time = 0

        # Static gesture stability
        self.position_history = deque(
            maxlen=history_size
        )

        # Swipe tracking
        self.swipe_history = deque(
            maxlen=swipe_history_size
        )

        self.swipe_start_position = None
        self.swipe_start_time = None

    # ==================================================
    # HAND CENTER
    # ==================================================

    def get_hand_center(self, landmarks):

        x = sum(
            point.x for point in landmarks
        ) / len(landmarks)

        y = sum(
            point.y for point in landmarks
        ) / len(landmarks)

        return x, y

    # ==================================================
    # HAND SIZE
    # ==================================================

    def get_hand_size(self, landmarks):

        xs = [
            point.x
            for point in landmarks
        ]

        ys = [
            point.y
            for point in landmarks
        ]

        width = max(xs) - min(xs)
        height = max(ys) - min(ys)

        # Use the larger dimension so that
        # hand orientation has less effect.

        hand_size = max(
            width,
            height
        )

        # Prevent division by zero
        return max(hand_size, 0.001)

    # ==================================================
    # STABILITY
    # ==================================================

    def is_stable(self, landmarks):

        center = self.get_hand_center(
            landmarks
        )

        self.position_history.append(
            center
        )

        if len(self.position_history) < 4:
            return False

        current_x, current_y = center

        distances = []

        for x, y in self.position_history:

            distance = math.sqrt(
                (current_x - x) ** 2 +
                (current_y - y) ** 2
            )

            distances.append(distance)

        maximum_movement = max(
            distances
        )

        return (
            maximum_movement
            <= self.stability_threshold
        )

    # ==================================================
    # RESET SWIPE
    # ==================================================

    def reset_swipe(self):

        self.swipe_start_position = None
        self.swipe_start_time = None

        self.swipe_history.clear()

    # ==================================================
    # SWIPE DETECTION
    # ==================================================

    def detect_swipe(
        self,
        landmarks,
        in_zone,
        current_time
    ):

        if not in_zone:

            self.reset_swipe()

            return None

        # ----------------------------------------------
        # CURRENT POSITION
        # ----------------------------------------------

        center_x, center_y = (
            self.get_hand_center(
                landmarks
            )
        )

        # ----------------------------------------------
        # CURRENT HAND SIZE
        # ----------------------------------------------

        hand_size = self.get_hand_size(
            landmarks
        )

        # ----------------------------------------------
        # START SWIPE TRACKING
        # ----------------------------------------------

        if self.swipe_start_position is None:

            self.swipe_start_position = (
                center_x,
                center_y
            )

            self.swipe_start_time = (
                current_time
            )

            self.swipe_history.append(
                (
                    center_x,
                    center_y,
                    hand_size,
                    current_time
                )
            )

            return None

        # ----------------------------------------------
        # ADD CURRENT POSITION
        # ----------------------------------------------

        self.swipe_history.append(
            (
                center_x,
                center_y,
                hand_size,
                current_time
            )
        )

        # ----------------------------------------------
        # TIME
        # ----------------------------------------------

        start_x, start_y = (
            self.swipe_start_position
        )

        elapsed = (
            current_time
            - self.swipe_start_time
        )

        # ----------------------------------------------
        # TOO SLOW
        # ----------------------------------------------

        if elapsed > self.swipe_time:

            # Start a new possible swipe
            self.swipe_start_position = (
                center_x,
                center_y
            )

            self.swipe_start_time = (
                current_time
            )

            self.swipe_history.clear()

            self.swipe_history.append(
                (
                    center_x,
                    center_y,
                    hand_size,
                    current_time
                )
            )

            return None

        # ----------------------------------------------
        # RAW MOVEMENT
        # ----------------------------------------------

        delta_x = center_x - start_x
        delta_y = center_y - start_y

        # ----------------------------------------------
        # HAND-SIZE NORMALIZATION
        # ----------------------------------------------

        # Average hand size during the swipe
        # makes the threshold adaptive to camera distance.

        sizes = [
            item[2]
            for item in self.swipe_history
        ]

        average_hand_size = (
            sum(sizes) / len(sizes)
        )

        # Movement relative to hand size
        normalized_horizontal = (
            abs(delta_x)
            / average_hand_size
        )

        normalized_vertical = (
            abs(delta_y)
            / average_hand_size
        )

        # ----------------------------------------------
        # HORIZONTAL DOMINANCE
        # ----------------------------------------------

        if (
            normalized_horizontal
            < normalized_vertical * 1.5
        ):

            return None

        # ----------------------------------------------
        # REQUIRED RELATIVE DISTANCE
        # ----------------------------------------------

        if (
            normalized_horizontal
            < self.swipe_ratio
        ):

            return None

        # ----------------------------------------------
        # SPEED CHECK
        # ----------------------------------------------

        if elapsed <= 0:

            return None

        speed = (
            abs(delta_x)
            / elapsed
        )

        if speed < self.swipe_min_speed:

            return None

        # ----------------------------------------------
        # DIRECTION CONSISTENCY
        # ----------------------------------------------

        positions = [
            item[0]
            for item in self.swipe_history
        ]

        if len(positions) >= 4:

            direction_changes = 0

            previous_direction = None

            for i in range(1, len(positions)):

                movement = (
                    positions[i]
                    - positions[i - 1]
                )

                if abs(movement) < 0.003:

                    continue

                if movement > 0:

                    direction = "RIGHT"

                else:

                    direction = "LEFT"

                if (
                    previous_direction is not None
                    and
                    direction
                    != previous_direction
                ):

                    direction_changes += 1

                previous_direction = direction

            # Too many direction changes means
            # the hand was probably moving randomly.

            if direction_changes > 2:

                return None

        # ----------------------------------------------
        # CONFIRM SWIPE
        # ----------------------------------------------

        self.reset_swipe()

        if delta_x < 0:

            return "SWIPE_LEFT"

        return "SWIPE_RIGHT"

    # ==================================================
    # MAIN UPDATE
    # ==================================================

    def update(
        self,
        gesture,
        landmarks,
        in_zone
    ):

        current_time = time.time()

        if (
            gesture is None
            or landmarks is None
            or not in_zone
        ):

            self.current_gesture = None
            self.gesture_start_time = None

            self.position_history.clear()

            self.reset_swipe()

            return None

        # ----------------------------------------------
        # SWIPE
        # ----------------------------------------------

        swipe = self.detect_swipe(
            landmarks,
            in_zone,
            current_time
        )

        if swipe:

            if (
                current_time
                - self.last_command_time
                >= self.cooldown
            ):

                self.last_command = swipe

                self.last_command_time = (
                    current_time
                )

                self.current_gesture = None
                self.gesture_start_time = None

                self.position_history.clear()

                return swipe

        # ----------------------------------------------
        # STATIC GESTURE
        # ----------------------------------------------

        stable = self.is_stable(
            landmarks
        )

        if gesture != self.current_gesture:

            self.current_gesture = gesture

            self.gesture_start_time = (
                current_time
            )

            return None

        if not stable:

            self.gesture_start_time = (
                current_time
            )

            return None

        elapsed = (
            current_time
            - self.gesture_start_time
        )

        if elapsed < self.hold_time:

            return None

        # ----------------------------------------------
        # COOLDOWN
        # ----------------------------------------------

        if (
            current_time
            - self.last_command_time
            < self.cooldown
        ):

            return None

        # ----------------------------------------------
        # CONFIRM STATIC GESTURE
        # ----------------------------------------------

        self.last_command = gesture

        self.last_command_time = (
            current_time
        )

        self.current_gesture = None
        self.gesture_start_time = None

        self.position_history.clear()

        return gesture


# ======================================================
# GESTURE ZONE
# ======================================================

def is_inside_zone(landmarks):

    xs = [
        point.x
        for point in landmarks
    ]

    ys = [
        point.y
        for point in landmarks
    ]

    center_x = sum(xs) / len(xs)
    center_y = sum(ys) / len(ys)

    return (
        0.20 <= center_x <= 0.80
        and
        0.20 <= center_y <= 0.80
    )

