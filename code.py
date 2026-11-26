#
# PICOder - hybrid NKRO keyboard encoder focused on MAME 
# GP0 = layer hold; tap GP0 alone sends keymap[0] on release
#

#
# PICOder - hybrid NKRO + layer; maps from keymap.json
#

import time
import json
import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard, find_device
from adafruit_hid.keycode import Keycode

# ---------- load config ----------
KEYMAP_PATH = "keymap.json"

# Adafruit name aliases (configurator / JSON convenience)
_ALIASES = {
    "SPACE": "SPACEBAR",
    "RETURN": "ENTER",
    "ESC": "ESCAPE",
    "CTRL": "LEFT_CONTROL",
    "CONTROL": "LEFT_CONTROL",
    "ALT": "LEFT_ALT",
    "SHIFT": "LEFT_SHIFT",
    "GUI": "LEFT_GUI",
    "WIN": "LEFT_GUI",
    "CMD": "LEFT_GUI",
}


def name_to_keycode(name):
    if name is None or name == "" or name == "None" or name == "NONE":
        return None
    name = str(name).strip().upper().replace(" ", "_")
    name = _ALIASES.get(name, name)
    if not hasattr(Keycode, name):
        print("Unknown keycode in keymap.json:", name)
        return None
    return getattr(Keycode, name)


def pin_name_to_board(name):
    # "GP0" -> board.GP0
    name = str(name).strip().upper()
    if not hasattr(board, name):
        raise ValueError("Unknown pin in keymap.json: " + name)
    return getattr(board, name)


with open(KEYMAP_PATH, "r") as f:
    cfg = json.load(f)

LAYER_PIN_INDEX = int(cfg.get("layer_pin_index", 0))
TAP_HOLD_S = float(cfg.get("tap_hold_s", 0.03))

key_pins = tuple(pin_name_to_board(p) for p in cfg["pins"])
keymap = tuple(name_to_keycode(n) for n in cfg["keymap"])
layer_keymap = tuple(name_to_keycode(n) for n in cfg["layer_keymap"])

if not (len(key_pins) == len(keymap) == len(layer_keymap)):
    raise ValueError("pins, keymap, and layer_keymap must be the same length")

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


print("Picoder ready — loaded", KEYMAP_PATH)

while True:
    while True:
        ev = keys.events.get()
        if ev is None:
            break

        idx = ev.key_number

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