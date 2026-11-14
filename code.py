#
# PICOder - hybrid NKRO keyboard encoder focused on MAME 
# GP0 = layer hold; tap GP0 alone sends keymap[0] on release
#

import time
import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard, find_device
from adafruit_hid.keycode import Keycode

# How long a "tap" key is held so the host sees it (seconds)
TAP_HOLD_S = 0.03

#Set which pin will be used for your shift function
LAYER_PIN_INDEX = 0

# we need to initialize each pin. do not change this unless you want to change which pins to enable and disable.
key_pins = (
    board.GP0,   # layer hold / tap for normal key
    board.GP1,
    board.GP2,
    board.GP3,
    board.GP4,
    board.GP5,
    board.GP6,
    board.GP7,
    board.GP8,
    board.GP9,
    board.GP10,
    board.GP11,
    board.GP12,
    board.GP13,
    board.GP14,
    board.GP15,
    board.GP16,
    board.GP17,
    board.GP18,
    board.GP19,
    board.GP20,
    board.GP21,
    board.GP22,
    board.GP26,
    board.GP27,
    board.GP28,
)

#EDIT YOUR NORMAL KEYS HERE! We need to map which keyboard keys will go to the the above hardware pins. Keys are currently mapped to MAME default keys.
keymap = (
    Keycode.ONE,          #GP0 player1 start - also default shifted layer key
    Keycode.FIVE,         #GP1 player1 coin
    Keycode.UP_ARROW,     #GP2 player1 up
    Keycode.DOWN_ARROW,   #GP3 player1 down
    Keycode.LEFT_ARROW,   #GP4 player1 left
    Keycode.RIGHT_ARROW,  #GP5 player1 right
    Keycode.LEFT_CONTROL, #GP6 player1 button1
    Keycode.LEFT_ALT,     #GP7 player1 button2
    Keycode.SPACEBAR,     #GP8 player1 button3
    Keycode.LEFT_SHIFT,   #GP9 player1 button4
    Keycode.Z,            #GP10 player1 button5
    Keycode.X,            #GP11 player1 button6
    Keycode.TWO,          #GP12 player2 start
    Keycode.SIX,          #GP13 player2 coin
    Keycode.R,            #GP14 player2 up
    Keycode.F,            #GP15 player2 down
    Keycode.D,            #GP16 player2 left
    Keycode.G,            #GP17 player2 right
    Keycode.A,            #GP18 player2 button1
    Keycode.S,            #GP19 player2 button2
    Keycode.Q,            #GP20 player2 button3
    Keycode.W,            #GP21 player2 button4
    Keycode.I,            #GP22 player2 button5
    Keycode.K,            #GP26 player2 button6
    Keycode.ESCAPE,       #GP27 Exit
    Keycode.TAB,          #GP28 Tab
)

#EDIT YOUR SHIFTED KEYS HERE! We need to map which keyboard keys will go to the the above hardware pins. Keys are currently mapped to MAME default keys. Standard shift key is GP0
layer_keymap = (
    None,                 # GP0  — never sends from shifted layer table
    Keycode.F1,           # GP1
    Keycode.F2,           # GP2
    Keycode.F3,           # GP3
    Keycode.F4,           # GP4
    Keycode.F5,           # GP5
    Keycode.F6,           # GP6
    Keycode.F7,           # GP7
    Keycode.F8,           # GP8
    Keycode.F9,           # GP9
    Keycode.F10,          # GP10
    Keycode.F11,          # GP11
    Keycode.F12,          # GP12
    Keycode.P,            # GP13
    Keycode.ESCAPE,       # GP14
    Keycode.U,            # GP15
    Keycode.Y,            # GP16
    Keycode.T,            # GP17
    Keycode.H,            # GP18
    Keycode.J,            # GP19
    Keycode.L,            # GP20
    Keycode.M,            # GP21
    Keycode.N,            # GP22
    Keycode.B,            # GP26
    Keycode.ENTER,        # GP27
    Keycode.BACKSPACE,    # GP28
)

# do not edit the functions below unless you know what you are doing
assert len(key_pins) == len(keymap) == len(layer_keymap)

keys = keypad.Keys(
    key_pins,
    value_when_pressed=False,
    pull=True,
    interval=0.02,
    max_events=64,
)


class HybridKeyboard(Keyboard):
    def __init__(self, devices):
        device = find_device(devices, usage_page=0x01, usage=0x06)
        try:
            device.send_report(b"\0" * 24)
        except ValueError:
            print("ERROR: device rejected 24-byte report — check boot.py")
            raise

        self._keyboard_device = device
        self.report = bytearray(24)
        self.report_modifier = memoryview(self.report)[0:1]
        self.report_keys = memoryview(self.report)[2:8]
        self.report_bitmap = memoryview(self.report)[8:]

    def _add_keycode_to_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] |= modifier
            return

        for i in range(6):
            if self.report_keys[i] == 0:
                self.report_keys[i] = keycode
                break
            if self.report_keys[i] == keycode:
                break
        else:
            for i in range(5):
                self.report_keys[i] = self.report_keys[i + 1]
            self.report_keys[5] = keycode

        self.report_bitmap[keycode >> 3] |= 1 << (keycode & 0x07)

    def _remove_keycode_from_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] &= ~modifier
            return

        j = 0
        for i in range(6):
            pressed_key = self.report_keys[i]
            if pressed_key == 0:
                break
            if pressed_key == keycode:
                continue
            self.report_keys[j] = pressed_key
            j += 1
        while j < 6:
            self.report_keys[j] = 0
            j += 1

        self.report_bitmap[keycode >> 3] &= ~(1 << (keycode & 0x07))

    def release_all(self):
        for i in range(len(self.report)):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)


kbd = HybridKeyboard(usb_hid.devices)

pressed = [False] * len(key_pins)
layer_used = False
active_keycodes = [None] * len(key_pins)


def layer_is_held():
    return pressed[LAYER_PIN_INDEX]


while True:
    while True:
        ev = keys.events.get()
        if ev is None:
            break

        idx = ev.key_number

        # ----- Layer key (GP0) -----
        if idx == LAYER_PIN_INDEX:
            if ev.pressed:
                pressed[idx] = True
                layer_used = False
            else:
                pressed[idx] = False
                if not layer_used:
                    tap_key = keymap[LAYER_PIN_INDEX]
                    if tap_key is not None:
                        kbd.press(tap_key)
                        time.sleep(TAP_HOLD_S)
                        kbd.release(tap_key)
                layer_used = False
            continue

        # ----- Other keys -----
        if ev.pressed:
            pressed[idx] = True
            if layer_is_held():
                layer_used = True
                key = layer_keymap[idx]
            else:
                key = keymap[idx]
            if key is None:
                continue
            active_keycodes[idx] = key
            kbd.press(key)
        else:
            pressed[idx] = False
            key = active_keycodes[idx]
            if key is not None:
                kbd.release(key)
                active_keycodes[idx] = None
