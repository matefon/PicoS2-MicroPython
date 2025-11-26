# PicoS2-MicroPython

A robust PS/2 to USB HID keyboard converter for the Raspberry Pi Pico (RP2040), written in MicroPython.

## Features

- **PIO-based PS/2 Driver**: Uses the RP2040's PIO state machines for precise, non-blocking signal reading.
- **Asyncio Core**: Fully asynchronous event loop handles USB reports and PS/2 events concurrently.
- **Robust Error Handling**: Includes a watchdog to restart the PS/2 reader if it crashes and file-based logging (`log.txt`).
- **Status Feedback**: Uses the RP2040-Zero's onboard NeoPixel for visual status indication.
- **Full Mapping**: Supports standard keys, modifiers, navigation clusters, and numpad.

## Hardware

- **Board**: Raspberry Pi Pico or RP2040-Zero (Code configured for RP2040-Zero NeoPixel on GPIO 16).
- **PS/2 Connector**: Female PS/2 socket or breakout.
- **Level Shifting**: PS/2 is 5V, Pico is 3.3V. While the Pico inputs are often tolerant, a level shifter or voltage divider is recommended for safety.

### Wiring (Default)

| PS/2 Pin | Pico Pin | Function |
|----------|----------|----------|
| 5V       | VBUS     | Power    |
| GND      | GND      | Ground   |
| CLK      | GPIO 0   | Clock    |
| DATA     | GPIO 1   | Data     |

*Note: Pins can be changed in `main.py`.*

## Installation

1. **Flash MicroPython**: Install the latest MicroPython firmware on your RP2040.
2. **Install Dependencies**:
   You need the `usb-device-keyboard` library.
   ```python
   import mip
   mip.install("usb-device-keyboard")
   ```
   *(Or copy the library manually if offline)*
3. **Copy Files**: Upload the following files to the root of the Pico:
   - `main.py`
   - `ps2_pio.py`
   - `keymap.py`
   - `ps2_constants.py`
   - `usb_constants.py`
   - `simple_test.py` (needed only if testing the PS/2 wiring)
4. *Change key definitions (optional)*: User friendly key/macro system defined in `keymap.py`.
5. **Run**: Reset the board. It will wait 2 seconds (flashing yellow) before starting.



## Status LED Codes (RP2040-Zero)

| Color | Pattern | Meaning |
|-------|---------|---------|
| 🟡 Yellow | Flashing | Initialization / Waiting |
| 🟢 Green | Solid (Dim) | Ready / Idle |
| 🟢 Green | Flash (Bright) | Key Press Detected |
| 🔴 Red | Solid | USB Error (Check connection) |
| 🔴 Red | Flashing | PS/2 Error (Unknown key/Protocol error) |

## Debugging

- **Log File**: Errors are written to `log.txt` on the device. Not cleared on startup unless `DEBUG = True` in `main.py`.
- **Debug Mode**: Set `DEBUG = True` in `main.py` to log all events, not just errors. Clears on startup.

## Some info about PS/2 protocol

- [hungarian](http://www.vfx.hu/info/atkeyboard.html)
- [english 1](https://www.avrfreaks.net/sites/default/files/PS2%20Keyboard.pdf)
- [english 2](https://karooza.net/how-to-interface-a-ps2-keyboard)

## Working keys

All keys are read correctly from the PS/2 keyboard.

Not working with HID right now: F13-F24 extended function keys. These are great for macro use in apps that support them, as they cannot be accessed from most keyboards.

**I accept any help and suggestions.**

*Disclaimer: this project was created using AI (Claude Sonnet 4.5 and Google Gemini 3 Pro (Preview) in VS Code).*
