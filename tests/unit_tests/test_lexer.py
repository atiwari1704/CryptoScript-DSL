import pytest
from cryptoscript.tokens import Token, TokenType
from cryptoscript.lexer import Lexer, LexerError

def lex(input: str) :
    lexer = Lexer(input)
    return lexer.tokenize()

def types(tokens: list[Token]) :
    return [t.type for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)] #For easier testing

def values(tokens: list[Token]) :
    return [t.value for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)] #For easier testing

# ------------------------------------------------------------------
#  IDENTIFIERS AND KEYWORDS
# ------------------------------------------------------------------

def test_identifier_1():
    assert types(lex("my_var")) == [TokenType.IDENT]
    assert values(lex("my_var")) == ["my_var"]

def test_identifier_2():
    assert types(lex("var1")) == [TokenType.IDENT]
    assert values(lex("var1")) == ["var1"]

def test_identifier_2():
    assert types(lex("_private")) == [TokenType.IDENT]
    assert values(lex("_private")) == ["_private"]

def test_keyword_1():
    assert types(lex("cipher")) == [TokenType.CIPHER]

def test_keyword_2():
    assert types(lex("encrypt")) == [TokenType.ENCRYPT]

def test_keyword_3():
    assert types(lex("sbox")) == [TokenType.SBOX]

def test_keyword_4():
    assert types(lex("pbox")) == [TokenType.PBOX]

def test_keyword_5():
    assert types(lex("repeat")) == [TokenType.REPEAT]

def test_keyword_6():
    assert types(lex("if")) == [TokenType.IF]

def test_keyword_7():
    assert types(lex("for")) == [TokenType.FOR]

def test_keyword_8():
    assert types(lex("def")) == [TokenType.DEF]

def test_keyword_9():
    assert types(lex("return")) == [TokenType.RETURN]

def test_type_1():
    assert types(lex("Int")) == [TokenType.INT]

def test_type_2():
    assert types(lex("ModInt")) == [TokenType.MODINT]

def test_type_3():
    assert types(lex("Matrix")) == [TokenType.MATRIX]

def test_type_4():
    assert types(lex("Hex")) == [TokenType.HEX]

def test_transform_1():
    assert types(lex("substitute")) == [TokenType.SUBSTITUTE]

def test_transform_2():
    assert types(lex("xor")) == [TokenType.XOR]

def test_conversion_1():
    assert types(lex("to_hex")) == [TokenType.TO_HEX]

def test_conversion_2():
    assert types(lex("to_le_bytes")) == [TokenType.TO_LE_BYTES]

def test_padding_1():
    assert types(lex("PKCS7")) == [TokenType.PKCS7]

def test_padding_2():
    assert types(lex("ZERO")) == [TokenType.ZERO]

def test_edgecase_1():
    assert types(lex("int")) == [TokenType.IDENT]

def test_multiple_identifiers():
    assert types(lex("x y z")) == [TokenType.IDENT, TokenType.IDENT, TokenType.IDENT]

def test_keyword_identifier():
    assert types(lex("if x")) == [TokenType.IF, TokenType.IDENT]

# ------------------------------------------------------------------
#  INTEGER AND HEX
# ------------------------------------------------------------------

def test_integer_1():
    assert types(lex("0")) == [TokenType.INT_LIT]
    assert values(lex("0")) == ["0"]

def test_integer_2():
    assert types(lex("42")) == [TokenType.INT_LIT]
    assert values(lex("42")) == ["42"]

def test_integer_3():
    assert types(lex("123456789")) == [TokenType.INT_LIT]
    assert values(lex("123456789")) == ["123456789"]

def test_integer_7() :
    with pytest.raises(LexerError):
        lex("248ab")

def test_hex_1():
    assert types(lex("0x1f")) == [TokenType.HEX_LIT]
    assert values(lex("0x1f")) == ["0x1f"]

def test_hex_2():
    assert types(lex("0X1F")) == [TokenType.HEX_LIT]
    assert values(lex("0X1F")) == ["0X1F"]

def test_hex_3():
    assert types(lex("0x1FF3A")) == [TokenType.HEX_LIT]
    assert values(lex("0xFF3A")) == ["0xFF3A"]

def test_hex_4():
    assert types(lex("0xaBcDeF")) == [TokenType.HEX_LIT]
    assert values(lex("0xaBcDeF")) == ["0xaBcDeF"]

def test_hex_5():
    assert types(lex("0x0")) == [TokenType.HEX_LIT]
    assert values(lex("0x0")) == ["0x0"]

def test_hex_6():
    with pytest.raises(LexerError):
        lex("0x")

def test_hex_7() :
    with pytest.raises(LexerError):
        lex("0x1G")

def test_integer_hex():
    assert types(lex("10 0xFF")) == [TokenType.INT_LIT, TokenType.HEX_LIT]


# ------------------------------------------------------------------
#  STRING
# ------------------------------------------------------------------

def test_string_1():
    assert types(lex('"hello"')) == [TokenType.STRING_LIT]
    assert values(lex('"hello"')) == ["hello"]

def test_string_2():
    assert types(lex("'world'")) == [TokenType.STRING_LIT]
    assert values(lex("'world'")) == ["world"]

def test_string_3():
    assert types(lex('""')) == [TokenType.STRING_LIT]
    assert values(lex('""')) == [""]

def test_string_4():
    assert types(lex('"hello world"')) == [TokenType.STRING_LIT]
    assert values(lex('"hello world"')) == ["hello world"]

def test_string_5():
    assert types(lex(r'"hello\nworld"')) == [TokenType.STRING_LIT]
    assert values(lex(r'"hello\nworld"')) == ["hello\nworld"]

def test_string_6():
    assert types(lex(r'"hello\tworld"')) == [TokenType.STRING_LIT]
    assert values(lex(r'"hello\tworld"')) == ["hello\tworld"]

def test_string_7():
    assert types(lex(r'"\\"')) == [TokenType.STRING_LIT]
    assert values(lex(r'"\\"')) == ["\\"]

def test_string_8():
    assert types(lex(r'"\"hello\""')) == [TokenType.STRING_LIT]
    assert values(lex(r'"\"hello\""')) == ['"hello"']

def test_string_9():
    with pytest.raises(LexerError):
        lex('"hello')

def test_string_10():
    with pytest.raises(LexerError):
        lex(r'"\q"')


# ------------------------------------------------------------------
#  BYTESTRING
# ------------------------------------------------------------------

def test_bytestring_1():
    assert types(lex('b"hello"')) == [TokenType.BYTES_LIT]
    assert values(lex('b"hello"')) == ["hello"]

def test_bytestring_2():
    assert types(lex("b'hello'")) == [TokenType.BYTES_LIT]
    assert values(lex('b"hello"')) == ['hello']

def test_bytestring_3():
    assert types(lex('b""')) == [TokenType.BYTES_LIT]
    assert values(lex('b""')) == [""]

def test_bytestring_4():
    assert types(lex(r'b"\x41"')) == [TokenType.BYTES_LIT]
    assert values(lex(r'b"\x41"')) == ["\\x41"]

def test_bytestring_5():
    assert types(lex(r'b"\xFF"')) == [TokenType.BYTES_LIT]
    assert values(lex(r'b"\xFF"')) == ["\\xFF"]

def test_bytestring_6():
    with pytest.raises(LexerError):
        lex(r'b"\xGG"')

def test_bytestring_7():
    with pytest.raises(LexerError):
        lex('b"hello')


# ------------------------------------------------------------------
#  OPERATORS AND DELIMITERS
# ------------------------------------------------------------------

def test_op_1():
    assert types(lex("+")) == [TokenType.PLUS]

def test_op_2():
    assert types(lex("-")) == [TokenType.MINUS]

def test_op_3():
    assert types(lex("*")) == [TokenType.STAR]

def test_op_4():
    assert types(lex("/")) == [TokenType.SLASH]

def test_op_5():
    assert types(lex("//")) == [TokenType.DOUBLESLASH]

def test_op_6():
    assert types(lex("%")) == [TokenType.PERCENT]

def test_op_7():
    assert types(lex("**")) == [TokenType.DOUBLESTAR]

def test_op_8():
    assert types(lex("=")) == [TokenType.EQUALS]

def test_op_9():
    assert types(lex("+=")) == [TokenType.PLUS_EQ]

def test_op_10():
    assert types(lex("-=")) == [TokenType.MINUS_EQ]

def test_op_11():
    assert types(lex("*=")) == [TokenType.STAR_EQ]

def test_op_12():
    assert types(lex("//=")) == [TokenType.DOUBLESLASH_EQ]

def test_op_13():
    assert types(lex("**=")) == [TokenType.DOUBLESTAR_EQ]

def test_op_14():
    assert types(lex(">>=")) == [TokenType.RSHIFT_EQ]

def test_op_15():
    assert types(lex("<<=")) == [TokenType.LSHIFT_EQ]

def test_op_16():
    assert types(lex("==")) == [TokenType.EQEQ]

def test_op_17():
    assert types(lex("!=")) == [TokenType.NEQ]

def test_op_18():
    assert types(lex("<")) == [TokenType.LT]

def test_op_19():
    assert types(lex(">")) == [TokenType.GT]

def test_op_20():
    assert types(lex("<=")) == [TokenType.LTE]

def test_op_21():
    assert types(lex(">=")) == [TokenType.GTE]

def test_pipeline():
    assert types(lex("|>")) == [TokenType.PIPELINE]

# Delimiters
def test_delim_1():
    assert types(lex("->")) == [TokenType.ARROW]

def test_delim_2():
    assert types(lex("(")) == [TokenType.LPAREN]

def test_delim_3():
    assert types(lex(")")) == [TokenType.RPAREN]

def test_delim_4():
    assert types(lex("[")) == [TokenType.LBRACKET]

def test_delim_5():
    assert types(lex("]")) == [TokenType.RBRACKET]

def test_delim_6():
    assert types(lex(":")) == [TokenType.COLON]

def test_delim_7():
    assert types(lex(",")) == [TokenType.COMMA]

def test_delim_8():
    assert types(lex(".")) == [TokenType.DOT]

def test_ch():
    with pytest.raises(LexerError):
        lex("@")

# ------------------------------------------------------------------
#  INDENTATION
# ------------------------------------------------------------------

def test_indent_1() :
    assert types(lex("if x:\n    y = 1")) == [TokenType.IF, TokenType.IDENT, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT, TokenType.DEDENT]

def test_indent_2() :
    assert types(lex("if x:\n    y = 1\n        z = 0x21")) == [TokenType.IF, TokenType.IDENT, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.HEX_LIT, TokenType.DEDENT, TokenType.DEDENT]

def test_indent_3() :
    assert types(lex("if x:\n    y = 1\n        z = 0x21\na = \"hello\"")) == [TokenType.IF, TokenType.IDENT, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.HEX_LIT, TokenType.DEDENT, TokenType.DEDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.STRING_LIT]

def test_indent_4() :
    assert types(lex("if x:\n    y = 1\n        z = 0x21\n\n        a = \"hello\"")) == [TokenType.IF, TokenType.IDENT, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.HEX_LIT, TokenType.IDENT, TokenType.EQUALS, TokenType.STRING_LIT, TokenType.DEDENT, TokenType.DEDENT]

def test_indent_5() :
    with pytest.raises(LexerError) :
        lex("if x:\n        y = 1\n    z = 0x21")

# ------------------------------------------------------------------
#  MULTI-TOKEN EXPRESSIONS
# ------------------------------------------------------------------

def test_multi_1():
    assert types(lex("x = 42")) == [TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT]

def test_multi_2():
    assert types(lex("x: Int")) == [TokenType.IDENT, TokenType.COLON, TokenType.INT]

def test_multi_3():
    assert types(lex("data |> xor(key)")) == [TokenType.IDENT, TokenType.PIPELINE, TokenType.XOR, TokenType.LPAREN, TokenType.IDENT, TokenType.RPAREN]

def test_multi_4():
    assert types(lex("pad(PKCS7)")) == [TokenType.PAD, TokenType.LPAREN, TokenType.PKCS7, TokenType.RPAREN]

def test_multi_5():
    assert types(lex("key = 0xFF")) == [TokenType.IDENT, TokenType.EQUALS, TokenType.HEX_LIT]

def test_multi_6():
    assert types(lex("key = 0xFF\nif key >= 0xFF : \n   a = True\nelse : \n    a = False")) == [TokenType.IDENT, TokenType.EQUALS, TokenType.HEX_LIT, TokenType.IF, TokenType.IDENT, TokenType.GTE, TokenType.HEX_LIT, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.TRUE, TokenType.DEDENT, TokenType.ELSE, TokenType.COLON, TokenType.INDENT, TokenType.IDENT, TokenType.EQUALS, TokenType.FALSE, TokenType.DEDENT]

# ------------------------------------------------------------------
#  MISC
# ------------------------------------------------------------------

def test_windows_line_ending():
    assert types(lex("x = 1\r\ny = 2")) == [TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT, TokenType.IDENT, TokenType.EQUALS, TokenType.INT_LIT]

def test_unexpect_EOF():
    with pytest.raises(LexerError):
        lex('"hello\\')