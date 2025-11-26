from ps2_constants import PS2
from usb_constants import USB

# --- KEY ACTION DEFINITION ---
class KeyAction:
    def __init__(self, codes, toggle=False):
        self.codes = codes if isinstance(codes, list) else [codes]
        self.toggle = toggle

# Use K for normal key, T for toggle key, M for multi-key (macro)
def K(code): return KeyAction(code, toggle=False)
def T(code): return KeyAction(code, toggle=True)
def M(*codes): return KeyAction(list(codes), toggle=False)

# Example for macro (A -> CTRL+ALT+T (open terminal)):
#   PS2.T: M(USB.L_CTRL, USB.L_ALT, USB.T)
#
# To use USB F13-F24 see README.

KEY_MAP = {
    # Letters
    PS2.A: K(USB.A),
    PS2.B: K(USB.B),
    PS2.C: K(USB.C),
    PS2.D: K(USB.D),
    PS2.E: K(USB.E),
    PS2.F: K(USB.F),
    PS2.G: K(USB.G),
    PS2.H: K(USB.H),
    PS2.I: K(USB.I),
    PS2.J: K(USB.J),
    PS2.K: K(USB.K),
    PS2.L: K(USB.L),
    PS2.M: K(USB.M),
    PS2.N: K(USB.N),
    PS2.O: K(USB.O),
    PS2.P: K(USB.P),
    PS2.Q: K(USB.Q),
    PS2.R: K(USB.R),
    PS2.S: K(USB.S),
    PS2.T: K(USB.T),
    PS2.U: K(USB.U),
    PS2.V: K(USB.V),
    PS2.W: K(USB.W),
    PS2.X: K(USB.X),
    PS2.Y: K(USB.Y),
    PS2.Z: K(USB.Z),

    # Numbers
    PS2.N1: K(USB.N1),
    PS2.N2: K(USB.N2),
    PS2.N3: K(USB.N3),
    PS2.N4: K(USB.N4),
    PS2.N5: K(USB.N5),
    PS2.N6: K(USB.N6),
    PS2.N7: K(USB.N7),
    PS2.N8: K(USB.N8),
    PS2.N9: K(USB.N9),
    PS2.N0: K(USB.N0),

    # F-Keys
    PS2.F1: K(USB.F1),
    PS2.F2: K(USB.F2),
    PS2.F3: K(USB.F3),
    PS2.F4: K(USB.F4),
    PS2.F5: K(USB.F5),
    PS2.F6: K(USB.F6),
    PS2.F7: K(USB.F7),
    PS2.F8: K(USB.F8),
    PS2.F9: K(USB.F9),
    PS2.F10: K(USB.F10),
    PS2.F11: K(USB.F11),
    PS2.F12: K(USB.F12),

    # Modifiers
    PS2.L_SHIFT: K(USB.L_SHIFT),
    PS2.R_SHIFT: K(USB.R_SHIFT),
    PS2.L_CTRL: K(USB.L_CTRL),
    PS2.R_CTRL: K(USB.R_CTRL),
    PS2.L_ALT: K(USB.L_ALT),
    PS2.R_ALT: K(USB.R_ALT),
    PS2.L_GUI: K(USB.L_GUI),
    PS2.R_GUI: K(USB.R_GUI),
    #(0x1F, False): K(USB.L_GUI), # Fallback L_GUI
    #(0x27, False): K(USB.R_GUI), # Fallback R_GUI
    PS2.APP: K(USB.APP),

    # Common
    PS2.ENTER: K(USB.ENTER),
    PS2.ESC: K(USB.ESC),
    PS2.BACKSPACE: K(USB.BACKSPACE),
    PS2.TAB: K(USB.TAB),
    PS2.SPACE: K(USB.SPACE),
    PS2.MINUS: K(USB.MINUS),
    PS2.EQUAL: K(USB.EQUAL),
    PS2.L_BRACKET: K(USB.L_BRACKET),
    PS2.R_BRACKET: K(USB.R_BRACKET),
    PS2.BACKSLASH: K(USB.BACKSLASH),
    PS2.SEMICOLON: K(USB.SEMICOLON),
    PS2.QUOTE: K(USB.QUOTE),
    PS2.GRAVE: K(USB.GRAVE),
    PS2.COMMA: K(USB.COMMA),
    PS2.DOT: K(USB.DOT),
    PS2.SLASH: K(USB.SLASH),
    
    # Locks
    PS2.CAPS_LOCK: K(USB.CAPS_LOCK),
    PS2.NUM_LOCK: K(USB.NUM_LOCK),
    PS2.SCROLL_LOCK: K(USB.SCROLL_LOCK),

    # Navigation
    PS2.INSERT: K(USB.INSERT),
    PS2.DELETE: K(USB.DELETE),
    PS2.HOME: K(USB.HOME),
    PS2.END: K(USB.END),
    PS2.PGUP: K(USB.PGUP),
    PS2.PGDN: K(USB.PGDN),
    PS2.UP: K(USB.UP),
    PS2.DOWN: K(USB.DOWN),
    PS2.LEFT: K(USB.LEFT),
    PS2.RIGHT: K(USB.RIGHT),
    PS2.PRINTSCR: K(USB.PRINTSCR),
    PS2.PAUSE: K(USB.PAUSE),

    # Numpad
    PS2.KP_0: K(USB.KP_0),
    PS2.KP_1: K(USB.KP_1),
    PS2.KP_2: K(USB.KP_2),
    PS2.KP_3: K(USB.KP_3),
    PS2.KP_4: K(USB.KP_4),
    PS2.KP_5: K(USB.KP_5),
    PS2.KP_6: K(USB.KP_6),
    PS2.KP_7: K(USB.KP_7),
    PS2.KP_8: K(USB.KP_8),
    PS2.KP_9: K(USB.KP_9),
    PS2.KP_DOT: K(USB.KP_DOT),
    PS2.KP_PLUS: K(USB.KP_PLUS),
    PS2.KP_MINUS: K(USB.KP_MINUS),
    PS2.KP_STAR: K(USB.KP_STAR),
    PS2.KP_SLASH: K(USB.KP_SLASH),
    PS2.KP_ENTER: K(USB.KP_ENTER),

    # ISO
    PS2.ISO_SLASH: K(USB.ISO_SLASH),
}
