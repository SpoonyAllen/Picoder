#
# PICOder - A simple keyboard encoder for MAME made by KLOV user DonPanetta
#
# Requires CircuitPython bootloader and Libraries installed first.
#
# Heavily based on NKRO code by Jeff Epler. Keypad to keycode transition examples by Dan Helbert.
# 
#I'm not good at this stuff at all so i left lots of comments in case you can't make sense of my crappy code.

# a sleep timeout for computing device to boot past bios/uefi. This workaround is used to get past the hybrid device IDs that are currently lacking in curcuitpython.
#You can omit this if your computer supports NKRO keyboard at bios/uefi.
import time
time.sleep(12)

# import curcuitpython libraries
import keypad
import board
import usb_hid
from adafruit_hid.keyboard import Keyboard, find_device
from adafruit_hid.keycode import Keycode

# this routine declares all the GPIO pins used
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
    board.GP28, #LED Line. This line controls the onboard LED as long as your code supports it. You will never see this blink in your arcade cabinet. Besides, we will steal it cuz we need as many pins as possible.
)

# We need to map which keyboard keys will go to the the above hardware pins. Keys are currently mapped to MAME default keys. This is where you can edit which keys are associated with each pin.
#see https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode for a complete list of keycodes. 
keymap = (
    Keycode.ONE,            #pin GP0 #player1 start
    Keycode.FIVE,           #pin GP1 #player1 coin
    Keycode.UP_ARROW,       #pin GP2 #player1 up
    Keycode.DOWN_ARROW,     #pin GP3 #player1 down
    Keycode.LEFT_ARROW,     #pin GP4  #player1 left
    Keycode.RIGHT_ARROW,    #pin GP5  #player1 right
    Keycode.LEFT_CONTROL,   #pin GP6  #player1 button1
    Keycode.LEFT_ALT,       #pin GP7 #player1 button2
    Keycode.SPACEBAR,       #pin GP8  #player1 button3
    Keycode.LEFT_SHIFT,     #pin GP9  #player1 button4
    Keycode.Z,              #pin GP10  #player1 button5
    Keycode.X,              #pin GP11 #player1 button6
    Keycode.TWO,            #pin GP12  #player2 start
    Keycode.SIX,            #pin GP13  #player2 coin
    Keycode.R,              #pin GP14  #player2 up
    Keycode.F,              #pin GP15  #player2 down
    Keycode.D,              #pin GP16 #player2 left
    Keycode.G,              #pin GP17 #player2 right
    Keycode.A,              #pin GP18 #player2 button1
    Keycode.S,              #pin GP19 #player2 button2
    Keycode.Q,              #pin GP20 #player2 button3
    Keycode.W,              #pin GP21 #player2 button4
    Keycode.I,              #pin GP22 #player2 button5
    Keycode.K,              #pin GP26 #player2 button6
    Keycode.ESCAPE,         #pin GP27 #Exit
    Keycode.TAB,            #pin GP28 #MAME menu
)

#Keypress routines. Don't touch anything below unless you know what you're doing.
keys = keypad.Keys(key_pins, value_when_pressed=False, pull=True)

class BitmapKeyboard(Keyboard):
    def __init__(self, devices):
        device = find_device(devices, usage_page=0x1, usage=0x6)

        try:
            device.send_report(b'\0' * 16)
        except ValueError:
            print("found keyboard, but it did not accept a 16-byte report. check that boot.py is installed properly")

        self._keyboard_device = device

        # report[0] modifiers
        # report[1:16] regular key presses bitmask
        self.report = bytearray(16)

        self.report_modifier = memoryview(self.report)[0:1]
        self.report_bitmap = memoryview(self.report)[1:]

    def _add_keycode_to_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] |= modifier
        else:
            self.report_bitmap[keycode >> 3] |= 1 << (keycode & 0x7)

    def _remove_keycode_from_report(self, keycode):
        modifier = Keycode.modifier_bit(keycode)
        if modifier:
            # Set bit for this modifier.
            self.report_modifier[0] &= ~modifier
        else:
            self.report_bitmap[keycode >> 3] &= ~(1 << (keycode & 0x7))
        
    def release_all(self):
        for i in range(len(self.report)):
            self.report[i] = 0
        self._keyboard_device.send_report(self.report)

kbd = BitmapKeyboard(usb_hid.devices)

while True:
    ev = keys.events.get()
    if ev is not None:
        key = keymap[ev.key_number]
        if ev.pressed:
            kbd.press(key)
        else:
            kbd.release(key)
