# Trackcoder trackball and spinner encoder for the raspberry pi pico.
#changelog:
# 0.1a Basic happ trackball support
# 0.2 Supports up to 3 trackballs
# 0.3 Added mouse buttons, sensitivity multiplier and inverting X and Y axis

import board
import rotaryio
import usb_hid
from adafruit_hid.mouse import Mouse
import time

# ============================================================
# HAPP TRACKBALL WIRING
# ============================================================
X Horizontal A Yellow → GP0  
X Horizontal B Green → GP1  
Y Vertical A Blue → GP2  
Y Vertical B Purple → GP3  
+5volt V → VBUS  
GND → GND
# ============================================================

# ============================================================
# CONFIGURATION - edit these
# ============================================================

# Sensitivity multiplier (higher = faster cursor)
SCALE = 2

# Invert axes if needed (True/False)
INVERT_X = False
INVERT_Y = False

# List of trackballs. Each entry is (x_a_pin, x_b_pin, y_a_pin, y_b_pin)
# Add more tuples for additional trackballs.
TRACKBALLS = [
    (board.GP0, board.GP1, board.GP2, board.GP3),   # Trackball 1
    # (board.GP4, board.GP5, board.GP6, board.GP7), # Trackball 2 (uncomment to enable)
    # (board.GP8, board.GP9, board.GP10, board.GP11), # Trackball 3
]

# Optional mouse buttons (active low with internal pull-up)
# Set to None if you don't have buttons wired
LEFT_BUTTON_PIN  = None   # e.g. board.GP16
RIGHT_BUTTON_PIN = None   # e.g. board.GP17
MIDDLE_BUTTON_PIN = None  # e.g. board.GP18

# ============================================================

mouse = Mouse(usb_hid.devices)

# Create encoders
encoders = []
for xa, xb, ya, yb in TRACKBALLS:
    x_enc = rotaryio.IncrementalEncoder(xa, xb)
    y_enc = rotaryio.IncrementalEncoder(ya, yb)
    encoders.append({
        "x": x_enc,
        "y": y_enc,
        "last_x": x_enc.position,
        "last_y": y_enc.position,
    })

# Optional buttons
def make_button(pin):
    if pin is None:
        return None
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    return btn

import digitalio
left_btn   = make_button(LEFT_BUTTON_PIN)
right_btn  = make_button(RIGHT_BUTTON_PIN)
middle_btn = make_button(MIDDLE_BUTTON_PIN)

print("Happ trackball mouse ready ({} trackball(s))".format(len(encoders)))

while True:
    total_dx = 0
    total_dy = 0

    for enc in encoders:
        # X axis
        pos = enc["x"].position
        dx = pos - enc["last_x"]
        enc["last_x"] = pos
        if INVERT_X:
            dx = -dx
        total_dx += dx

        # Y axis
        pos = enc["y"].position
        dy = pos - enc["last_y"]
        enc["last_y"] = pos
        if INVERT_Y:
            dy = -dy
        total_dy += dy

    # Apply scale
    dx = total_dx * SCALE
    dy = total_dy * SCALE

    # Buttons (active low)
    buttons = 0
    if left_btn and not left_btn.value:
        buttons |= Mouse.LEFT_BUTTON
    if right_btn and not right_btn.value:
        buttons |= Mouse.RIGHT_BUTTON
    if middle_btn and not middle_btn.value:
        buttons |= Mouse.MIDDLE_BUTTON

    if dx or dy or buttons:
        mouse.move(x=dx, y=dy, buttons=buttons)
    else:
        # Keep the report alive when idle (optional but good practice)
        mouse.release_all()

    # Small sleep is fine; rotaryio is interrupt-driven so you won't miss steps
    time.sleep(0.001)