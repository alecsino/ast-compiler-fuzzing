import enum
import string

CHARACTERS  = string.ascii_letters + string.digits + string.punctuation
INT_MIN = -2147483648
INT_MAX = 2147483647
FLOAT_MIN = -1.17549e-038
FLOAT_MAX = 3.40282e+038
DOUBLE_MIN = 2.22507e-308
DOUBLE_MAX = 1.79769e+308
SHORT_MIN = -32768
SHORT_MAX = 32767
LONG_MIN = -9223372036854775808
LONG_MAX = 9223372036854775807


class Type(str, enum.Enum):
    """Class for types constants in C."""
    
    INT = 'int'
    FLOAT = 'float'
    DOUBLE = 'double'
    SHORT = 'short'
    LONG = 'long'
    CHAR = 'char'
    