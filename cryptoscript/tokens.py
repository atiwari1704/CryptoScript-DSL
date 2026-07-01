from enum import Enum, auto


class TokenType(Enum):

    # ------------------------------------------------------------------
    #  LITERALS
    # ------------------------------------------------------------------
    INT_LIT = auto()
    HEX_LIT = auto()
    BYTES_LIT = auto()
    STRING_LIT = auto()
    BOOL_LIT = auto()

    # ------------------------------------------------------------------
    #  IDENTIFIER
    # ------------------------------------------------------------------
    IDENT = auto()

    # ------------------------------------------------------------------
    #  KEYWORDS FROM PYTHON
    # ------------------------------------------------------------------

    # Logic / Boolean
    FALSE = auto()
    TRUE = auto()
    NONE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Control flow
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()

    # Structure
    DEF = auto()
    IMPORT = auto()
    FROM = auto()
    AS = auto()
    WITH = auto()
    PASS = auto()

    # Pattern matching
    MATCH = auto()
    CASE = auto()
    IN = auto()
    IS = auto()

    # ------------------------------------------------------------------
    #  CUSTOM KEYWORDS
    # ------------------------------------------------------------------
    CIPHER = auto()
    ENCRYPT = auto()
    SBOX = auto()
    PBOX = auto()
    REPEAT = auto()

    # ------------------------------------------------------------------
    #  OPERATORS
    # ------------------------------------------------------------------

    # Arithmetic
    PLUS = auto()   # +
    MINUS = auto()   # -
    STAR = auto()   # *
    SLASH = auto()   # /
    DOUBLESLASH = auto()   # //
    PERCENT = auto()   # %
    DOUBLESTAR = auto()   # **

    # Assignment
    EQUALS = auto()   # =
    PLUS_EQ = auto()   # +=
    MINUS_EQ = auto()   # -=
    STAR_EQ = auto()   # *=
    SLASH_EQ = auto()   # /=
    DOUBLESLASH_EQ = auto()   # //=
    PERCENT_EQ = auto()   # %=
    DOUBLESTAR_EQ = auto()   # **=
    AMP_EQ = auto()   # &=
    PIPE_EQ = auto()   # |=
    CARET_EQ = auto()   # ^=
    RSHIFT_EQ = auto()   # >>=
    LSHIFT_EQ = auto()   # <<=

    # Comparison
    EQEQ = auto()   # ==
    NEQ = auto()   # !=
    LT = auto()   # <
    GT = auto()   # >
    LTE = auto()   # <=
    GTE = auto()   # >=

    # Bitwise
    AMP = auto()   # &
    PIPE = auto()   # |
    CARET = auto()   # ^
    TILDE = auto()   # ~
    LSHIFT = auto()   # <<
    RSHIFT = auto()   # >>

    # Delimiters
    LPAREN = auto()   # (
    RPAREN = auto()   # )
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    LBRACE = auto()   # {
    RBRACE = auto()   # }
    COMMA = auto()   # ,
    COLON = auto()   # :
    DOT = auto()   # .
    SEMICOLON = auto()   # ;
    ARROW = auto()   # ->

    # ------------------------------------------------------------------
    #  CUSTOM OPERATOR
    # ------------------------------------------------------------------
    PIPELINE = auto()   # |>

    # ------------------------------------------------------------------
    #  DATA TYPES
    # ------------------------------------------------------------------
    INT = auto()
    BOOL = auto()
    STRING = auto()
    BYTES = auto()
    HEX = auto()
    MODINT = auto()
    MATRIX = auto()

    # ------------------------------------------------------------------
    #  CORE TRANSFORM PRIMITIVES
    # ------------------------------------------------------------------
    SUBSTITUTE = auto()
    PERMUTE = auto()
    XOR = auto()
    ROTL = auto()
    ROTR = auto()
    PAD = auto()
    UNPAD = auto()

    # ------------------------------------------------------------------
    #  SAFE TYPE CONVERSIONS
    # ------------------------------------------------------------------
    TO_BYTES = auto()
    TO_LE_BYTES = auto()
    TO_BE_BYTES = auto()
    TO_HEX = auto()
    TO_STRING = auto()
    TO_INT = auto()

    # ------------------------------------------------------------------
    #  PADDING SCHEMES
    # ------------------------------------------------------------------
    PKCS7 = auto()
    ZERO = auto()

    # ------------------------------------------------------------------
    #  OTHERS
    # ------------------------------------------------------------------
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()


# ------------------------------------------------------------------
#  KEYWORD LOOKUP TABLE
# ------------------------------------------------------------------
KEYWORDS: dict[str, TokenType] = {
    # ------------------------------------------------------------------
    #  KEYWORDS FROM PYTHON
    # ------------------------------------------------------------------

    # Logic / Boolean
    "False":    TokenType.FALSE,
    "True":     TokenType.TRUE,
    "None":     TokenType.NONE,
    "and":      TokenType.AND,
    "or":       TokenType.OR,
    "not":      TokenType.NOT,

    # Control flow
    "if":       TokenType.IF,
    "elif":     TokenType.ELIF,
    "else":     TokenType.ELSE,
    "for":      TokenType.FOR,
    "while":    TokenType.WHILE,
    "break":    TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "return":   TokenType.RETURN,

    # Structure
    "def":      TokenType.DEF,
    "import":   TokenType.IMPORT,
    "from":     TokenType.FROM,
    "as":       TokenType.AS,
    "with":     TokenType.WITH,
    "pass":     TokenType.PASS,

    # Pattern matching
    "match":    TokenType.MATCH,
    "case":     TokenType.CASE,
    "in":       TokenType.IN,
    "is":       TokenType.IS,

    # ------------------------------------------------------------------
    #  CUSTOM KEYWORDS
    # ------------------------------------------------------------------
    "cipher":   TokenType.CIPHER,
    "encrypt":  TokenType.ENCRYPT,
    "sbox":     TokenType.SBOX,
    "pbox":     TokenType.PBOX,
    "repeat":   TokenType.REPEAT,

    # ------------------------------------------------------------------
    #  DATA TYPES
    # ------------------------------------------------------------------
    "Int":      TokenType.INT,
    "Bool":     TokenType.BOOL,
    "String":   TokenType.STRING,
    "Bytes":    TokenType.BYTES,
    "Hex":      TokenType.HEX,
    "ModInt":   TokenType.MODINT,
    "Matrix":   TokenType.MATRIX,

    # ------------------------------------------------------------------
    #  CORE TRANSFORM PRIMITIVES
    # ------------------------------------------------------------------
    "substitute":  TokenType.SUBSTITUTE,
    "permute":     TokenType.PERMUTE,
    "xor":         TokenType.XOR,
    "rotl":        TokenType.ROTL,
    "rotr":        TokenType.ROTR,
    "pad":         TokenType.PAD,
    "unpad":       TokenType.UNPAD,

    # ------------------------------------------------------------------
    #  SAFE TYPE CONVERSIONS
    # ------------------------------------------------------------------
    "to_bytes":    TokenType.TO_BYTES,
    "to_le_bytes": TokenType.TO_LE_BYTES,
    "to_be_bytes": TokenType.TO_BE_BYTES,
    "to_hex":      TokenType.TO_HEX,
    "to_string":   TokenType.TO_STRING,
    "to_int":      TokenType.TO_INT,

    # ------------------------------------------------------------------
    #  PADDING SCHEMES
    # ------------------------------------------------------------------
    "PKCS7":    TokenType.PKCS7,
    "ZERO":     TokenType.ZERO,

}


# ------------------------------------------------------------------
#  TOKEN CLASS
# ------------------------------------------------------------------
class Token:
    def __init__(self, type: TokenType, value: str, line: int):
        self.type = type
        self.value = value
        self.line = line

    def __str__(self):
        return f"Token({self.type.name}, \"{self.value}\", line={self.line})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value
