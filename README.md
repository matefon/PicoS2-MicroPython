# PicoS2-MicroPython

A robust PS/2 to USB HID keyboard converter for the Raspberry Pi Pico (RP2040), written in MicroPython.

## Features

- **PIO-based PS/2 Driver**: Uses the RP2040's PIO state machines for precise, non-blocking signal reading.
- **Asyncio Core**: Fully asynchronous event loop handles USB reports and PS/2 events concurrently.
- **Robust Error Handling**: Includes a watchdog to restart the PS/2 reader if it crashes and file-based logging (`log.txt`).
- **Status Feedback**: Uses the RP2040-Zero's onboard NeoPixel for visual status indication.
- **Full Mapping**: Supports standard keys, modifiers, navigation clusters, and numpad.
- **Easy macro definitions**: Change macro definitions in `keymap.py` using Thonny.

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
   In case it fails:
   
   - Close Thonny
   - run `pipx run mpremote mip install usb-device-keyboard`
   
   *(Or copy the library manually if offline)*
3. **Copy Files**: Upload the following files to the root of the Pico:
   - `main.py`
   - `ps2_pio.py`
   - `keymap.py`
   - `ps2_constants.py`
   - `usb_constants.py`
   - `simple_test.py` (needed only if testing the PS/2 wiring)
4. *Change key definitions (optional)*: User friendly key/macro system defined in `keymap.py`. Edit in Thonny for example (hit `Stop/Restart Backend` until you see the terminal in which you could type).
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
- [english](https://karooza.net/how-to-interface-a-ps2-keyboard)

## Working keys

All keys are read correctly from the PS/2 keyboard.

Not working with HID right now (out of the box): F13-F24 extended function keys. These are great for macro use in apps that support them, as they cannot be accessed (and be pressed) from most keyboards. 

## Extended function keys (F13-F24)

This is a MicroPython HID limitation. In `micropython-lib/micropython/usb/usb-device-keyboard/usb/device/keyboard.py` the `_KEYBOARD_REPORT_DESC` is using `logical` and `usage maximum` of `101`. A value of `115` (`x73`) is needed for extended function keys to work.

How to fix:
- Close Thonny
- Install `mpy-cross` and `mpremote` with `pip` or `pipx`: `pipx install mpy-cross mpremote`
- *Optional, recommended*: Download latest `keyboard.py` from `https://github.com/micropython/micropython-lib/blob/master/micropython/usb/usb-device-keyboard/usb/device/keyboard.py` and copy this into the repo `lib` folder
- Run this in the repo `lib` folder: `mpy-cross keyboard.py`
- *Optional* Save original `keyboard.mpy`: `mpremote cp :lib/usb/device/keyboard.mpy original_keyboard.mpy` (you can revert by re-installing the library, see above)
- Copy the patched `keyboard.mpy`: `mpremote cp keyboard.mpy :lib/usb/device/keyboard.mpy`
- Reboot the Pico.
- Test the extended function keys (remember to change some key definitions first then reboot the Pico): `pipx install hid-tools` then run `hid-recorder`

Note: precompiled patched `keyboard.mpy` is available in the repo `lib` folder.

Note: on my KDE Ubuntu 25.10 system, extended function keys are interpreted differently (`F14` as `XF86Launch5`, you can check this with `xev -event keyboard` or `evtest`). You can try to fix this with assigning the keycode (the number xev showed you) to the key:

e.g. `xmodmap -e "keycode 184 = F14"` (not tested) or use `xkb`/`xmodmap`.



**I accept any help and suggestions.**

*Disclaimer: this project was created using AI (Claude Sonnet 4.5 and Google Gemini 3 Pro (Preview) in VS Code). This is hobby code, usage of AI speeds up development drastically.*
