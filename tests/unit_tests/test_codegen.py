import pytest

from cryptoscript.lexer import Lexer
from cryptoscript.parser import Parser
from cryptoscript.codegen import CodeGen, CodeGenError
from cryptoscript.type_checker import TypeChecker, TypeCheckError

#  Helper utilities

def compile_dsl(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens, source).parse()
    TypeChecker(source).check(ast)
    return CodeGen().generate(ast)


from typing import Optional
def run_dsl(source: str, extra_globals: Optional[dict] = None) -> dict:
    py_src = compile_dsl(source)
    ns: dict = {}
    if extra_globals:
        ns.update(extra_globals)
    exec(py_src, ns)
    return ns

#  Literals

def test_lit_1():
    ns = run_dsl("x: Int = 0\n")
    assert ns["x"] == 0

def test_lit_2():
    ns = run_dsl("x: Int = 42\n")
    assert ns["x"] == 42

def test_lit_3():
    ns = run_dsl("x: Int = 123456789\n")
    assert ns["x"] == 123456789

def test_lit_4():
    ns = run_dsl("x: Hex = 0xFF\n")
    assert ns["x"] == 0xFF
    assert isinstance(ns["x"], int)

def test_lit_5():
    ns = run_dsl("x: Hex = 0X1A2B\n")
    assert ns["x"] == 0x1A2B
    assert isinstance(ns["x"], int)

def test_lit_6():
    ns = run_dsl('x: String = "hello"\n')
    assert ns["x"] == "hello"

def test_lit_7():
    ns = run_dsl("x: Bool = True\n")
    assert ns["x"] is True

def test_lit_8():
    ns = run_dsl("x: Bool = False\n")
    assert ns["x"] is False

def test_lit_9():
    ns = run_dsl("x: Int = None\n")
    assert ns["x"] is None

def test_lit_10():
    ns = run_dsl('x: Bytes = b"abc"\n')
    assert ns["x"] == b"abc"

def test_lit_11():
    ns = run_dsl(r'x: Bytes = b"\x41\x42"' + "\n")
    assert ns["x"] == b"AB"

def test_lit_12():
    ns = run_dsl("x: Int = [1, 2, 3]\n")
    assert ns["x"] == [1, 2, 3]

def test_lit_13():
    ns = run_dsl("x: Int = []\n")
    assert ns["x"] == []

#  Variable Declaration

def test_var_1():
    ns = run_dsl("x: Int\n")
    assert ns["x"] == 0

def test_var_2():
    ns = run_dsl("x: Bool\n")
    assert ns["x"] is False

def test_var_3():
    ns = run_dsl("x: String\n")
    assert ns["x"] == ""

def test_var_4():
    ns = run_dsl("x: Bytes\n")
    assert ns["x"] == b""

def test_var_5():
    ns = run_dsl("x: Hex\n")
    assert ns["x"] == 0
    assert isinstance(ns["x"], int)

def test_var_6():
    ns = run_dsl("x: ModInt[7]\n")
    assert int(ns["x"]) == 0

def test_var_7():
    ns = run_dsl("x: ModInt[7] = 10\n")
    assert int(ns["x"]) == 3   # 10 % 7

def test_var_8():
    ns = run_dsl("m: Matrix[Int, 2, 3]\n")
    obj = ns["m"]
    assert obj.rows == 2 and obj.cols == 3

#  Expressions

def test_expr_1():
    assert run_dsl("x: Int = 3 + 4\n")["x"] == 7

def test_expr_2():
    assert run_dsl("x: Int = 10 - 3\n")["x"] == 7

def test_expr_3():
    assert run_dsl("x: Int = 6 * 7\n")["x"] == 42

def test_expr_4():
    assert run_dsl("x: Int = 7 // 2\n")["x"] == 3

def test_expr_5():
    assert run_dsl("x: Int = 10 % 3\n")["x"] == 1

def test_expr_6():
    assert run_dsl("x: Int = 2 ** 10\n")["x"] == 1024

def test_expr_7():
    assert run_dsl("x: Int = 0xFF & 0x0F\n")["x"] == 0x0F

def test_expr_8():
    assert run_dsl("x: Int = 0xF0 | 0x0F\n")["x"] == 0xFF

def test_expr_9():
    assert run_dsl("x: Int = 0xFF ^ 0x0F\n")["x"] == 0xF0

def test_expr_10():
    assert run_dsl("x: Int = 1 << 4\n")["x"] == 16

def test_expr_11():
    assert run_dsl("x: Int = 32 >> 2\n")["x"] == 8

def test_expr_12():
    assert run_dsl("x: Int = -5\n")["x"] == -5

def test_expr_13():
    assert run_dsl("x: Int = ~0\n")["x"] == -1

def test_expr_14():
    assert run_dsl("x: Bool = 1 == 1\n")["x"] is True

def test_expr_15():
    assert run_dsl("x: Bool = 1 != 2\n")["x"] is True

def test_expr_16():
    assert run_dsl("x: Bool = 3 < 5\n")["x"] is True

def test_expr_17():
    ns = run_dsl("x: Bool = not True\n")
    assert ns["x"] is False

def test_expr_18():
    ns = run_dsl("x: Bool = not False\n")
    assert ns["x"] is True

def test_expr_19():
    src = "x: Int = 0\nif not False:\n    x = 1\n"
    assert run_dsl(src)["x"] == 1

def test_expr_20():
    assert run_dsl("x: Bool = True and False\n")["x"] is False

def test_expr_21():
    assert run_dsl("x: Bool = False or True\n")["x"] is True

def test_expr_22():
    src = 'x: Bytes = b"AB" |> xor(b"\\xff")\n'
    ns  = run_dsl(src)
    assert ns["x"] == bytes([ord("A") ^ 0xFF, ord("B") ^ 0xFF])

def test_expr_23():
    src = 'x: Bytes = b"\\x00\\x01" |> xor(b"\\x01") |> xor(b"\\x01")\n'
    ns  = run_dsl(src)
    assert ns["x"] == b"\x00\x01"

def test_expr_24():
    ns = run_dsl('x: Int = to_int(b"\\x0a")\n')
    assert ns["x"] == 10

#  Assignment

def test_assign_1():
    ns = run_dsl("x: Int = 0\nx = 99\n")
    assert ns["x"] == 99

def test_assign_2():
    ns = run_dsl("x: Int = 10\nx += 5\n")
    assert ns["x"] == 15

def test_assign_3():
    ns = run_dsl("x: Int = 10\nx -= 3\n")
    assert ns["x"] == 7

def test_assign_4():
    ns = run_dsl("x: Int = 3\nx *= 4\n")
    assert ns["x"] == 12

def test_assign_5():
    ns = run_dsl("x: Int = 0xFF\nx ^= 0x0F\n")
    assert ns["x"] == 0xF0

# Imports

def test_import_1():
    assert "import os" in compile_dsl("import os\n")

def test_import_2():
    assert "from os import path" in compile_dsl("from os import path\n")

def test_import_3():
    assert "from os import path, getcwd" in compile_dsl("from os import path, getcwd\n")

def test_import_4():
    assert "import os.path" in compile_dsl("import os.path\n")

# Control Flow

def test_control_1():
    ns = run_dsl("x: Int = 0\nif True:\n    x = 1\n")
    assert ns["x"] == 1

def test_control_2():
    ns = run_dsl("x: Int = 0\nif False:\n    x = 1\n")
    assert ns["x"] == 0

def test_control_3():
    ns = run_dsl("x: Int = 0\nif False:\n    x = 1\nelse:\n    x = 2\n")
    assert ns["x"] == 2

def test_control_4():
    src = (
        "x: Int = 0\n"
        "y: Int = 5\n"
        "if y == 1:\n"
        "    x = 1\n"
        "elif y == 5:\n"
        "    x = 5\n"
        "else:\n"
        "    x = 99\n"
    )
    assert run_dsl(src)["x"] == 5

def test_control_5():
    src = "i: Int = 0\nx: Int = 0\nwhile i < 5:\n    x += i\n    i += 1\n"
    assert run_dsl(src)["x"] == 10   # 0+1+2+3+4

def test_control_6():
    ns = run_dsl("x: Int = 0\nfor i in [1, 2, 3, 4]:\n    x += i\n")
    assert ns["x"] == 10

def test_control_7():
    src = (
        "i: Int = 0\n"
        "while True:\n"
        "    i += 1\n"
        "    if i == 3:\n"
        "        break\n"
    )
    assert run_dsl(src)["i"] == 3

def test_control_8():
    src = (
        "total: Int = 0\n"
        "for i in [1, 2, 3, 4, 5]:\n"
        "    if i == 3:\n"
        "        continue\n"
        "    total += i\n"
    )
    assert run_dsl(src)["total"] == 12   # 1+2+4+5

def test_control_9():
    assert "pass" in compile_dsl("if True:\n    pass\n")

# Repeat

def test_repeat_1():
    ns = run_dsl("x: Int = 0\nrepeat(5):\n    x += 1\n")
    assert ns["x"] == 5

def test_repeat_2():
    ns = run_dsl("x: Int = 1\nrepeat(4):\n    x *= 2\n")
    assert ns["x"] == 16

def test_repeat_3():
    ns = run_dsl("x: Int = 7\nrepeat(0):\n    x = 0\n")
    assert ns["x"] == 7

def test_repeat_4():
    py = compile_dsl("repeat(3):\n    pass\n")
    assert "for _i in range(3):" in py

# Functions

def test_func_1():
    src = "def add(a: Int, b: Int) -> Int:\n    return a + b\n"
    ns  = run_dsl(src)
    assert ns["add"](3, 4) == 7

def test_func_2():
    src = 'def greet() -> String:\n    return "hello"\n'
    ns  = run_dsl(src)
    assert ns["greet"]() == "hello"

def test_func_3():
    src = (
        "def inc(x: Int, step: Int = 1) -> Int:\n"
        "    return x + step\n"
    )
    ns = run_dsl(src)
    assert ns["inc"](5) == 6
    assert ns["inc"](5, 10) == 15

def test_func_4():
    src = (
        "def double(n: Int) -> Int:\n"
        "    result: Int = n * 2\n"
        "    return result\n"
    )
    assert run_dsl(src)["double"](7) == 14

def test_func_5():
    src = (
        "def fact(n: Int) -> Int:\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * fact(n - 1)\n"
    )
    assert run_dsl(src)["fact"](5) == 120

def test_func_6():
    src = (
        "def process(data: Bytes, key: Bytes) -> Bytes:\n"
        "    return data |> xor(key)\n"
    )
    ns = run_dsl(src)
    assert ns["process"](b"\x00\xFF", b"\xFF\xFF") == b"\xFF\x00"

def test_func_7():
    src = "def foo(x: Int, y: Bytes) -> Bool:\n    return True\n"
    py  = compile_dsl(src)
    assert "def foo(x: int, y: bytes) -> bool:" in py

def test_func_8():
    src = "def bar(x: Int):\n    pass\n"
    py  = compile_dsl(src)
    sig_line = next(l for l in py.splitlines() if "def bar" in l)
    assert "->" not in sig_line

# SBox/PBox

def test_sbox_1():
    ns = run_dsl("sbox my_sbox = [0x63, 0x7c, 0x77, 0x7b]\n")
    assert ns["my_sbox"] == [0x63, 0x7C, 0x77, 0x7B]

def test_pbox_1():
    ns = run_dsl("pbox my_pbox = [3, 0, 2, 1]\n")
    assert ns["my_pbox"] == [3, 0, 2, 1]

def test_sbox_2():
    src = (
        "sbox s = [1, 0, 3, 2]\n"
        'x: Bytes = substitute(b"\\x00\\x01\\x02\\x03", s)\n'
    )
    ns = run_dsl(src)
    assert ns["x"] == bytes([1, 0, 3, 2])

def test_pbox_2():
    src = (
        "pbox p = [3, 1, 0, 2]\n"
        'x: Bytes = permute(b"abcd", p)\n'
    )
    ns = run_dsl(src)
    assert ns["x"] == b"dbac"

def test_sbox_3():
    ns = run_dsl("sbox s = [0x03, 0x02, 0x01, 0x00]\n")
    inv = ns["_cs_invert_sbox"](ns["s"])
    assert inv == [3, 2, 1, 0]

def test_sbox_4():
    ns = run_dsl("sbox s = [0x63, 0x7c, 0x77, 0x7b]\n")
    inv = ns["_cs_invert_sbox"](ns["s"])
    assert inv

def test_sbox_5():
    src = (
        "sbox s = [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5]\n"
        "cipher C(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> substitute(s)\n"
    )
    ns = run_dsl(src)
    c = ns["C"](b"\xAA\xBB\xCC\xDD\xEE\xFF\x00\x11")
    pt = bytes(range(8))
    enc = c.encrypt(pt)
    assert c.decrypt(enc) == pt

def test_invert_sbox_6():
    identity = list(range(256))
    swapped  = identity[:]
    swapped[0], swapped[255] = swapped[255], swapped[0]
    entries = ", ".join(str(x) for x in swapped)
    ns  = run_dsl(f"sbox s = [{entries}]\n")
    inv = ns["_cs_invert_sbox"](ns["s"])
    assert all(inv[swapped[i]] == i for i in range(256))

# Inbuilt Functions

def test_xor_1():
    ns = run_dsl('x: Bytes = xor(b"\\xAA", b"\\xFF")\n')
    assert ns["x"] == bytes([0xAA ^ 0xFF])

def test_xor_2():
    src = 'x: Bytes = xor(b"\\x01\\x02\\x03\\x04", b"\\xFF")\n'
    ns  = run_dsl(src)
    assert ns["x"] == bytes([0x01^0xFF, 0x02^0xFF, 0x03^0xFF, 0x04^0xFF])

def test_rotl_1():
    ns = run_dsl("x: Int = rotl(1, 1, 8)\n")
    assert ns["x"] == 2

def test_rotr_1():
    ns = run_dsl("x: Int = rotr(2, 1, 8)\n")
    assert ns["x"] == 1

def test_rotl_2():
    ns = run_dsl("x: Int = rotl(0x80, 1, 8)\n")
    assert ns["x"] == 1

def test_pad_1():
    src = 'x: Bytes = pad(b"hello", PKCS7, 8)\n'
    ns  = run_dsl(src)
    assert len(ns["x"]) == 8
    assert ns["x"].endswith(bytes([3, 3, 3]))   # 5 bytes + 3-byte padding

def test_unpad_1():
    src = 'x: Bytes = unpad(b"hello\\x03\\x03\\x03", PKCS7)\n'
    ns  = run_dsl(src)
    assert ns["x"] == b"hello"

def test_pad_2():
    src = 'x: Bytes = pad(b"hi", ZERO, 4)\n'
    ns  = run_dsl(src)
    assert ns["x"] == b"hi\x00\x00"

def test_pad_3():
    py = compile_dsl('x: Bytes = pad(b"hi", PKCS7)\n')
    assert '"PKCS7"' in py
    assert "= PKCS7" not in py

def test_pad_4():
    py = compile_dsl('x: Bytes = pad(b"hi", ZERO)\n')
    assert '"ZERO"' in py
    assert "= ZERO" not in py

def test_to_bytes_1():
    ns = run_dsl("x: Bytes = to_bytes(255, 1)\n")
    assert ns["x"] == b"\xFF"

def test_to_bytes_2():
    ns = run_dsl('x: Bytes = to_bytes("hi")\n')
    assert ns["x"] == b"hi"

def test_to_le_bytes_1():
    ns = run_dsl("x: Bytes = to_le_bytes(256, 2)\n")
    assert ns["x"] == b"\x00\x01"

def test_to_be_bytes_1():
    ns = run_dsl("x: Bytes = to_be_bytes(256, 2)\n")
    assert ns["x"] == b"\x01\x00"

def test_to_hex_1():
    ns = run_dsl("x: Hex = to_hex(255)\n")
    assert ns["x"] == "0xff"

def test_to_hex_2():
    ns = run_dsl('x: Hex = to_hex(b"\\xff")\n')
    assert ns["x"] == "0xff"

def test_to_string_1():
    ns = run_dsl('x: String = to_string(b"hello")\n')
    assert ns["x"] == "hello"

def test_to_int_2():
    ns = run_dsl('x: Int = to_int(b"\\x0a")\n')
    assert ns["x"] == 10

# ModInt

def test_modint_1():
    ns     = run_dsl("a: ModInt[7] = 5\nb: ModInt[7] = 4\n")
    result = ns["a"] + ns["b"]
    assert int(result) == 2

def test_modint_2():
    ns     = run_dsl("a: ModInt[7] = 2\nb: ModInt[7] = 5\n")
    result = ns["a"] - ns["b"]
    assert int(result) == 4

def test_modint_3():
    ns     = run_dsl("a: ModInt[7] = 3\nb: ModInt[7] = 5\n")
    result = ns["a"] * ns["b"]
    assert int(result) == 1   # 15 % 7

def test_modint_4():
    ns     = run_dsl("a: ModInt[13] = 2\n")
    result = ns["a"] ** 10
    assert int(result) == pow(2, 10, 13)

def test_modint_5():
    ns = run_dsl("a: ModInt[5] = 7\n")
    assert ns["a"] == 2   # 7 % 5

def test_modint_6():
    src = (
        "def mod_add(a: ModInt[7], b: ModInt[7]) -> ModInt[7]:\n"
        "    return a + b\n"
    )
    ns     = run_dsl(src)
    ModInt = ns["ModInt"]
    result = ns["mod_add"](ModInt(5, 7), ModInt(4, 7))
    assert int(result) == 2   # (5+4) % 7

# Cipher

def test_cipher_1():
    src = (
        "sbox s = [1, 0, 3, 2]\n"
        "cipher Toy(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key) |> substitute(s)\n"
    )
    py = compile_dsl(src)
    assert "class Toy:" in py
    assert "def __init__(self, key: bytes):" in py
    assert "def encrypt(self, data):" in py
    assert "def decrypt(self, data):" in py
    encrypt_idx = py.index("def encrypt")
    encrypt_section = py[encrypt_idx:]
    assert "self.key" in encrypt_section
    for fn in ("xor", "substitute", "permute", "rotl", "rotr",
                "pad", "unpad", "to_bytes", "to_hex",
                "_cs_invert_sbox", "_cs_invert_pbox"):
        assert f"def {fn}" in py or f"def {fn}(" in py
    assert "class ModInt:" in py
    assert "class Matrix:" in py

def test_cipher_2():
    src = (
        "cipher Bare() -> Bytes:\n"
        "    encrypt:\n"
        '        data |> xor(b"\\x01")\n'
    )
    py = compile_dsl(src)
    assert "def __init__(self):" in py
    assert "def __init__(self, ):" not in py

def test_cipher_3():
    src = (
        "cipher XorCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key)\n"
    )
    ns = run_dsl(src)
    c  = ns["XorCipher"](b"\xFF")
    assert c.encrypt(b"\xAA") == bytes([0xAA ^ 0xFF])
    plaintext = b"\x01\x02\x03\x04"
    assert c.decrypt(c.encrypt(plaintext)) == plaintext

def test_cipher_4():
    src = (
        "sbox s = [3, 2, 1, 0]\n"
        "cipher SubCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> substitute(s)\n"
    )
    ns = run_dsl(src)
    c  = ns["SubCipher"](b"")
    assert c.encrypt(bytes([0, 1, 2, 3])) == bytes([3, 2, 1, 0])
    plaintext = bytes([0, 1, 2, 3])
    assert c.decrypt(c.encrypt(plaintext)) == plaintext

def test_cipher_5():
    src = (
        "sbox s = [1, 0, 3, 2, 5, 4, 7, 6]\n"
        "cipher TwoStep(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key) |> substitute(s)\n"
    )
    ns        = run_dsl(src)
    cipher    = ns["TwoStep"](b"\x00")
    plaintext = bytes([0, 1, 2, 3, 4, 5, 6, 7])
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_cipher_6():
    src = (
        "cipher PadCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> pad(PKCS7) |> xor(key)\n"
    )
    ns        = run_dsl(src)
    cipher    = ns["PadCipher"](b"\xFF")
    plaintext = b"hello"
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_cipher_7():
    src = (
        "cipher RepCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> repeat(3):\n"
        "            xor(key)\n"
    )
    ns     = run_dsl(src)
    cipher = ns["RepCipher"](b"\xFF\xFF")
    assert cipher.encrypt(b"\x00\x00") == b"\xFF\xFF"
    plaintext = b"\xBE\xEF"
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_cipher_8():
    src = (
        "sbox s = [1, 0, 3, 2]\n"
        "cipher FullCipher(key: Bytes, iv: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(iv) |> substitute(s) |> xor(key)\n"
    )
    ns        = run_dsl(src)
    cipher    = ns["FullCipher"](b"\x00", b"\x00")
    plaintext = bytes([0, 1, 2, 3])
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_cipher_9():
    src = (
        "cipher RotCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> rotl(3, 8)\n"
    )
    ns        = run_dsl(src)
    cipher    = ns["RotCipher"](b"")
    plaintext = 0b00001111
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_cipher_10():
    src = (
        "cipher NullCipher() -> Bytes:\n"
        "    encrypt:\n"
        '        data |> xor(b"\\xAA")\n'
    )
    ns     = run_dsl(src)
    cipher = ns["NullCipher"]()
    assert cipher.encrypt(b"\xAA") == b"\x00"
    assert cipher.decrypt(b"\x00") == b"\xAA"

def test_cipher_11():
    src = (
        "sbox s = [1, 0, 3, 2]\n"
        "cipher RevCheck(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key) |> substitute(s)\n"
    )
    py = compile_dsl(src)
    decrypt_idx   = py.index("def decrypt")
    decrypt_body  = py[decrypt_idx:]
    sub_pos = decrypt_body.index("substitute")
    xor_pos = decrypt_body.index("xor")
    assert sub_pos < xor_pos, \
        "In decrypt, substitute (inverse first step) should precede xor (inverse second step)"

def test_cipher_13():
    src = (
        "cipher BadCipher(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> my_func(key)\n"
    )
    ns     = run_dsl(src)
    cipher = ns["BadCipher"](b"")
    with pytest.raises(NotImplementedError):
        cipher.decrypt(b"x")

#  Match

def test_match_1():
    src = (
        "x: Int = 0\n"
        "y: Int = 2\n"
        "match y:\n"
        "    case 1:\n"
        "        x = 10\n"
        "    case 2:\n"
        "        x = 20\n"
    )
    assert run_dsl(src)["x"] == 20

def test_match_2():
    src = (
        "x: Int = 0\n"
        "y: Int = 9\n"
        "match y:\n"
        "    case 1:\n"
        "        x = 10\n"
    )
    assert run_dsl(src)["x"] == 0

def test_match_3():
    src = (
        "val: Int = 99\n"
        "match val:\n"
        "    case 1:\n"
        "        r: Int = 1\n"
        "    case _:\n"
        "        r: Int = 99\n"
    )
    assert run_dsl(src)["r"] == 99

def test_match_4():
    src = (
        "val: Int = 7\n"
        "r: Int = 0\n"
        "match val:\n"
        "    case _:\n"
        "        r = 55\n"
    )
    assert run_dsl(src)["r"] == 55

# With

def test_with_1():
    src = (
        'result: String = ""\n'
        'with open("./cryptoscript/ast_nodes.py") as f:\n'
        '    result = "opened"\n'
    )
    assert run_dsl(src)["result"] == "opened"

# Generation

def test_gen_1():
    py = compile_dsl("x: Int = 0\n")
    for name in ("xor", "substitute", "permute", "pad", "unpad",
                    "rotl", "rotr", "to_bytes", "to_hex",
                    "_cs_invert_sbox", "_cs_invert_pbox"):
        assert f"def {name}(" in py
    assert "class ModInt:" in py
    assert "class Matrix:" in py

def test_gen_2():
    src = (
        "sbox s = [0, 1, 2, 3]\n"
        "cipher Demo(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> substitute(s) |> xor(key)\n"
        "def helper(x: Int) -> Int:\n"
        "    return x * 2\n"
    )
    py = compile_dsl(src)
    compile(py, "<generated>", "exec")

def test_gen_3():
    py = compile_dsl("")
    assert isinstance(py, str)
    compile(py, "<empty>", "exec")

def test_gen_4():
    src = (
        "sbox s = [1, 0, 3, 2]\n"
        "pbox p = [3, 2, 1, 0]\n"
        "cipher Multi(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> substitute(s) |> permute(p) |> xor(key)\n"
    )
    py = compile_dsl(src)
    assert "def encrypt" in py
    assert "def decrypt" in py
    assert "_cs_invert_sbox" in py
    assert "_cs_invert_pbox" in py

def test_gen_5():
    from cryptoscript.ast_nodes import (
        Program, ExprStmt, PipelineExpr,
        BytesLit, FuncCall, RepeatBlock, IntLit,
    )
    inner_call = FuncCall(name="xor", args=[BytesLit(value="\\x01")])
    inner_pipeline = PipelineExpr(
        base=BytesLit(value=""), steps=[inner_call]
    )
    repeat_step = RepeatBlock(count=IntLit(value=2), pipeline=inner_pipeline)
    pipeline    = PipelineExpr(
        base=BytesLit(value="hi"),
        steps=[repeat_step],
    )
    tree = Program(statements=[ExprStmt(expr=pipeline)])
    with pytest.raises(CodeGenError, match="repeat"):
        CodeGen().generate(tree)

def test_gen_6():
    from cryptoscript.ast_nodes import Program, ASTNode
    class UnknownStmt(ASTNode):
        pass
    tree = Program(statements=[UnknownStmt()])
    with pytest.raises(CodeGenError, match="No code generator"):
        CodeGen().generate(tree)

def test_gen_7():
    from cryptoscript.ast_nodes import Program, ExprStmt, ASTNode
    class UnknownExpr(ASTNode):
        pass
    tree = Program(statements=[ExprStmt(expr=UnknownExpr())])
    with pytest.raises(CodeGenError, match="No code generator"):
        CodeGen().generate(tree)

# Full Tests

def test_full_1():
    sbox_entries = list(range(1, 256)) + [0]
    entries_src  = ", ".join(str(v) for v in sbox_entries)
    src = (
        f"sbox caesar = [{entries_src}]\n"
        "cipher Caesar(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> substitute(caesar)\n"
    )
    ns = run_dsl(src)
    c  = ns["Caesar"](b"")
    pt = bytes([65, 66, 67])   # ABC
    ct = c.encrypt(pt)
    assert ct == bytes([66, 67, 68])   # BCD
    assert c.decrypt(ct) == pt

def test_full_2():
    src = (
        "cipher XorRot(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key) |> rotl(1, 8)\n"
    )
    ns        = run_dsl(src)
    cipher    = ns["XorRot"](b"\xFF")
    plaintext = b"\x0F"
    assert cipher.decrypt(cipher.encrypt(plaintext)) == plaintext

def test_full_3():
    src = (
        "def fib(n: Int) -> Int:\n"
        "    if n <= 1:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 2)\n"
    )
    ns = run_dsl(src)
    assert [ns["fib"](i) for i in range(8)] == [0, 1, 1, 2, 3, 5, 8, 13]

def test_full_4():
    src = (
        "def mod_exp(base: ModInt[13], exp: Int) -> ModInt[13]:\n"
        "    return base ** exp\n"
    )
    ns     = run_dsl(src)
    ModInt = ns["ModInt"]
    result = ns["mod_exp"](ModInt(3, 13), 4)
    assert int(result) == pow(3, 4, 13)

def test_full_5():
    src = (
        "def gen_keys(base_key: Bytes, rounds: Int) -> Int:\n"
        "    count: Int = 0\n"
        "    k: Bytes = base_key\n"
        "    for i in [0, 1, 2, 3]:\n"
        "        k = xor(k, to_bytes(i + 1, 1))\n"
        "        count += 1\n"
        "    return count\n"
    )
    ns = run_dsl(src)
    assert ns["gen_keys"](b"\x00", 4) == 4

def test_full_6():
    src = "x: Bool = not (False or False) and True\n"
    ns  = run_dsl(src)
    assert ns["x"] is True

def test_full_7():
    src = (
        "found: Int = 0\n"
        "i: Int = 0\n"
        "while not found == 1:\n"
        "    i += 1\n"
        "    if i == 5:\n"
        "        found = 1\n"
    )
    ns = run_dsl(src)
    assert ns["i"] == 5
    assert ns["found"] == 1

def test_full_8() :
    src = (
        "sbox s = [1, 0, 3, 2, 5, 4, 7, 6]\n"
        "\n"
        "cipher FancyCipher(key: Bytes, iv: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> pad(PKCS7) |> xor(iv) |> repeat(3):\n"
        "            xor(key) |> substitute(s)\n"
        "        |> xor(key)\n"
        "\n"
        "mycipher = FancyCipher(b\"\xAA\", b\"\x55\")\n"
        "plaintext = b\"\x00\x01\x02\x03\"\n"
        "\n"
        "encrypted = mycipher.encrypt(plaintext)\n"
        "decrypted = mycipher.decrypt(encrypted)"
    )
    ns = run_dsl(src)
    assert ns["decrypted"] == ns["plaintext"]

#Test Method Call Generation

def test_method_call_1():
    src = compile_dsl("result = myobj.mymethod(1, 2)\n")
    assert "myobj.mymethod(1, 2)" in src

def test_method_call_2():
    ns = run_dsl("result = data.hex()\n", extra_globals={"data": b"\xde\xad"})
    assert ns["result"] == "dead"

def test_method_call_3():
    ns = run_dsl('result = msg.encode("utf-8")\n', extra_globals={"msg": "hi"})
    assert ns["result"] == b"hi"

def test_chained_4():
    src = compile_dsl("result = hashlib.sha256(data).digest()\n")
    assert "digest()" in src
    assert "hashlib.sha256(" in src