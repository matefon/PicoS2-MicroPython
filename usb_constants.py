from usb.device.keyboard import KeyCode

class USB:
    """USB HID Usage IDs (Page 0x07)"""
    # Letters
    A = KeyCode.A; B = KeyCode.B; C = KeyCode.C; D = KeyCode.D; E = KeyCode.E
    F = KeyCode.F; G = KeyCode.G; H = KeyCode.H; I = KeyCode.I; J = KeyCode.J
    K = KeyCode.K; L = KeyCode.L; M = KeyCode.M; N = KeyCode.N; O = KeyCode.O
    P = KeyCode.P; Q = KeyCode.Q; R = KeyCode.R; S = KeyCode.S; T = KeyCode.T
    U = KeyCode.U; V = KeyCode.V; W = KeyCode.W; X = KeyCode.X; Y = KeyCode.Y
    Z = KeyCode.Z

    # Numbers
    N1 = KeyCode.N1; N2 = KeyCode.N2; N3 = KeyCode.N3; N4 = KeyCode.N4; N5 = KeyCode.N5
    N6 = KeyCode.N6; N7 = KeyCode.N7; N8 = KeyCode.N8; N9 = KeyCode.N9; N0 = KeyCode.N0

    # Function Keys
    F1 = KeyCode.F1; F2 = KeyCode.F2; F3 = KeyCode.F3; F4 = KeyCode.F4; F5 = KeyCode.F5
    F6 = KeyCode.F6; F7 = KeyCode.F7; F8 = KeyCode.F8; F9 = KeyCode.F9; F10 = KeyCode.F10
    F11 = KeyCode.F11; F12 = KeyCode.F12

    # Modifiers
    L_CTRL   = KeyCode.LEFT_CTRL
    L_SHIFT  = KeyCode.LEFT_SHIFT
    L_ALT    = KeyCode.LEFT_ALT
    L_GUI    = getattr(KeyCode, 'LEFT_GUI', getattr(KeyCode, 'GUI', getattr(KeyCode, 'LEFT_META', 0xE3)))
    R_CTRL   = KeyCode.RIGHT_CTRL
    R_SHIFT  = KeyCode.RIGHT_SHIFT
    R_ALT    = KeyCode.RIGHT_ALT
    R_GUI    = getattr(KeyCode, 'RIGHT_GUI', getattr(KeyCode, 'RIGHT_META', 0xE7))

    # Common Keys
    ENTER    = KeyCode.ENTER
    ESC      = KeyCode.ESCAPE
    BACKSPACE= KeyCode.BACKSPACE
    TAB      = KeyCode.TAB
    SPACE    = KeyCode.SPACE
    MINUS    = KeyCode.MINUS
    EQUAL    = KeyCode.EQUAL
    L_BRACKET= KeyCode.OPEN_BRACKET
    R_BRACKET= KeyCode.CLOSE_BRACKET
    BACKSLASH= KeyCode.BACKSLASH
    SEMICOLON= KeyCode.SEMICOLON
    QUOTE    = KeyCode.QUOTE
    GRAVE    = KeyCode.GRAVE
    COMMA    = KeyCode.COMMA
    DOT      = KeyCode.DOT
    SLASH    = KeyCode.SLASH
    CAPS_LOCK= KeyCode.CAPS_LOCK

    # Navigation
    PRINTSCR = getattr(KeyCode, 'PRINT_SCREEN', 0x46)
    SCROLL_LOCK= getattr(KeyCode, 'SCROLL_LOCK', 0x47)
    PAUSE    = getattr(KeyCode, 'PAUSE', 0x48)
    INSERT   = getattr(KeyCode, 'INSERT', 0x49)
    HOME     = getattr(KeyCode, 'HOME', 0x4A)
    PGUP     = getattr(KeyCode, 'PAGE_UP', 0x4B)
    DELETE   = getattr(KeyCode, 'DELETE', 0x4C)
    END      = getattr(KeyCode, 'END', 0x4D)
    PGDN     = getattr(KeyCode, 'PAGE_DOWN', 0x4E)
    RIGHT    = getattr(KeyCode, 'RIGHT', 0x4F)
    LEFT     = getattr(KeyCode, 'LEFT', 0x50)
    DOWN     = getattr(KeyCode, 'DOWN', 0x51)
    UP       = getattr(KeyCode, 'UP', 0x52)

    # Numpad
    NUM_LOCK = getattr(KeyCode, 'NUM_LOCK', 0x53)
    KP_SLASH = getattr(KeyCode, 'KP_DIVIDE', 0x54)
    KP_STAR  = getattr(KeyCode, 'KP_MULTIPLY', 0x55)
    KP_MINUS = getattr(KeyCode, 'KP_MINUS', 0x56)
    KP_PLUS  = getattr(KeyCode, 'KP_PLUS', 0x57)
    KP_ENTER = getattr(KeyCode, 'KP_ENTER', 0x58)
    KP_1     = getattr(KeyCode, 'KP_1', 0x59)
    KP_2     = getattr(KeyCode, 'KP_2', 0x5A)
    KP_3     = getattr(KeyCode, 'KP_3', 0x5B)
    KP_4     = getattr(KeyCode, 'KP_4', 0x5C)
    KP_5     = getattr(KeyCode, 'KP_5', 0x5D)
    KP_6     = getattr(KeyCode, 'KP_6', 0x5E)
    KP_7     = getattr(KeyCode, 'KP_7', 0x5F)
    KP_8     = getattr(KeyCode, 'KP_8', 0x60)
    KP_9     = getattr(KeyCode, 'KP_9', 0x61)
    KP_0     = getattr(KeyCode, 'KP_0', 0x62)
    KP_DOT   = getattr(KeyCode, 'KP_PERIOD', 0x63)

    # Misc
    APP      = getattr(KeyCode, 'APPLICATION', 0x65)
    ISO_SLASH= 0x64