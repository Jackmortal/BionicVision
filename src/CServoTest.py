import busio
import board
import time
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# Standard MG995 pulse widths
MIN_PULSE = 500
MAX_PULSE = 2500

# Channel mapping
FINGERS = {
    "pointer": 0,
    "middle":  1,
    "thumb":   2,
    "ring":    3,
    "pinky":   4,
}

# Safe angle limits — tighten these as you learn each finger's real range
LIMITS = {
    "pointer": (20, 160),
    "middle":  (20, 160),
    "ring":    (20, 160),
    "pinky":   (20, 160),
    "thumb":   (20, 160),
}

# ── Setup ──────────────────────────────────────────────────────────────────

def init_pca():
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50
    return pca

def get_servo(pca, channel):
    return servo.Servo(
        pca.channels[channel],
        min_pulse=MIN_PULSE,
        max_pulse=MAX_PULSE
    )

# ── Movement ───────────────────────────────────────────────────────────────

def move_slowly(servo_obj, target_angle, step=2, delay=0.02):
    """Gradually move servo to target angle."""
    current = servo_obj.angle or 90
    target = max(0, min(180, target_angle))
    steps = range(int(current), int(target), step if current < target else -step)
    for angle in steps:
        servo_obj.angle = angle
        time.sleep(delay)
    servo_obj.angle = target

def move_finger(pca, name, target_angle, step=2, delay=0.02):
    """Move a named finger to a target angle, clamped to its safe limits."""
    min_a, max_a = LIMITS[name]
    safe = max(min_a, min(max_a, target_angle))
    if safe != target_angle:
        print(f"  ⚠ {name}: clamped {target_angle}° → {safe}°")
    s = get_servo(pca, FINGERS[name])
    print(f"  {name}: moving to {safe}°")
    move_slowly(s, safe, step=step, delay=delay)

def move_all(pca, angle, step=2, delay=0.02):
    """Move all fingers to the same angle."""
    for name in FINGERS:
        move_finger(pca, name, angle, step=step, delay=delay)

# ── Test Routines ──────────────────────────────────────────────────────────

def test_single_finger(pca, name):
    """
    Sweep one finger through its full range and back.
    Good for checking travel distance and finding real limits.
    """
    min_a, max_a = LIMITS[name]
    print(f"\n── Single finger test: {name} ──")
    print(f"  Opening ({min_a}°)...")
    move_finger(pca, name, min_a)
    time.sleep(0.5)
    print(f"  Closing ({max_a}°)...")
    move_finger(pca, name, max_a)
    time.sleep(0.5)
    print(f"  Back to open ({min_a}°)...")
    move_finger(pca, name, min_a)
    time.sleep(0.5)

def test_all_fingers_individually(pca):
    """
    Test each finger one at a time so you can watch each one.
    Best for spotting which finger has issues.
    """
    print("\n══ Testing all fingers individually ══")
    for name in FINGERS:
        input(f"\n  Press Enter to test {name}...")
        test_single_finger(pca, name)

def test_open_close(pca, reps=3):
    """
    Open and close the full hand repeatedly.
    Good for checking overall grip and finger sync.
    """
    print(f"\n══ Open/close test ({reps} reps) ══")
    for i in range(reps):
        print(f"\n  Rep {i+1}/{reps}")
        print("  Opening...")
        move_all(pca, 20)
        time.sleep(0.8)
        print("  Closing...")
        move_all(pca, 160)
        time.sleep(0.8)
    print("  Returning to open...")
    move_all(pca, 20)

def test_incremental(pca, name, steps=5):
    """
    Move a finger in even increments across its range.
    Good for checking if movement is smooth or jerky at certain points.
    """
    min_a, max_a = LIMITS[name]
    increment = (max_a - min_a) // steps
    print(f"\n══ Incremental test: {name} ══")
    print(f"  Range: {min_a}° → {max_a}° in {steps} steps of ~{increment}°")
    for i in range(steps + 1):
        angle = min_a + (increment * i)
        print(f"  Step {i}: {angle}°")
        move_finger(pca, name, angle)
        time.sleep(1.0)
    print("  Returning to open...")
    move_finger(pca, name, min_a)

def test_speed(pca, name):
    """
    Test the same finger at 3 different speeds.
    Useful for finding the slowest reliable speed before the servo stalls.
    """
    min_a, max_a = LIMITS[name]
    print(f"\n══ Speed test: {name} ══")
    speeds = [("Slow", 1, 0.04), ("Medium", 2, 0.02), ("Fast", 4, 0.01)]
    for label, step, delay in speeds:
        print(f"\n  {label} (step={step}, delay={delay}s)")
        move_finger(pca, name, min_a)
        time.sleep(0.3)
        s = get_servo(pca, FINGERS[name])
        move_slowly(s, max_a, step=step, delay=delay)
        time.sleep(0.5)
    move_finger(pca, name, min_a)

# ── Interactive Menu ───────────────────────────────────────────────────────

MENU = """
══════════════════════════════
  Bionic Hand Test Menu
══════════════════════════════
  1. Test single finger
  2. Test all fingers individually
  3. Open / close full hand
  4. Incremental test (single finger)
  5. Speed test (single finger)
  6. Move finger to specific angle
  0. Exit
══════════════════════════════
"""

def pick_finger():
    names = list(FINGERS.keys())
    print("\n  Fingers:", ", ".join(f"{i+1}={n}" for i, n in enumerate(names)))
    try:
        idx = int(input("  Pick finger (1-5): ")) - 1
        return names[idx]
    except (ValueError, IndexError):
        print("  Invalid choice.")
        return None

def main():
    pca = init_pca()
    print("Initializing — moving all fingers to open position...")
    move_all(pca, 20)
    time.sleep(1)

    while True:
        print(MENU)
        choice = input("Choice: ").strip()

        if choice == "1":
            name = pick_finger()
            if name:
                test_single_finger(pca, name)

        elif choice == "2":
            test_all_fingers_individually(pca)

        elif choice == "3":
            try:
                reps = int(input("  How many reps? (default 3): ") or 3)
            except ValueError:
                reps = 3
            test_open_close(pca, reps=reps)

        elif choice == "4":
            name = pick_finger()
            if name:
                try:
                    steps = int(input("  How many steps? (default 5): ") or 5)
                except ValueError:
                    steps = 5
                test_incremental(pca, name, steps=steps)

        elif choice == "5":
            name = pick_finger()
            if name:
                test_speed(pca, name)

        elif choice == "6":
            name = pick_finger()
            if name:
                try:
                    angle = int(input(f"  Target angle for {name} (0-180): "))
                    move_finger(pca, name, angle)
                except ValueError:
                    print("  Invalid angle.")

        elif choice == "0":
            print("Returning all fingers to open position...")
            move_all(pca, 20)
            print("Done.")
            break

        else:
            print("  Invalid choice, try again.")

if __name__ == "__main__":
    main()
