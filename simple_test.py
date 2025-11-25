"""
Minimal PS/2 keyboard test - prints raw scancodes
Upload ps2_pio.py first, then run this file
"""

import uasyncio as asyncio
from ps2_pio import PS2Keyboard

# === UPDATE THESE PINS ===
CLK_PIN = 0
DATA_PIN = 1
# =========================

def on_key(scancode, pressed, extended):
    """Simple callback - just print the event"""
    print(f"{'▼' if pressed else '▲'} 0x{scancode:02X} {'[EXT]' if extended else ''}")

async def main():
    print("PS/2 Keyboard Test")
    print(f"CLK=GPIO{CLK_PIN}, DATA=GPIO{DATA_PIN}")
    print("-" * 40)
    
    kb = PS2Keyboard(CLK_PIN, DATA_PIN, on_key)
    asyncio.create_task(kb.read_loop())
    
    print("Ready - press keys!\n")
    
    while True:
        await asyncio.sleep(60)

asyncio.run(main())
