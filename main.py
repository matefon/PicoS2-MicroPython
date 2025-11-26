# MicroPython PS/2 to USB HID Converter
# Full Implementation

import uasyncio as asyncio
import usb.device
from usb.device.keyboard import KeyboardInterface
from ps2_pio import PS2Keyboard
from machine import Pin
import time
import sys
import neopixel

# --- DEBUG LOGGING ---
DEBUG = False

# --- STATUS LED CONTROLLER ---
class StatusController:
    def __init__(self):
        # RP2040-Zero NeoPixel is on GPIO 16
        self.np = neopixel.NeoPixel(Pin(16), 1)
        self.state = "INIT" # INIT, READY, USB_ERR, PS2_ERR
        self.last_act = 0
        
    def trigger_activity(self):
        self.last_act = time.ticks_ms()
        
    def trigger_error(self, type):
        self.state = type
        self.last_act = time.ticks_ms()
        
    def set_state(self, s):
        self.state = s
        
    async def run(self):
        while True:
            try:
                if self.state == "INIT":
                    # Flash Yellow
                    self.np[0] = (20, 20, 0); self.np.write()
                    await asyncio.sleep(0.2)
                    self.np[0] = (0, 0, 0); self.np.write()
                    await asyncio.sleep(0.2)
                    
                elif self.state == "USB_ERR":
                    # Solid Red
                    self.np[0] = (50, 0, 0); self.np.write()
                    await asyncio.sleep(0.2)
                    
                elif self.state == "PS2_ERR":
                    # Flash Red
                    self.np[0] = (50, 0, 0); self.np.write()
                    await asyncio.sleep(0.1)
                    self.np[0] = (0, 0, 0); self.np.write()
                    await asyncio.sleep(0.1)
                    # Auto-clear error after 1s
                    if time.ticks_diff(time.ticks_ms(), self.last_act) > 1000:
                        self.state = "READY"
                        
                elif self.state == "READY":
                    # Solid Green (Dim), Flash Bright on Activity
                    if time.ticks_diff(time.ticks_ms(), self.last_act) < 100:
                        self.np[0] = (0, 50, 0) # Brighter Green
                    else:
                        self.np[0] = (0, 5, 0)   # Dim Green
                    self.np.write()
                    await asyncio.sleep(0.05)
            except:
                await asyncio.sleep(1)

STATUS = StatusController()

def log(msg, error=False):
    print(msg)
    if DEBUG or error:
        try:
            with open("log.txt", "a") as f:
                f.write(f"{time.ticks_ms()}: {msg}\n")
        except:
            pass

# Clear log on startup
if DEBUG:
    try:
        with open("log.txt", "w") as f:
            f.write("--- STARTUP ---\n")
    except:
        pass

# --- CONFIGURATION ---
PS2_CLK_PIN = 0
PS2_DATA_PIN = 1

# --- PS/2 CONSTANTS ---
from ps2_constants import PS2

# --- USB HID CONSTANTS ---
from usb_constants import USB

# --- KEY ACTION DEFINITION AND MAPPINGS ---
from keymap import KEY_MAP

# --- LOGIC ---

class PS2ToUSB(KeyboardInterface):
    def __init__(self):
        super().__init__()
        self.pressed_keys = set()
        self.last_sent_keys = []
        self.error_state = False

    def update_key(self, action, pressed):
        if action is None: return
        STATUS.trigger_activity()
        
        changed = False
        for code in action.codes:
            if action.toggle:
                if pressed:
                    if code in self.pressed_keys: self.pressed_keys.discard(code)
                    else: self.pressed_keys.add(code)
                    changed = True
            else:
                if pressed:
                    if code not in self.pressed_keys:
                        self.pressed_keys.add(code)
                        changed = True
                else:
                    if code in self.pressed_keys:
                        self.pressed_keys.discard(code)
                        changed = True
        
        if changed: self.flush_keys()

    def flush_keys(self):
        if not self.is_open(): return
        try:
            keys_list = list(self.pressed_keys)
            keys_list.sort()
            if keys_list != self.last_sent_keys:
                # print(f"Sending: {keys_list}")
                self.send_keys(keys_list)
                self.last_sent_keys = keys_list
                self.error_state = False
                if STATUS.state == "USB_ERR": STATUS.set_state("READY")
        except Exception as e:
            log(f"USB Error: {e}", error=True)
            STATUS.set_state("USB_ERR")
            self.pressed_keys.clear()
            self.last_sent_keys = []
            try: self.send_keys([])
            except: pass
            self.error_state = True

async def main():
    log("Starting PS/2 to USB HID Bridge...")
    asyncio.create_task(STATUS.run())
    
    usb_kb = None
    try:
        usb_kb = PS2ToUSB()
        usb.device.get().init(usb_kb, builtin_driver=True)
    
        log("Waiting for USB enumeration...")
        while not usb_kb.is_open():
            await asyncio.sleep(1)
            # log(".", end="") # Don't spam log file
        log("\nUSB Keyboard Ready")
        STATUS.set_state("READY")
        
        def ps2_callback(scancode, pressed, extended):
            # print(f"PS2: {hex(scancode)} {pressed}")
            key_tuple = (scancode, extended)
            
            # Debug Windows Keys specifically
            if scancode in [0x1F, 0x27]:
                log(f"WIN KEY: {hex(scancode)} Ext:{extended} Pressed:{pressed}", error=True)

            action = KEY_MAP.get(key_tuple)
            if action:
                try:
                    usb_kb.update_key(action, pressed)
                except Exception as e:
                    log(f"Update Key Error: {e}", error=True)
                    STATUS.set_state("USB_ERR")
            else:
                log(f"Unknown: {hex(scancode)} Ext:{extended}", error=True)
                STATUS.trigger_error("PS2_ERR")

        log("Initializing PS/2...")
        ps2_kb = PS2Keyboard(clk_pin=PS2_CLK_PIN, data_pin=PS2_DATA_PIN, callback=ps2_callback)
        ps2_task = asyncio.create_task(ps2_kb.read_loop())
        
        log("Main loop running")
        while True:
            if ps2_task.done():
                log("PS/2 Loop Died! Restarting...", error=True)
                try:
                    exc = ps2_task.exception()
                    if exc: log(f"PS/2 Crash: {exc}", error=True)
                except: pass
                ps2_task = asyncio.create_task(ps2_kb.read_loop())
            await asyncio.sleep(1)
            
    except Exception as e:
        log(f"Main Error: {e}", error=True)
        STATUS.set_state("USB_ERR")
        if usb_kb:
            try:
                log("Clearing USB keys due to error...")
                usb_kb.send_keys([])
            except:
                pass
        raise e

if __name__ == "__main__":
    log("Waiting 2 seconds before starting USB... Press Ctrl+C to stop.")
    time.sleep(2)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Stopped by user")
    except Exception as e:
        log(f"CRITICAL ERROR: {e}", error=True)
        import sys
        sys.print_exception(e)
        # Blink error code
        led = Pin(Pin.board.LED, Pin.OUT) if hasattr(Pin, 'board') else Pin(25, Pin.OUT)
        while True:
            led.toggle()
            time.sleep(0.1)
