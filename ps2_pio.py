# ps2_pio.py - PS/2 Keyboard decoder using PIO on Raspberry Pi Pico (MicroPython)

from machine import Pin
import rp2
import uasyncio as asyncio

# PS/2 protocol basics:
# - Clock: device-driven, 10-16 kHz
# - Data valid on falling clock edges
# - Frame: 1 start bit (0), 8 data bits (LSB first), 1 parity bit (odd), 1 stop bit (1)

@rp2.asm_pio(
    in_shiftdir=rp2.PIO.SHIFT_RIGHT,  # LSB first
    autopush=True,
    push_thresh=22,                   # Push after 22 bits (11 × 2 pins)
)
def ps2_reader():
    # PIO program to read PS/2 keyboard data
    # in_base (pin 0): CLK
    # in_base+1 (pin 1): DATA
    wrap_target()
    
    # Wait for idle state (CLK=1, DATA=1) to ensure clean frame start
    wait(1, pin, 0)           # Wait for CLK high
    wait(1, pin, 1)           # Wait for DATA high (idle)
    
    # Now wait for the start bit (CLK falling, DATA low)
    wait(0, pin, 0)           # Wait for CLK to fall (start bit)
    
    # Read first bit (start bit)
    in_(pins, 2)
    
    # Read remaining 10 bits
    set(x, 9)
    
    label("bitloop")
    wait(1, pin, 0)           # Wait for CLK high
    wait(0, pin, 0)           # Wait for CLK low (falling edge)
    in_(pins, 2)
    jmp(x_dec, "bitloop")
    
    # After 11 reads × 2 bits = 22 bits, autopush triggers
    wrap()


class PS2Keyboard:
    def __init__(self, clk_pin: int, data_pin: int, callback=None):
        print(f"Initializing PS2 keyboard with CLK={clk_pin}, DATA={data_pin}")
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.data = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        
        # Quick pin check
        # import time
        # time.sleep_ms(100)
        # clk_val = self.clk.value()
        # data_val = self.data.value()
        # print(f"Initial pin states: CLK={clk_val}, DATA={data_val}")
        # if clk_val == 0 or data_val == 0:
        #     print("WARNING: Pin is LOW! Check wiring and pull-ups.")
        
        # Configure PIO: DATA is pin 0, CLK is pin 1
        # We need CLK pin = DATA pin - 1 for PIO mapping
        # So swap them: use CLK as base, DATA as base+1
        if data_pin != clk_pin + 1:
            print(f"ERROR: DATA pin must be CLK + 1. You have CLK={clk_pin}, DATA={data_pin}")
            raise ValueError("Invalid pin configuration")
        
        self.sm = rp2.StateMachine(
            0,
            ps2_reader,
            freq=2_000_000,
            in_base=self.clk,     # Base is CLK, so pin 0=CLK, pin 1=DATA
        )
        
        self.sm.active(1)
        
        # Parser states
        self.extended = False
        self.break_code = False
        self.pause_state = 0  # 0=Idle, 1=E1 seen, etc.

        # Callback: callback(scancode, pressed, extended)
        self.callback = callback
        
        self.queue = []

    def _decode_frame(self, frame: int):
        # PIO reads 2 pins × 11 times = 22 bits total
        # With SHIFT_RIGHT, bits shift right into ISR.
        # The first bit read (Start) is shifted to the right-most position (LSB)
        # of the valid data.
        # 22 bits valid. They are at bits 31:10 of the 32-bit word.
        # Bit 10 is the first bit read (Start).
        # Bit 31 is the last bit read (Stop).
        
        bits = []
        for i in range(11):
            # Extract from LSB (Start) to MSB (Stop)
            # Start is at bit 10. Next is 12, etc.
            shift = 10 + (i * 2)
            pair = (frame >> shift) & 0b11
            
            # Pin 0 is CLK, Pin 1 is DATA. We want DATA (bit 1 of pair).
            data_bit = (pair >> 1) & 1
            bits.append(data_bit)
            
        # Now bits[0] is Start, bits[1..8] is Data, bits[9] is Parity, bits[10] is Stop
        start = bits[0]
        stop = bits[10]
        
        if start != 0 or stop != 1:
            # print(f"Frame error: start={start}, stop={stop}")
            return None
            
        data_byte = 0
        for i in range(8):
            data_byte |= (bits[i+1] << i)
            
        parity = bits[9]
        
        # Odd parity check
        ones = bin(data_byte).count('1')
        if (ones + parity) % 2 != 1:
            # print(f"Parity error")
            return None
            
        return data_byte

    def _process_scancode(self, sc):
        """
        Handle PS/2 make/break and extended sequences.
        Calls user callback when a full event is decoded.
        """
        # Handle Pause/Break (E1 sequence)
        # Sequence: E1 14 77 E1 F0 14 F0 77
        if sc == 0xE1:
            self.pause_state = 1
            return
            
        if self.pause_state > 0:
            # Processing E1 sequence
            if self.pause_state == 1:
                if sc == 0x14: self.pause_state = 2
                elif sc == 0xF0: self.pause_state = 3
                else: self.pause_state = 0
            elif self.pause_state == 2:
                if sc == 0x77:
                    # First 77 -> Trigger Press
                    if self.callback: self.callback(0x77, True, True)
                    self.pause_state = 0
                else: self.pause_state = 0
            elif self.pause_state == 3:
                if sc == 0x14: self.pause_state = 4
                else: self.pause_state = 0
            elif self.pause_state == 4:
                if sc == 0xF0: self.pause_state = 5
                else: self.pause_state = 0
            elif self.pause_state == 5:
                if sc == 0x77:
                    # Second 77 -> Trigger Release
                    if self.callback: self.callback(0x77, False, True)
                self.pause_state = 0
            return

        if sc == 0xE0:
            self.extended = True
            return
        
        if sc == 0xF0:
            self.break_code = True
            return
        
        # We have a complete scancode
        pressed = not self.break_code
        extended = self.extended
        
        # Special handling for Print Screen
        # Make: E0 12 E0 7C
        # Break: E0 F0 7C E0 F0 12
        # We can just treat E0 12 as a fake shift (ignored) and E0 7C as the actual key
        if extended and sc == 0x12:
            # This is part of PrintScreen make/break, ignore it
            self.extended = False
            self.break_code = False
            return
            
        if extended and sc == 0x7C:
            # This is the actual PrintScreen code
            pass

        # Reset state for next scancode
        self.break_code = False
        self.extended = False
        
        # Call the user's callback
        if self.callback:
            self.callback(sc, pressed, extended)
        
        # Also queue it for polling
        self.queue.append((sc, pressed, extended))

    async def read_loop(self):
        """Async loop that reads from PIO FIFO and processes scancodes"""
        print("PS/2 read_loop started")
        while True:
            if self.sm.rx_fifo():
                raw = self.sm.get()
                sc = self._decode_frame(raw)
                if sc is not None:
                    self._process_scancode(sc)
            await asyncio.sleep_ms(1)
    
    def get_event(self):
        """Poll for events (alternative to callback)"""
        return self.queue.pop(0) if self.queue else None
