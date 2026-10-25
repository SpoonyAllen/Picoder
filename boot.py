# boot.py — hybrid NKRO + boot-compatible keyboard
import usb_hid

HYBRID_REPORT_BYTES = 24
REPORT_ID = 0x04

hybrid_keyboard_descriptor = bytes((
    0x05, 0x01,                     # Usage Page (Generic Desktop)
    0x09, 0x06,                     # Usage (Keyboard)
    0xA1, 0x01,                     # Collection (Application)
    0x85, REPORT_ID,                #   Report ID

    # Modifier byte
    0x75, 0x01,
    0x95, 0x08,
    0x05, 0x07,
    0x19, 0xE0,
    0x29, 0xE7,
    0x15, 0x00,
    0x25, 0x01,
    0x81, 0x02,

    # LED output
    0x95, 0x05,
    0x75, 0x01,
    0x05, 0x08,
    0x19, 0x01,
    0x29, 0x05,
    0x91, 0x02,
    0x95, 0x01,
    0x75, 0x03,
    0x91, 0x03,

    # 7-byte padding so first 8 payload bytes look like a boot report
    0x95, 0x38,                     # 56 bits = 7 bytes
    0x75, 0x01,
    0x81, 0x01,                     # Constant

    # NKRO bitmap (16 bytes)
    0x95, (HYBRID_REPORT_BYTES - 8) * 8,
    0x75, 0x01,
    0x15, 0x00,
    0x25, 0x01,
    0x05, 0x07,
    0x19, 0x00,
    0x29, (HYBRID_REPORT_BYTES - 8) * 8 - 1,
    0x81, 0x02,

    0xC0,
))

hybrid_keyboard = usb_hid.Device(
    report_descriptor=hybrid_keyboard_descriptor,
    usage_page=0x01,
    usage=0x06,
    report_ids=(REPORT_ID,),
    in_report_lengths=(HYBRID_REPORT_BYTES,),
    out_report_lengths=(1,),
)

usb_hid.enable(
    (
        hybrid_keyboard,
        usb_hid.Device.MOUSE,
        usb_hid.Device.CONSUMER_CONTROL,
    )
)
print("enabled HID with hybrid NKRO keyboard")