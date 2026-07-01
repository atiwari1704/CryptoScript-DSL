import pytest
from cryptoscript.lexer import Lexer
from cryptoscript.parser import Parser, ParseError
from cryptoscript.ast_nodes import *

def parse(src: str) :
    return Parser(Lexer(src).tokenize(), src).parse()

def first(src: str):
    return parse(src).statements[0]

# ==================================================================
#  AST NODE
# ==================================================================

def test_nodes_1():
    nodes = [
        SimpleType("Int"), ModIntType(7), MatrixType(SimpleType("Int"), 2, 2), MatrixType(ModIntType(7), 2, 2),
        IntLit(1), HexLit("0xFF"), BytesLit("ab"), StringLit("hi"),
        BoolLit(True), NoneLit(), ListLit([]),
        Ident("x"), Attribute(Ident("x"), "y"), Subscript(Ident("x"), IntLit(0)),
        BinOp(IntLit(1), "+", IntLit(2)), UnaryOp("-", IntLit(1)),
        FuncCall("f"), PipelineExpr(Ident("x")),
        ExprStmt(IntLit(1)), VarDecl("x", SimpleType("Int")),
        AssignStmt(Ident("x"), "=", IntLit(1)), ReturnStmt(),
        BreakStmt(), ContinueStmt(), PassStmt(),
        ImportStmt("os"), Param("x", SimpleType("Int")),
        FuncDef("f", [], None, []),
        SboxDef("s"), PboxDef("p"),
        EncryptBlock(PipelineExpr(Ident("d"))),
        CipherDef("C", [], None, EncryptBlock(PipelineExpr(Ident("d")))),
        RepeatStmt(IntLit(4)), RepeatBlock(IntLit(4), PipelineExpr(Ident("d"))),
        IfStmt(BoolLit(True), []), WhileStmt(BoolLit(True)),
        ForStmt("x", Ident("items")), CaseClause(IntLit(1)),
        MatchStmt(Ident("x")), WithStmt(Ident("f")),
        Program(),
    ]
    for node in nodes:
        assert isinstance(node, ASTNode), f"{type(node).__name__} does not inherit ASTNode"

# ==================================================================
#  TYPE
# ==================================================================

def test_type_1():
    assert SimpleType("Int").name == "Int"

def test_type_2():
    assert ModIntType(17).modulus == 17

def test_type_3():
    m = MatrixType(SimpleType("Int"), 3, 4)
    assert m.rows == 3
    assert m.cols == 4
    assert isinstance(m.elem_type, SimpleType)

def test_type_3():
    m = MatrixType(ModIntType(7), 3, 4)
    assert m.rows == 3
    assert m.cols == 4
    assert isinstance(m.elem_type, ModIntType)

# ==================================================================
#  Literals
# ==================================================================

def test_lit_1():
    assert IntLit(42).value == 42

def test_lit_2():
    assert HexLit("0xFF").value == "0xFF"

def test_lit_3():
    assert BytesLit("ab").value == "ab"

def test_lit_4():
    assert StringLit("hello").value == "hello"

def test_lit_5():
    assert BoolLit(True).value is True

def test_lit_6():
    assert BoolLit(False).value is False

def test_lit_7():
    assert isinstance(NoneLit(), NoneLit)

def test_lit_8():
    assert ListLit().elements == []

def test_lit_9():
    lst = ListLit([IntLit(1), IntLit(2)])
    assert len(lst.elements) == 2

# ==================================================================
#  Expressions
# ==================================================================

def test_expr_1():
    assert Ident("x").name == "x"

def test_expr_2():
    a = Attribute(Ident("obj"), "method")
    assert a.attr == "method"
    assert isinstance(a.obj, Ident)

def test_expr_3():
    s = Subscript(Ident("arr"), IntLit(0))
    assert isinstance(s.index, IntLit)

def test_expr_4():
    b = BinOp(IntLit(1), "+", IntLit(2))
    assert b.op == "+"
    assert isinstance(b.left, IntLit)
    assert isinstance(b.right, IntLit)

def test_expr_5():
    u = UnaryOp("-", IntLit(5))
    assert u.op == "-"
    assert isinstance(u.operand, IntLit)

def test_expr_6():
    f = FuncCall("xor", [Ident("key")])
    assert f.name == "xor"
    assert len(f.args) == 1

def test_expr_7():
    assert FuncCall("f").args == []

def test_expr_8():
    p = PipelineExpr(Ident("data"), [FuncCall("xor", [Ident("k")])])
    assert isinstance(p.base, Ident)
    assert len(p.steps) == 1

# ==================================================================
# IMPORTS
# ==================================================================

def test_import_1():
    stmt = first("import os\n")
    assert isinstance(stmt, ImportStmt)
    assert stmt.module == "os"
    assert stmt.names == []

def test_import_2():
    stmt = first("import os.path\n")
    assert isinstance(stmt, ImportStmt)
    assert stmt.module == "os.path"

def test_import_3():
    stmt = first("from math import gcd\n")
    assert isinstance(stmt, ImportStmt)
    assert stmt.module == "math"
    assert stmt.names == ["gcd"]

def test_import_4():
    stmt = first("from math import gcd, pow\n")
    assert stmt.names == ["gcd", "pow"]

# ==================================================================
# VAR DECL
# ==================================================================

def test_vardecl_1():
    stmt = first("x: Int\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, SimpleType)
    assert stmt.type.name == "Int"
    assert stmt.value is None

def test_vardecl_2():
    stmt = first("x: Int = 42\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, SimpleType)
    assert stmt.type.name == "Int"
    assert isinstance(stmt.value, IntLit)
    assert stmt.value.value == 42

def test_vardecl_3():
    stmt = first("key: Bytes\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "key"
    assert isinstance(stmt.type, SimpleType)
    assert stmt.type.name == "Bytes"
    assert stmt.value is None

def test_vardecl_4():
    stmt = first("x: Hex\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, SimpleType)
    assert stmt.type.name == "Hex"
    assert stmt.value is None

def test_vardecl_5():
    stmt = first("x: ModInt[17]\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, ModIntType)
    assert stmt.type.modulus == 17
    assert stmt.value is None

def test_vardecl_6():
    stmt = first("x: Matrix[Int, 3, 4]\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, MatrixType)
    assert stmt.value is None
    assert stmt.type.rows == 3
    assert stmt.type.cols == 4

def test_vardecl_7():
    stmt = first("x: Matrix[ModInt[7], 2, 2]\n")
    assert isinstance(stmt, VarDecl)
    assert stmt.name == "x"
    assert isinstance(stmt.type, MatrixType)
    assert stmt.value is None
    assert stmt.type.rows == 2
    assert stmt.type.cols == 2
    assert isinstance(stmt.type.elem_type, ModIntType)
    assert stmt.type.elem_type.modulus == 7

# ==================================================================
# ASSIGNMENT
# ==================================================================

def test_assign_1():
    stmt = first("x = 42\n")
    assert isinstance(stmt, AssignStmt)
    assert stmt.op == "="
    assert isinstance(stmt.value, IntLit)

def test_assign_2():
    stmt = first("x += 1\n")
    assert isinstance(stmt, AssignStmt)
    assert stmt.op == "+="

def test_assign_3():
    stmt = first("x -= 1\n")
    assert stmt.op == "-="

def test_assign_4():
    stmt = first("x *= 2\n")
    assert stmt.op == "*="

def test_assign_5():
    stmt = first("x //= 2\n")
    assert stmt.op == "//="

# ==================================================================
# EXPRESSIONS
# ==================================================================

def test_expr_1():
    stmt = first("42\n")
    assert isinstance(stmt.expr, IntLit)
    assert stmt.expr.value == 42

def test_expr_2():
    stmt = first("0xFF\n")
    assert isinstance(stmt.expr, HexLit)
    assert stmt.expr.value == "0xFF"

def test_expr_3():
    stmt = first('"hello"\n')
    assert isinstance(stmt.expr, StringLit)
    assert stmt.expr.value == "hello"

def test_expr_4():
    stmt = first("True\n")
    assert isinstance(stmt.expr, BoolLit)
    assert stmt.expr.value is True

def test_expr_5():
    stmt = first("False\n")
    assert isinstance(stmt.expr, BoolLit)
    assert stmt.expr.value is False

def test_expr_6():
    stmt = first("None\n")
    assert isinstance(stmt.expr, NoneLit)

def test_expr_7():
    stmt = first("my_var\n")
    assert isinstance(stmt.expr, Ident)
    assert stmt.expr.name == "my_var"

def test_expr_8():
    stmt = first("1 + 2\n")
    assert isinstance(stmt.expr, BinOp)
    assert stmt.expr.op == "+"

def test_expr_9():
    stmt = first("a - b\n")
    assert stmt.expr.op == "-"

def test_expr_10():
    stmt = first("a * b\n")
    assert stmt.expr.op == "*"

def test_expr_11():
    stmt = first("a % n\n")
    assert stmt.expr.op == "%"

def test_expr_12():
    stmt = first("a ** b\n")
    assert stmt.expr.op == "**"

def test_expr_13():
    stmt = first("a & b\n")
    assert stmt.expr.op == "&"

def test_expr_14():
    stmt = first("a | b\n")
    assert stmt.expr.op == "|"

def test_expr_15():
    stmt = first("a ^ b\n")
    assert stmt.expr.op == "^"

def test_expr_16():
    stmt = first("a == b\n")
    assert stmt.expr.op == "=="

def test_expr_17():
    stmt = first("a != b\n")
    assert stmt.expr.op == "!="

def test_expr_18():
    stmt = first("a < b\n")
    assert stmt.expr.op == "<"

def test_expr_19():
    stmt = first("a <= b\n")
    assert stmt.expr.op == "<="

def test_expr_20():
    stmt = first("a + b * c\n")
    assert stmt.expr.op == "+"
    assert stmt.expr.right.op == "*"

def test_expr_21():
    stmt = first("a ** b ** c\n")
    assert stmt.expr.op == "**"
    assert stmt.expr.right.op == "**"

def test_expr_22():
    stmt = first("(1 + 2)\n")
    assert isinstance(stmt.expr, BinOp)

def test_expr_23():
    stmt = first("[1, 2, 3]\n")
    assert isinstance(stmt.expr, ListLit)
    assert len(stmt.expr.elements) == 3

def test_expr_24():
    stmt = first("[]\n")
    assert isinstance(stmt.expr, ListLit)
    assert stmt.expr.elements == []

def test_expr_25():
    stmt = first("arr[0]\n")
    assert isinstance(stmt.expr, Subscript)

def test_expr_26():
    stmt = first("obj.attr\n")
    assert isinstance(stmt.expr, Attribute)
    assert stmt.expr.attr == "attr"

def test_expr_27():
    stmt = first("f()\n")
    assert isinstance(stmt.expr, FuncCall)
    assert stmt.expr.name == "f"
    assert stmt.expr.args == []

def test_expr_28():
    stmt = first("xor(key)\n")
    assert isinstance(stmt.expr, FuncCall)
    assert len(stmt.expr.args) == 1

def test_expr_29():
    stmt = first("rotl(x, 3)\n")
    assert len(stmt.expr.args) == 2

# ==================================================================
# PIPELINE OP
# ==================================================================

def test_pipeline_1():
    stmt = first("data |> xor(key)\n")
    assert isinstance(stmt.expr, PipelineExpr)
    assert isinstance(stmt.expr.base, Ident)
    assert stmt.expr.base.name == "data"
    assert len(stmt.expr.steps) == 1

def test_pipeline_2():
    stmt = first("data |> xor(key) |> to_hex()\n")
    assert len(stmt.expr.steps) == 2

def test_pipeline_3():
    stmt = first("data |> xor(key)\n")
    assert isinstance(stmt.expr.steps[0], FuncCall)
    assert stmt.expr.steps[0].name == "xor"

def test_pipeline_4():
    stmt = first("data |> substitute(s1)\n")
    assert stmt.expr.steps[0].name == "substitute"

def test_pipeline_5():
    stmt = first("data |> pad(PKCS7)\n")
    assert stmt.expr.steps[0].name == "pad"

def test_pipeline_6():
    stmt = first("data |> permute(p1)\n")
    assert stmt.expr.steps[0].name == "permute"

def test_pipeline_7():
    with pytest.raises(ParseError):
        parse("data |> 42\n")

# ==================================================================
# SBOX & PBOX
# ==================================================================

def test_sbox_1():
    stmt = first("sbox a1 = [0x63, 0x7c]\n")
    assert isinstance(stmt, SboxDef)
    assert stmt.name == "a1"
    assert len(stmt.entries) == 2
    assert isinstance(stmt.entries[0], HexLit)

def test_sbox_2():
    stmt = first("sbox empty = []\n")
    assert stmt.entries == []

def test_pbox_1():
    stmt = first("pbox p1 = [1, 0, 3, 2]\n")
    assert isinstance(stmt, PboxDef)
    assert stmt.name == "p1"
    assert len(stmt.entries) == 4
    assert isinstance(stmt.entries[0], IntLit)

# ==================================================================
# FUNC DEF
# ==================================================================

def test_func_1():
    stmt = first("def f():\n    pass\n")
    assert isinstance(stmt, FuncDef)
    assert stmt.name == "f"
    assert stmt.params == []

def test_func_2():
    stmt = first("def f() -> Int:\n    pass\n")
    assert isinstance(stmt.return_type, SimpleType)
    assert stmt.return_type.name == "Int"

def test_func_3():
    stmt = first("def f(x: Int, y: Bytes):\n    pass\n")
    assert len(stmt.params) == 2
    assert stmt.params[0].name == "x"
    assert stmt.params[1].name == "y"

def test_func_4():
    stmt = first("def f(x: Int):\n    pass\n")
    assert isinstance(stmt.params[0].type, SimpleType)
    assert stmt.params[0].type.name == "Int"

def test_func_5():
    stmt = first("def f():\n    pass\n")
    assert isinstance(stmt.body[0], PassStmt)

def test_func_6():
    stmt = first("def f() -> Int:\n    return 42\n")
    assert isinstance(stmt.body[0], ReturnStmt)
    assert isinstance(stmt.body[0].value, IntLit)

def test_func_7():
    stmt = first("def f():\n    return\n")
    assert stmt.body[0].value is None

# ==================================================================
# CIPHER DEF
# ==================================================================

def test_cipher_1():
    stmt = first("cipher MyCipher(key: Bytes):\n    encrypt:\n        data |> xor(key)\n")
    assert isinstance(stmt, CipherDef)
    assert stmt.name == "MyCipher"
    assert len(stmt.params) == 1
    assert stmt.params[0].name == "key"
    assert isinstance(stmt.encrypt_block, EncryptBlock)
    assert isinstance(stmt.encrypt_block.pipeline, PipelineExpr)

def test_cipher_2():
    stmt = first("cipher MyCipher(key: Bytes) -> Bytes:\n    encrypt:\n        data |> xor(key)\n")
    assert isinstance(stmt.return_type, SimpleType)
    assert stmt.return_type.name == "Bytes"

# ==================================================================
# CONTROL
# ==================================================================

def test_if_1():
    src = "if x:\n    pass\n"
    stmt = first(src)
    assert isinstance(stmt, IfStmt)
    assert isinstance(stmt.condition, Ident)

def test_if_2():
    src = "if x:\n    pass\nelse:\n    pass\n"
    stmt = first(src)
    assert len(stmt.else_body) == 1

def test_if_3():
    src = "if x:\n    pass\nelif y:\n    pass\n"
    stmt = first(src)
    assert len(stmt.elif_clauses) == 1

def test_if_4():
    src = "if x:\n    pass\nelif y:\n    pass\nelse:\n    pass\n"
    stmt = first(src)
    assert len(stmt.elif_clauses) == 1
    assert len(stmt.else_body) == 1

def test_while_1():
    src = "while x:\n    pass\n"
    stmt = first(src)
    assert isinstance(stmt, WhileStmt)
    assert isinstance(stmt.condition, Ident)

def test_for_1():
    src = "for i in items:\n    pass\n"
    stmt = first(src)
    assert isinstance(stmt, ForStmt)
    assert stmt.var == "i"
    assert isinstance(stmt.iterable, Ident)

def test_break_1():
    src = "def f():\n    break\n"
    assert isinstance(first(src).body[0], BreakStmt)

def test_continue_1():
    src = "def f():\n    continue\n"
    assert isinstance(first(src).body[0], ContinueStmt)

def test_pass_1():
    src = "def f():\n    pass\n"
    assert isinstance(first(src).body[0], PassStmt)

def test_return_1():
    src = "def f():\n    return 42\n"
    ret = first(src).body[0]
    assert isinstance(ret, ReturnStmt)
    assert isinstance(ret.value, IntLit)

def test_return_2():
    src = "def f():\n    return\n"
    ret = first(src).body[0]
    assert ret.value is None

def test_repeat_1():
    src = "repeat(4):\n    pass\n"
    stmt = first(src)
    assert isinstance(stmt, RepeatStmt)
    assert isinstance(stmt.count, IntLit)
    assert stmt.count.value == 4

def test_with_1():
    src = "with open(f):\n    pass\n"
    stmt = first(src)
    assert isinstance(stmt, WithStmt)

def test_with_2():
    src = "with open(f) as h:\n    pass\n"
    stmt = first(src)
    assert stmt.as_name == "h"

def test_match_1():
    src = "match x:\n    case 1:\n        pass\n"
    stmt = first(src)
    assert isinstance(stmt, MatchStmt)
    assert len(stmt.cases) == 1
    assert isinstance(stmt.cases[0].pattern, IntLit)

# ==================================================================
# MISC
# ==================================================================

def test_misc_1():
    stmt = parse("x = 1\ny = 2\n")
    assert len(stmt.statements) == 2

def test_misc_2():
    stmt = first("def f():\n    if x:\n        return 1\n")
    assert isinstance(stmt.body[0], IfStmt)

def test_misc_3():
    stmt = parse("x = 1\n")
    assert isinstance(stmt, Program)

def test_misc_4():
    stmt = parse("")
    assert stmt.statements == []