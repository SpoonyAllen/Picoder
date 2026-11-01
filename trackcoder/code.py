# Trackcoder trackball and spinner encoder for the raspberry pi pico.
#changelog:
# 0.1a Basic happ trackball support
# 0.2 Supports up to 3 trackballs
# 0.3 Added mouse buttons, sensitivity multiplier and inverting X and Y axis

import board
import digitalio
import rotaryio
import time
import usb_hid
from adafruit_hid.mouse import Mouse

# ============================================================
# HAPP TRACKBALL WIRING
# ============================================================
#Trackball 1
#X Horizontal A Yellow → GP0  
#X Horizontal B Green → GP1  
#Y Vertical A Blue → GP2  
#Y Vertical B Purple → GP3  
#+5volt V → VBUS  
#GND → GND
#Trackball 2
#X Horizontal A Yellow → GP4  
#X Horizontal B Green → GP5  
#Y Vertical A Blue → GP6  
#Y Vertical B Purple → GP7  
#+5volt V → VBUS  
#GND → GND
#Trackball 3
#X Horizontal A Yellow → GP8  
#X Horizontal B Green → GP9  
#Y Vertical A Blue → GP10  
#Y Vertical B Purple → GP11  
#+5volt V → VBUS  
#GND → GND
# EC11 style Y-axis scroll wheel encoder
#EC11 A → GP12
#EC11 B → GP13
#EC11 BUTTON → GP14

# Optional mouse buttons
#LEFT → GP15
#RIGHT → GP16
#MIDDLE → GP17

# ============================================================

# ============================================================
# CONFIGURATION
# ============================================================

SCALE = 2                  # Trackball sensitivity
INVERT_X = False
INVERT_Y = False

SCROLL_SCALE = 1           # Scroll units per EC11 click
INVERT_SCROLL = False

# Three trackballs: (x_a, x_b, y_a, y_b)
TRACKBALLS = [
    (board.GP0, board.GP1, board.GP2, board.GP3),   # Trackball 1
    (board.GP4, board.GP5, board.GP6, board.GP7),   # Trackball 2
    (board.GP8, board.GP9, board.GP10, board.GP11), # Trackball 3
]

# EC11 encoder
EC11_A = board.GP12
EC11_B = board.GP13

# Optional EC11 push button (active low)
EC11_BUTTON = board.GP14

# Optional mouse buttons
LEFT_BUTTON_PIN   = board.GP15
RIGHT_BUTTON_PIN  = board.GP16
MIDDLE_BUTTON_PIN = board.GP17

# ============================================================

mouse = Mouse(usb_hid.devices)

# --- Create trackball encoders ---
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

# --- EC11 scroll encoder ---
scroll_enc = rotaryio.IncrementalEncoder(EC11_A, EC11_B)
last_scroll = scroll_enc.position

def make_button(pin):
    if pin is None:
        return None
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    return btn

left_btn   = make_button(LEFT_BUTTON_PIN)
right_btn  = make_button(RIGHT_BUTTON_PIN)
middle_btn = make_button(MIDDLE_BUTTON_PIN)
ec11_btn   = make_button(EC11_BUTTON)

print(f"Ready: {len(encoders)} trackballs + EC11 scroll")

while True:
    # ===== Trackball movement (sum of all 3) =====
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

    dx = total_dx * SCALE
    dy = total_dy * SCALE

    # ===== EC11 scroll =====
    pos = scroll_enc.position
    dscroll = pos - last_scroll
    last_scroll = pos
    if INVERT_SCROLL:
        dscroll = -dscroll
    wheel = dscroll * SCROLL_SCALE

    # ===== Buttons =====
    if left_btn is not None:
        if not left_btn.value:
            mouse.press(Mouse.LEFT_BUTTON)
        else:
            mouse.release(Mouse.LEFT_BUTTON)

    if right_btn is not None:
        if not right_btn.value:
            mouse.press(Mouse.RIGHT_BUTTON)
        else:
            mouse.release(Mouse.RIGHT_BUTTON)

    if middle_btn is not None:
        if not middle_btn.value:
            mouse.press(Mouse.MIDDLE_BUTTON)
        else:
            mouse.release(Mouse.MIDDLE_BUTTON)

    # Optional: use EC11 button as middle click
    if ec11_btn is not None:
        if not ec11_btn.value:
            mouse.press(Mouse.MIDDLE_BUTTON)
        else:
            mouse.release(Mouse.MIDDLE_BUTTON)

    # ===== Send report =====
    if dx or dy or wheel:
        mouse.move(x=dx, y=dy, wheel=wheel)

    time.sleep(0.001)
