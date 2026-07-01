import pytest
from cryptoscript.lexer import Lexer
from cryptoscript.parser import Parser
from cryptoscript.codegen import CodeGen
from cryptoscript.type_checker import TypeChecker, TypeCheckError

# Helpers

def typecheck(source: str):
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens, source).parse()
    TypeChecker(source).check(ast)

def assert_ok(source: str):
    typecheck(source)

def assert_type_error(source: str):
    with pytest.raises(TypeCheckError):
        typecheck(source)

# Variable Declaration

def test_var_1():
    assert_ok("x: Int = 42\n")

def test_var_2():
    assert_ok("x: Int = 0xFF\n")

def test_var_3():
    assert_ok("x: Hex = 42\n")

def test_var_4():
    assert_ok('x: Bytes = b"\\xAA"\n')

def test_var_5():
    assert_ok('x: String = "hello"\n')

def test_var_6():
    assert_ok("x: Bool = True\n")

def test_var_7():
    assert_ok("x: ModInt[7] = 5\n")

def test_var_8():
    assert_ok("x: ModInt[7] = 0xFF\n")

def test_var_9():
    assert_type_error('x: Int = b"\\xAA"\n')

def test_var_10():
    assert_type_error("x: Bytes = 42\n")

def test_var_11():
    assert_type_error('x: Int = "hello"\n')

def test_var_12():
    assert_type_error('x: Bytes = "hello"\n')

def test_var_13():
    assert_type_error(
        "a: ModInt[13] = 5\n"
        "b: ModInt[7] = a\n"
    )

# Assignment

def test_assign_1():
    assert_ok("x: Int = 1\nx = 2\n")

def test_assign_2():
    assert_ok("x: Int = 1\nx = 0xFF\n")

def test_assign_3():
    assert_type_error('x: Int = 1\nx = b"\\xAA"\n')

def test_assign_4():
    assert_type_error('x: Bytes = b"\\x00"\nx = 42\n')

def test_assign_5():
    assert_ok("x = 42\ny = x + 1\n")

def test_assign_6():
    assert_ok("x: Int = 5\nx += 1\n")

def test_assign_7():
    assert_type_error("x = 42\nx = \"hello\"\n")

# Binary Operations

def test_binops_1():
    assert_ok("x: Int = 1 + 2\n")

def test_binops_2():
    assert_ok("x: Int = 0xFF + 1\n")

def test_binops_3():
    assert_type_error('x: Int = b"\\xAA" + 1\n')

def test_binops_4():
    assert_type_error('x = b"\\xAA" * 2\n')

def test_binops_5():
    assert_ok("a: ModInt[7] = 3\nb: ModInt[7] = 4\nc = a + b\n")

def test_binops_6():
    assert_type_error("a: ModInt[7] = 3\nb: ModInt[13] = 4\nc = a + b\n")

def test_binops_7():
    assert_ok("x: Bool = 1 < 2\n")

def test_binops_8():
    assert_ok("x: Bool = True and False\n")

def test_binops_9():
    assert_ok("a: ModInt[7] = 3\nb = a + 1\n")

# Unary Operations

def test_unary_1():
    assert_ok("x: Int = -5\n")

def test_unary_2():
    assert_ok("x: Bool = not True\n")

def test_unary_3():
    assert_type_error('x = -b"\\xAA"\n')

def test_unary_4():
    assert_ok("x: Int = ~0xFF\n")

def test_unary_5():
    assert_type_error('x = ~b"\\xAA"\n')

# Func Def

def test_funcdef_1():
    assert_ok("def add(a: Int, b: Int) -> Int:\n    return a + b\n")

def test_funcdef_2():
    assert_ok("def foo(x: Int):\n    pass\n")

def test_funcdef_3():
    assert_type_error(
        "def f() -> Int:\n"
        '    return b"\\xAA"\n'
    )

def test_funcdef_4():
    assert_ok(
        "def f(x: Bytes) -> Bytes:\n"
        "    return x\n"
    )

def test_funcdef_5():
    assert_type_error(
        "def f(a: Int, b: Int) -> Int:\n"
        "    return a + b\n"
        "y = f(1)\n"
    )

def test_funcdef_6():
    assert_type_error(
        "def f(a: Bytes) -> Bytes:\n"
        "    return a\n"
        "y = f(42)\n"
    )

def test_funcdef_7():
    assert_ok(
        "def f(a: Int, b: Int) -> Int:\n"
        "    return a + b\n"
        "y = f(1, 2)\n"
    )

def test_funcdef_8():
    assert_ok(
        "def f(a: Int) -> Int:\n"
        "    return a\n"
    )

def test_funcdef_9():
    assert_ok(
        "def fact(n: Int) -> Int:\n"
        "    if n <= 1:\n"
        "        return 1\n"
        "    return n * fact(n - 1)\n"
    )

def test_funcdef_10():
    assert_ok(
        "def mod_add(a: ModInt[7], b: ModInt[7]) -> ModInt[7]:\n"
        "    return a + b\n"
    )

# Pipeline

def test_pipeline_1():
    assert_ok('result = b"\\x01" |> xor(b"\\xFF")\n')

def test_pipeline_2():
    assert_ok("sbox s = [1, 0, 3, 2]\nresult = b\"\\x00\" |> substitute(s)\n")

def test_pipeline_3():
    assert_ok('result = b"hello" |> pad(PKCS7)\n')

def test_pipeline_4():
    assert_ok('result = b"\\xAA" |> to_hex()\n')

def test_pipeline_5():
    assert_ok('result = b"\\xAA" |> to_int()\n')

def test_pipeline_6():
    assert_type_error("result = 42 |> xor(b\"\\xFF\")\n")

def test_pipeline_7():
    assert_type_error("sbox s = [1, 0]\nresult = 42 |> substitute(s)\n")

def test_pipeline_8():
    assert_type_error("result = 42 |> pad(PKCS7)\n")

def test_pipeline_9():
    assert_type_error("result = 0xFF |> xor(b\"\\xAA\")\n")

def test_pipeline_10():
    assert_ok('result = b"\\xAA" |> xor(b"\\xFF") |> to_hex()\n')

def test_pipeline_11():
    assert_type_error('result = b"\\xAA" |> to_hex() |> xor(b"\\xFF")\n')

def test_pipeline_12():
    assert_ok("pbox p = [0, 1, 2, 3]\nresult = b\"\\x01\\x02\\x03\\x04\" |> permute(p)\n")

# Cipher Def

def test_cipherdef_1():
    assert_ok(
        "cipher C(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key)\n"
    )

def test_cipherdef_2():
    assert_ok(
        "sbox s = [1, 0, 3, 2]\n"
        "cipher C(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(key) |> substitute(s)\n"
    )

def test_cipherdef_3():
    assert_type_error(
        "cipher C(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> to_hex() |> xor(key)\n"
    )

def test_cipherdef_4():
    assert_ok(
        "cipher C(key: Bytes, iv: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> xor(iv) |> xor(key)\n"
    )

def test_cipherdef_5():
    assert_ok(
        "sbox s = [1, 0, 3, 2]\n"
        "cipher C(key: Bytes) -> Bytes:\n"
        "    encrypt:\n"
        "        data |> repeat(4):\n"
        "            xor(key) |> substitute(s)\n"
    )

# SBox/PBox

def test_sbox_1():
    assert_ok("sbox s = [0, 1, 2, 3]\n")

def test_sbox_2():
    assert_ok("sbox s = [0x00, 0x01, 0x02, 0x03]\n")

def test_sbox_3():
    assert_type_error('sbox s = [0, "hello", 2]\n')

def test_pbox_1():
    assert_ok("pbox p = [3, 1, 0, 2]\n")

def test_pbox_2():
    assert_type_error("pbox p = [0, -1, 2]\n")

def test_pbox_3():
    assert_type_error('pbox p = [0, "a", 2]\n')

# Control Flow

def test_control_1():
    assert_ok(
        "x: Int = 5\n"
        "if x > 3:\n"
        "    y: Int = 1\n"
    )

def test_control_2():
    assert_ok(
        "x: Int = 5\n"
        "if x > 3:\n"
        "    y: Int = 1\n"
        "else:\n"
        "    y: Int = 0\n"
    )

def test_control_3():
    assert_ok(
        "x: Int = 0\n"
        "while x < 10:\n"
        "    x += 1\n"
    )

def test_control_4():
    assert_ok(
        "total: Int = 0\n"
        "for i in range(5):\n"
        "    total += i\n"
    )

def test_control_5():
    assert_ok(
        "x: Int = 0\n"
        "repeat(5):\n"
        "    x += 1\n"
    )

def test_control_6():
    assert_type_error(
        'x: Int = 0\n'
        'repeat(b"\\xAA"):\n'
        '    x += 1\n'
    )

def test_control_7():
    assert_ok(
        "val: Int = 2\n"
        "match val:\n"
        "    case 1:\n"
        "        r: Int = 10\n"
        "    case 2:\n"
        "        r: Int = 20\n"
    )

# Subscript

def test_subscript_1():
    assert_ok('x: Bytes = b"\\x01\\x02"\ny: Int = x[0]\n')

def test_subscript_2():
    assert_ok("x = [1, 2, 3]\ny = x[0]\n")

def test_subscript_3():
    assert_type_error('x = [1, 2, 3]\ny = x[b"\\x00"]\n')

def test_subscript_4():
    assert_type_error('x = [1, 2, 3]\ny = x["a"]\n')

# Mod Int

def test_modint_1():
    assert_ok(
        "a: ModInt[7] = 3\n"
        "b: ModInt[7] = 5\n"
        "c = a + b\n"
    )

def test_modint_2():
    assert_type_error(
        "a: ModInt[7] = 3\n"
        "b: ModInt[13] = 5\n"
        "c = a + b\n"
    )

def test_modint_3():
    assert_ok("a: ModInt[7] = 3\nc = a + 1\n")

def test_modint_4():
    assert_ok("a: ModInt[7] = 10\n")

def test_modint_5():
    assert_type_error('a: ModInt[7] = b"\\xAA"\n')

def test_modint_6():
    assert_ok(
        "def f(a: ModInt[7], b: ModInt[7]) -> ModInt[7]:\n"
        "    return a + b\n"
        "x: ModInt[7] = 3\n"
        "y: ModInt[7] = 4\n"
        "z = f(x, y)\n"
    )

# Unknown

def test_unknown_1():
    assert_ok("import hashlib\nresult = hashlib.sha256(b\"\\x01\")\n")

def test_unknown_2():
    assert_ok("result = myobj.method\n")

def test_unknown_3():
    assert_ok("x: Int = None\n")

def test_unknown_4():
    assert_ok("x = [1, 2, 3]\n")

def test_unknown_5():
    assert_ok("result = some_data |> to_hex()\n")