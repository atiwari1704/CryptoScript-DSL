from cryptoscript.tokens import Token, TokenType, KEYWORDS

# ------------------------------------------------------------------
#  Tests for Lookup Table
# ------------------------------------------------------------------

def test_not_empty():
    assert len(KEYWORDS) > 0

def test_token_types():
    for key, val in KEYWORDS.items():
        assert isinstance(val, TokenType), \
            f"KEYWORDS['{key}'] is not a TokenType"

def test_no_duplicate_keys():
    assert len(KEYWORDS) == len(set(KEYWORDS.keys()))

#Python Keywords
def test_python_boolean_logic_keywords():
    assert KEYWORDS["True"]  == TokenType.TRUE
    assert KEYWORDS["False"] == TokenType.FALSE
    assert KEYWORDS["None"]  == TokenType.NONE
    assert KEYWORDS["and"] == TokenType.AND
    assert KEYWORDS["or"]  == TokenType.OR
    assert KEYWORDS["not"] == TokenType.NOT

def test_python_control_flow_keywords():
    assert KEYWORDS["if"]       == TokenType.IF
    assert KEYWORDS["elif"]     == TokenType.ELIF
    assert KEYWORDS["else"]     == TokenType.ELSE
    assert KEYWORDS["for"]      == TokenType.FOR
    assert KEYWORDS["while"]    == TokenType.WHILE
    assert KEYWORDS["break"]    == TokenType.BREAK
    assert KEYWORDS["continue"] == TokenType.CONTINUE
    assert KEYWORDS["return"]   == TokenType.RETURN

def test_python_structure_keywords():
    assert KEYWORDS["def"]    == TokenType.DEF
    assert KEYWORDS["import"] == TokenType.IMPORT
    assert KEYWORDS["from"]   == TokenType.FROM
    assert KEYWORDS["as"]     == TokenType.AS
    assert KEYWORDS["with"]   == TokenType.WITH
    assert KEYWORDS["pass"]   == TokenType.PASS

def test_python_pattern_matching_keywords():
    assert KEYWORDS["match"] == TokenType.MATCH
    assert KEYWORDS["case"]  == TokenType.CASE
    assert KEYWORDS["in"]    == TokenType.IN
    assert KEYWORDS["is"]    == TokenType.IS

#Custom Keywords
def test_cryptoscript_custom_keywords():
    assert KEYWORDS["cipher"]  == TokenType.CIPHER
    assert KEYWORDS["encrypt"] == TokenType.ENCRYPT
    assert KEYWORDS["sbox"]    == TokenType.SBOX
    assert KEYWORDS["pbox"]    == TokenType.PBOX
    assert KEYWORDS["repeat"]  == TokenType.REPEAT

#Data Types
def test_data_type():
    assert KEYWORDS["Int"]    == TokenType.INT
    assert KEYWORDS["Bool"]   == TokenType.BOOL
    assert KEYWORDS["String"] == TokenType.STRING
    assert KEYWORDS["Bytes"]  == TokenType.BYTES
    assert KEYWORDS["Hex"]    == TokenType.HEX
    assert KEYWORDS["ModInt"] == TokenType.MODINT
    assert KEYWORDS["Matrix"] == TokenType.MATRIX

#Transform Primitives
def test_transform_primitives():
    assert KEYWORDS["substitute"]  == TokenType.SUBSTITUTE
    assert KEYWORDS["permute"]     == TokenType.PERMUTE
    assert KEYWORDS["xor"]         == TokenType.XOR
    assert KEYWORDS["rotl"]        == TokenType.ROTL
    assert KEYWORDS["rotr"]        == TokenType.ROTR
    assert KEYWORDS["pad"]         == TokenType.PAD
    assert KEYWORDS["unpad"]       == TokenType.UNPAD

#Safe Type Conversions
def test_type_conversion():
    assert KEYWORDS["to_bytes"]    == TokenType.TO_BYTES
    assert KEYWORDS["to_le_bytes"] == TokenType.TO_LE_BYTES
    assert KEYWORDS["to_be_bytes"] == TokenType.TO_BE_BYTES
    assert KEYWORDS["to_hex"]      == TokenType.TO_HEX
    assert KEYWORDS["to_string"]   == TokenType.TO_STRING
    assert KEYWORDS["to_int"]      == TokenType.TO_INT

#Padding Schemes
def test_padding_schemes():
    assert KEYWORDS["PKCS7"] == TokenType.PKCS7
    assert KEYWORDS["ZERO"]  == TokenType.ZERO

def test_unknown_words():
    assert "abcde"     not in KEYWORDS
    assert "foobar"     not in KEYWORDS
    assert "cryptoscript" not in KEYWORDS


# ------------------------------------------------------------------
#  Tests for Token Class
# ------------------------------------------------------------------

def test_token_type():
    t = Token(TokenType.CIPHER, "cipher", 1)
    assert t.type == TokenType.CIPHER

def test_token_value():
    t = Token(TokenType.CIPHER, "cipher", 1)
    assert t.value == "cipher"

def test_token_line():
    t = Token(TokenType.CIPHER, "cipher", 5)
    assert t.line == 5

def test_token_str_1():
    t = Token(TokenType.CIPHER, "cipher", 1)
    assert str(t) == 'Token(CIPHER, "cipher", line=1)'

def test_token_str_2():
    t = Token(TokenType.INT_LIT, "42", 3)
    assert str(t) == 'Token(INT_LIT, "42", line=3)'

def test_token_str_3():
    t = Token(TokenType.HEX_LIT, "0x1F", 7)
    assert str(t) == 'Token(HEX_LIT, "0x1F", line=7)'

def test_token_equality_1():
    t1 = Token(TokenType.INT_LIT, "42", 1)
    t2 = Token(TokenType.INT_LIT, "42", 1)
    assert t1 == t2

def test_token_equality_2():
    t1 = Token(TokenType.INT_LIT, "42", 1)
    t2 = Token(TokenType.INT_LIT, "42", 99)
    assert t1 == t2

def test_token_inequality_1():
    t1 = Token(TokenType.INT_LIT,    "42", 1)
    t2 = Token(TokenType.STRING_LIT, "42", 1)
    assert t1 != t2

def test_token_inequality_2():
    t1 = Token(TokenType.INT_LIT, "42", 1)
    t2 = Token(TokenType.INT_LIT, "99", 1)
    assert t1 != t2

def test_token_pipeline():
    t = Token(TokenType.PIPELINE, "|>", 2)
    assert t.type  == TokenType.PIPELINE
    assert t.value == "|>"
    assert t.line  == 2

def test_token_eof():
    t = Token(TokenType.EOF, "", 10)
    assert t.type  == TokenType.EOF
    assert t.value == ""