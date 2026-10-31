This is a low cost, low-overhead keyboard encoder script for the Raspberry Pi Pico RP2040 devices. It is based on original code examples from Jeff Epler and the original Picoder code from Don Panetta at the KLOV message board. It has been updated by me to support the latest circuitphython and hybrid boot+NKRO HID descriptor. It will allow you to have a fully featured encoder for your MAME arcade or indie game project without the high cost of a Ultimarc Ipac. The latest build also includes a shifted function to add additional keys for utility functions, shortcuts etc which now brings it closer to full Ipac functionality. The code is written in Python using the circuitpython bootloader and libraries. You will need to install the CircuitPython boot-loader then write the Picoder code and libraries. It's a small process so please follow the instructions carefully.





Quick instructions

-Download the picoder UF2 firmware.

-Hold the BOOTSEL button down on your raspberry pi pico and then plug your Pico into your PC using a USB cable. Your Pico should appear as a usb mass storage device on your PC.

-Drag the picoder UF2 firmware into your Pico drive folder. Your Pico may restart once or twice and then reappear. Picoder is already configured using default MAME keys.

Manual Instructions:
-Download the CircuitPython 10x UF2 bootloader from https://circuitpython.org/board/raspberry_pi_pico/

-Hold the BOOTSEL button down on your raspberry pi pico and then plug your Pico into your PC using a USB cable. Your Pico should appear as a usb mass storage device on your PC.

-Drag the CircuitPython UF2 firmware into your Pico drive folder. Your Pico may restart once or twice and then reappear as a mass storage device with different folders.

-Download Picoder, decompress and dump the contents of the folder into the root of your Pico drive. The Picoder zip file already contains the needed external circuitpython HID libraries. Your PC should ask if you would like to overwrite files. Click yes. Your Pico should reset. You can confirm that BOOT+NKRO descriptor is enabled by opening the boot\_out.txt. The string "enabled HID with hybrid NKRO keyboard" should appear.

See provided picoder_pinout.jpg for the standard corresponding pins. You can test your keys and Rollover code by using Microsoft's Keyboard Ghosting Demo
https://www.microsoft.com/applied-sciences/projects/anti-ghosting-demo

Editing keys:
&#x20;   Open code.py and find the section entitled #EDIT YOUR NORMAL KEYS HERE!. There you will find the normal/standard keys corresponding to each pin. Directly below that is your shifted layer keys. Edit these to add additional functionality for your shifted keys function. modifying the keycodes requires using the circuitpythons keycodes. See circuitpythons keycode.py for more keycodes.
https://github.com/adafruit/Adafruit_CircuitPython_HID/blob/main/adafruit_hid/keycode.py

![](picoder_pinout.jpg)
