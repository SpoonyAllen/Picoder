import board
import keypad
import usb_hid
from adafruit_hid.keyboard import Keyboard, find_device
from adafruit_hid.keycode import Keycode

# we need to initialize each pin. do not change this unless you want to change which pins to enable and disable.
key_pins = (
    board.GP0,   #UART TX Line. This is a serial transmit line. We will steal it cuz we need as many pins as possible.
    board.GP1,   #UART RX Line. This is a serial recieve line. We will steal it cuz we already stole the transmit line lol
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
#   board.GP28, #GP28 controls Pico LED activity. You can steal it if you absolutely need one more input. I left out any LED input routines from the code just for this.
)


# We need to map which keyboard keys will go to the the above hardware pins. Keys are currently mapped to MAME default keys.
keymap = (
    Keycode.ONE,     #player1 start
    Keycode.FIVE,     #player1 coin
    Keycode.UP_ARROW,     #player1 up
    Keycode.DOWN_ARROW,     #player1 down
    Keycode.LEFT_ARROW,     #player1 left
    Keycode.RIGHT_ARROW,     #player1 right
    Keycode.LEFT_CONTROL,     #player1 button1
    Keycode.LEFT_ALT,     #player1 button2
    Keycode.SPACEBAR,     #player1 button3
    Keycode.LEFT_SHIFT,     #player1 button4
    Keycode.Z,     #player1 button5
    Keycode.X,     #player1 button6
    Keycode.TWO,     #player2 start
    Keycode.SIX,     #player2 coin
    Keycode.R,     #player2 up
    Keycode.F,     #player2 down
    Keycode.D,     #player2 left
    Keycode.G,     #player2 right
    Keycode.A,     #player2 button1
    Keycode.S,     #player2 button2
    Keycode.Q,     #player2 button3
    Keycode.W,     #player2 button4
    Keycode.I,     #player2 button5
    Keycode.K,     #player2 button6
    Keycode.ESCAPE,     #Exit
)

keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)


class HybridKeyboard(Keyboard):
    def __init__(self, devices):
        device = find_device(devices, usage_page=0x01, usage=0x06)

        try:
            device.send_report(b"\0" * 24)
            print("OK: 24-byte report accepted")
        except ValueError as e:
            print("ERROR: device rejected 24-byte report:", e)
            raise

        self._keyboard_device = device
        self.report = bytearray(24)
        # [0] modifiers | [1] reserved | [2:8] boot key slots | [8:24] NKRO bitmap
        self.report_modifier = memoryview(self.report)[0:1]
        self.report_keys = memoryview(self.report)[2:8]
        self.report_bitmap = memoryview(self.report)[8:]

    def _add_keycode_to_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] |= modifier
            return

        # Boot slots (first 6 non-modifier keys)
        for i in range(6):
            if self.report_keys[i] == 0:
                self.report_keys[i] = keycode
                break
            if self.report_keys[i] == keycode:
                break
        else:
            # Rotate oldest out
            for i in range(5):
                self.report_keys[i] = self.report_keys[i + 1]
            self.report_keys[5] = keycode

        # NKRO bitmap
        self.report_bitmap[keycode >> 3] |= 1 << (keycode & 0x07)

    def _remove_keycode_from_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            self.report_modifier[0] &= ~modifier
            return

        j = 0
        for i in range(6):
            pressed = self.report_keys[i]
            if pressed == 0:
                break
            if pressed == keycode:
                continue
            self.report_keys[j] = pressed
            j += 1
        while j < 6:
            self.report_keys[j] = 0
            j += 1

        self.report_bitmap[keycode >> 3] &= ~(1 << (keycode & 0x07))

    def release_all(self):
        for i in range(len(self.report)):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)


print("Looking for keyboard device...")
print("usb_hid.devices:", usb_hid.devices)
kbd = HybridKeyboard(usb_hid.devices)
print("HybridKeyboard ready")

while True:
    ev = keys.events.get()
    if ev is not None:
        key = keymap[ev.key_number]
        print("pin", ev.key_number, "keycode", key, "pressed" if ev.pressed else "released")
        if ev.pressed:
            kbd.press(key)
        else:
            kbd.release(key)