This is a low cost, low-overhead keyboard encoder script for the Raspberry Pi Pico RP2040 devices. It is based on original code examples from Jeff Epler and the original Picoder code from Don Panetta at the KLOV message board. It has been updated by me to support the latest circuitphython and hybrid boot+NKRO HID descriptor. It will allow you to run a no-frills, full 2 player six button setup. The code is written in Python using the circuitpython bootloader and libraries. You will need to install the CircuitPython boot-loader, CircuitPython libraries and then overwrite with the Picoder code and libraries to get this going. It's a small process so please follow the instructions carefully.





Instructions:



&#x20;   Download the CircuitPython 10x UF2 bootloader from https://circuitpython.org/board/raspberry\_pi\_pico/

&#x20;   Hold the BOOTSEL button down on your raspberry pi pico and then plug your Pico into your PC using a USB cable. Your Pico should appear as a usb mass storage device on your PC.



&#x20;   Drag the CircuitPython UF2 firmware into your Pico drive folder. Your Pico may restart once or twice and then reappear as a mass storage device with different folders.

&#x20;   Now you need to install the CircuitPython libraries. You can download them at https://circuitpython.org/libraries . Scroll down to the Bundle for 7.x link and download the bundle. Decompress the contents and dump them to the root of your Pico drive.



&#x20;   Download Picoder, decompress and dump the contents of the folder into the root of your Pico drive. Your PC should ask if you would like to overwrite files. Click yes.

&#x20;   This last step is important. Standard HID descriptor only allows 6 simultaneous button presses. Picoder uses N-Key Rollover to get around this limitation. To enable N-Key Rollover you need to reset your Pico. See the default pinout image below to find the reset pin or Flip your Pico upside down and use a short piece of wire to short the 'RUN' pin to any ground on the board. Your Pico should reset. You can confirm that BOOT+NKRO descriptor is enabled by opening the boot\_out.txt. The string "enabled HID with hybrid NKRO keyboard" should appear.

See provided picoder_pinout.jpg for the standard corresponding pins. You can test your keys and Rollover code by using Microsoft's Keyboard Ghosting Demo

https://www.microsoft.com/applied-sciences/projects/anti-ghosting-demo

