# ps2_pio.py - PS/2 Keyboard decoder using PIO on Raspberry Pi Pico (MicroPython)

from machine import Pin
import rp2
import uasyncio as asyncio
import time

# PS/2 protocol basics:
# - Clock: device-driven, 10-16 kHz
# - Data valid on falling clock edges
# - Frame: 1 start bit (0), 8 data bits (LSB first), 1 parity bit (odd), 1 stop bit (1)

@rp2.asm_pio(
    in_shiftdir=rp2.PIO.SHIFT_LEFT,   # Shift in from right (LSB), shifts to left
    autopush=True,
    push_thresh=22,                   # Push after 22 bits
)
def ps2_reader():
    # PIO program to read PS/2 keyboard data
    wrap_target()
    
    # Wait for idle state (CLK=1)
    wait(1, pin, 0)
    
    # Wait for Start Bit (CLK falling)
    wait(0, pin, 0)
    in_(pins, 2) # Sample Start Bit
    
    # Read remaining 10 bits (8 Data + 1 Parity + 1 Stop)
    set(x, 9)
    label("bitloop")
    wait(1, pin, 0) # Wait for CLK High
    wait(0, pin, 0) # Wait for CLK Low
    in_(pins, 2)    # Sample
    jmp(x_dec, "bitloop")
    
    wrap()

class PS2Keyboard:
    def __init__(self, clk_pin: int, data_pin: int, callback=None):
        print(f"Initializing PS2 keyboard with CLK={clk_pin}, DATA={data_pin}")
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.data = Pin(data_pin, Pin.IN, Pin.PULL_UP)
        
        if data_pin != clk_pin + 1:
            raise ValueError("DATA pin must be CLK + 1")
        
        self._init_sm()
        
        self.extended = False
        self.break_code = False
        self.pause_state = 0
        self.callback = callback
        self.queue = []
        self.ack_event = asyncio.Event()

    def _init_sm(self):
        print("Initializing PIO StateMachine...")
        # Remove existing SM if any (not strictly necessary as we overwrite, but good for cleanup)
        if hasattr(self, 'sm'):
            self.sm.active(0)
            
        self.sm = rp2.StateMachine(
            0,
            ps2_reader,
            freq=2_000_000,
            in_base=self.clk,
        )
        self.sm.active(1)
        print("PIO StateMachine Active")

    def _decode_frame(self, frame: int):
        # SHIFT_LEFT: First bit in (Start) is at MSB of the 22-bit chunk.
        # Last bit in (Stop) is at LSB.
        # 22 bits are in bits 21:0 of the integer.
        
        # Bit 21:20 = Start Bit Sample (DATA, CLK)
        # Bit 19:18 = Data Bit 0
        # ...
        # Bit 1:0   = Stop Bit
        
        bits = []
        for i in range(11):
            # i=0 is Start (Top), i=10 is Stop (Bottom)
            shift = (10 - i) * 2
            pair = (frame >> shift) & 0b11
            # Bit 1 of pair is DATA (since in_base=CLK, pin 0=CLK, pin 1=DATA)
            data_bit = (pair >> 1) & 1
            bits.append(data_bit)
            
        start = bits[0]
        stop = bits[10]
        
        if start != 0 or stop != 1:
            print(f"Frame Error: Start={start} Stop={stop} Raw={hex(frame)}")
            return None
            
        data_byte = 0
        for i in range(8):
            data_byte |= (bits[i+1] << i)
            
        parity = bits[9]
        
        ones = bin(data_byte).count('1')
        if (ones + parity) % 2 != 1:
            print(f"Parity Error: Data={hex(data_byte)} P={parity}")
            return None
            
        return data_byte

    def _process_scancode(self, sc):
        """
        Handle PS/2 make/break and extended sequences.
        Calls user callback when a full event is decoded.
        """
        # Handle ACK (0xFA)
        if sc == 0xFA:
            self.ack_event.set()
            return

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
    
    def send(self, byte):
        """Send a byte to the PS/2 device (Host-to-Device communication). Returns True if physical ACK bit is 0."""
        # Disable PIO to take control of pins
        self.sm.active(0)
        
        # Helper functions for open-drain simulation
        def drive_low(pin):
            pin.init(Pin.OUT, value=0)
            
        def release(pin):
            pin.init(Pin.IN, Pin.PULL_UP)
            
        # Calculate odd parity
        parity = 1
        temp = byte
        while temp:
            parity ^= (temp & 1)
            temp >>= 1
            
        ack_received = False
        try:
            # 1. Request to Send
            drive_low(self.clk)
            time.sleep_us(120) # >100us
            drive_low(self.data)
            time.sleep_us(10)
            release(self.clk)
            
            # 2. Send Data (8 bits, LSB first)
            for i in range(8):
                # Wait for CLK Low (Device drives it)
                start = time.ticks_us()
                while self.clk.value() == 1:
                    if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK low")
                
                # Set Data
                bit = (byte >> i) & 1
                if bit: release(self.data)
                else: drive_low(self.data)
                
                # Wait for CLK High (Device samples)
                start = time.ticks_us()
                while self.clk.value() == 0:
                    if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK high")
                
            # 3. Parity Bit
            start = time.ticks_us()
            while self.clk.value() == 1:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK low (Parity)")
            
            if parity: release(self.data)
            else: drive_low(self.data)
            
            start = time.ticks_us()
            while self.clk.value() == 0:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK high (Parity)")
            
            # 4. Stop Bit (Always 1)
            start = time.ticks_us()
            while self.clk.value() == 1:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK low (Stop)")
            
            release(self.data)
            
            start = time.ticks_us()
            while self.clk.value() == 0:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK high (Stop)")
            
            # 5. Ack Bit (Device drives Data Low)
            start = time.ticks_us()
            while self.clk.value() == 1:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK low (Ack)")
            
            # Check ACK
            ack_received = (self.data.value() == 0)
            
            start = time.ticks_us()
            while self.clk.value() == 0:
                if time.ticks_diff(time.ticks_us(), start) > 10000: raise OSError("Timeout waiting for CLK high (Ack)")
                
            # Do NOT wait for data to be released here. 
            # The keyboard might immediately start sending the response (0xFA).
            # We need to switch to PIO mode ASAP.
                 
        except OSError as e:
            print(f"PS/2 Send Error: {e}")
            return False
        finally:
            # Ensure pins are back to input/pullup
            release(self.clk)
            release(self.data)
            
            # Small delay to let lines stabilize high
            time.sleep_us(50)
            
            # Re-enable PIO and restore pin mux
            self._init_sm()
            
        return ack_received

    async def send_cmd(self, cmd, arg=None):
        """Send a command and optionally an argument, waiting for ACK (0xFA) for each."""
        self.ack_event.clear()
        if not self.send(cmd):
            print(f"CMD {hex(cmd)} Physical NACK")
            return False
            
        try:
            await asyncio.wait_for(self.ack_event.wait(), 0.2)
        except asyncio.TimeoutError:
            print(f"CMD {hex(cmd)} Timeout waiting for ACK")
            return False
            
        if arg is not None:
            await asyncio.sleep_ms(5) # Small delay between bytes
            self.ack_event.clear()
            if not self.send(arg):
                print(f"ARG {hex(arg)} Physical NACK")
                return False
            try:
                await asyncio.wait_for(self.ack_event.wait(), 0.2)
            except asyncio.TimeoutError:
                print(f"ARG {hex(arg)} Timeout waiting for ACK")
                return False
                
        return True

    # Convenience methods
    async def cmd_reset(self): return await self.send_cmd(0xFF)
    async def cmd_resend(self): return await self.send_cmd(0xFE) # Note: Resend usually doesn't get ACK? It gets the last byte.
    async def cmd_set_defaults(self): return await self.send_cmd(0xF6)
    async def cmd_disable(self): return await self.send_cmd(0xF5)
    async def cmd_enable(self): return await self.send_cmd(0xF4)
    async def cmd_set_typematic(self, rate): return await self.send_cmd(0xF3, rate)
    async def cmd_set_leds(self, leds): return await self.send_cmd(0xED, leds)
    async def cmd_echo(self): 
        # Echo expects 0xEE response, not 0xFA. Special case.
        # For now, just send and let main loop handle 0xEE if needed.
        return self.send(0xEE)
