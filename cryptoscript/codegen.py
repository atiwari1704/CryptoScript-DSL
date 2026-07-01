from cryptoscript.ast_nodes import *

_PADDING_SCHEMES = frozenset({"PKCS7", "ZERO"})

_PREAMBLE = '''\
# ================================================
#  CryptoScript — generated Python file
# ================================================
# ── Runtime library ────


def _cs_invert_sbox(sbox: list) -> list:
    size = max(max(sbox) + 1, len(sbox))
    inv = list(range(size))
    for i, v in enumerate(sbox):
        inv[v] = i
    return inv


def _cs_invert_pbox(pbox: list) -> list:
    inv = [0] * len(pbox)
    for i, v in enumerate(pbox):
        inv[v] = i
    return inv


def substitute(data: bytes, sbox: list) -> bytes:
    return bytes(sbox[b] if b < len(sbox) else b for b in data)


def permute(data: bytes, pbox: list) -> bytes:
    return bytes(data[i] for i in pbox)


def xor(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("xor: key must be non-empty")
    key_rep = (key * ((len(data) // len(key)) + 1))[: len(data)]
    return bytes(a ^ b for a, b in zip(data, key_rep))


def rotl(value, n: int, bits: int = 32):
    n %= bits
    mask = (1 << bits) - 1
    if isinstance(value, bytes):
        val_int = int.from_bytes(value, "big")
        res_int = ((val_int << n) | (val_int >> (bits - n))) & mask
        return res_int.to_bytes(max(1, len(value)), "big")
    return ((value << n) | (value >> (bits - n))) & mask


def rotr(value, n: int, bits: int = 32):
    n %= bits
    mask = (1 << bits) - 1
    if isinstance(value, bytes):
        val_int = int.from_bytes(value, "big")
        res_int = ((val_int >> n) | (val_int << (bits - n))) & mask
        return res_int.to_bytes(max(1, len(value)), "big")
    return ((value >> n) | (value << (bits - n))) & mask


def pad(data: bytes, scheme: str, block_size: int = 16) -> bytes:
    if scheme == "PKCS7":
        p = block_size - (len(data) % block_size)
        return data + bytes([p] * p)
    if scheme == "ZERO":
        p = (-len(data)) % block_size
        return data + bytes(p)
    raise ValueError(f"pad: unknown scheme {scheme!r}")


def unpad(data: bytes, scheme: str) -> bytes:
    if scheme == "PKCS7":
        if not data:
            raise ValueError("unpad: empty data")
        p = data[-1]
        return data[:-p]
    if scheme == "ZERO":
        return data.rstrip(b"\\x00")
    raise ValueError(f"unpad: unknown scheme {scheme!r}")


def to_bytes(value, length=None, byteorder="big") -> bytes:
    if isinstance(value, ModInt):
        value = value.value
    if isinstance(value, bytes):
        return value
    if isinstance(value, int):
        n = length or max(1, (value.bit_length() + 7) // 8)
        return value.to_bytes(n, byteorder=byteorder)
    if isinstance(value, str):
        if value.startswith("0x") or value.startswith("0X"):
            return bytes.fromhex(value[2:])
        return value.encode("utf-8")
    raise TypeError(f"to_bytes: unsupported type {type(value).__name__}")


def to_le_bytes(value, length=None) -> bytes:
    if isinstance(value, ModInt):
        value = value.value
    return to_bytes(value, length=length, byteorder="little")


def to_be_bytes(value, length=None) -> bytes:
    if isinstance(value, ModInt):
        value = value.value
    return to_bytes(value, length=length, byteorder="big")


def to_hex(value) -> str:
    if isinstance(value, ModInt):
        return hex(value.value)
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if isinstance(value, str):
        return "0x" + value.encode("utf-8").hex()
    raise TypeError(f"to_hex: unsupported type {type(value).__name__}")


def to_string(value) -> str:
    if isinstance(value, ModInt):
        return hex(value.value)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, int):
        return hex(value)
    return str(value)


def to_int(value) -> int:
    if isinstance(value, ModInt):
        return value.value
    if isinstance(value, int):
        return value
    if isinstance(value, bytes):
        return int.from_bytes(value, byteorder="big")
    if isinstance(value, str):
        return int(value, 0)
    raise TypeError(f"to_int: unsupported type {type(value).__name__}")


class ModInt:

    __slots__ = ("value", "modulus")

    def __init__(self, value: int, modulus: int):
        self.modulus = modulus
        self.value   = int(value) % modulus

    def _v(self, other):
        return other.value if isinstance(other, ModInt) else int(other)

    def __add__(self, other):  return ModInt(self.value + self._v(other), self.modulus)
    def __radd__(self, other): return self.__add__(other)
    def __sub__(self, other):  return ModInt(self.value - self._v(other), self.modulus)
    def __rsub__(self, other): return ModInt(self._v(other) - self.value, self.modulus)
    def __mul__(self, other):  return ModInt(self.value * self._v(other), self.modulus)
    def __rmul__(self, other): return self.__mul__(other)
    def __pow__(self, exp, mod=None):
        return ModInt(pow(self.value, self._v(exp), self.modulus), self.modulus)
    def __eq__(self, other):   return self.value == self._v(other)
    def __int__(self):         return self.value
    def __repr__(self):        return f"ModInt({self.value}, mod={self.modulus})"


class Matrix:

    def __init__(self, rows: int, cols: int, data=None):
        self.rows = rows
        self.cols = cols
        self.data = data if data is not None else [[0] * cols for _ in range(rows)]

    def __getitem__(self, idx):        return self.data[idx]
    def __setitem__(self, idx, value): self.data[idx] = value

    def __add__(self, other):
        assert isinstance(other, Matrix) and self.rows == other.rows and self.cols == other.cols
        return Matrix(self.rows, self.cols,
                      [[self.data[r][c] + other.data[r][c]
                        for c in range(self.cols)] for r in range(self.rows)])

    def __mul__(self, other):
        if isinstance(other, Matrix):
            assert self.cols == other.rows
            return Matrix(self.rows, other.cols,
                          [[sum(self.data[r][k] * other.data[k][c]
                               for k in range(self.cols))
                            for c in range(other.cols)]
                           for r in range(self.rows)])
        return Matrix(self.rows, self.cols,
                      [[self.data[r][c] * other for c in range(self.cols)]
                       for r in range(self.rows)])

    def __repr__(self):
        return f"Matrix({self.rows}x{self.cols}, {self.data})"


# ── End of runtime ──────────
'''


class CodeGenError(Exception):
    def __init__(self, message: str):
        super().__init__(f"CodeGen Error : {message}")


class CodeGen:
    INDENT = "    "

    def __init__(self):
        self._lines: list[str] = []
        self._depth: int = 0
        self._cipher_params: list[str] = []

    def generate(self, tree: Program) -> str:
        """Return the complete Python source string for *tree*."""
        self._lines = [_PREAMBLE]
        self._depth = 0
        self._cipher_params = []
        for stmt in tree.statements:
            self._emit_stmt(stmt)
        return "\n".join(self._lines)

    # Helpers

    def _pad(self) -> str:
        return self.INDENT * self._depth

    def _write(self, line: str = ""):
        self._lines.append(self._pad() + line)

    def _blank(self):
        self._lines.append("")

    #  Statement dispatcher

    def _emit_stmt(self, node: ASTNode):
        name = type(node).__name__
        handler = getattr(self, f"_stmt_{name}", None)
        if handler is None:
            raise CodeGenError(
                f"No code generator for statement node '{name}'. "
                "This AST node type is not supported."
            )
        handler(node)

    #  Expression dispatcher

    def _gen(self, node: ASTNode) -> str:
        name = type(node).__name__
        handler = getattr(self, f"_expr_{name}", None)
        if handler is None:
            raise CodeGenError(
                f"No code generator for expression node '{name}'. "
                "This AST node type is not supported."
            )
        return handler(node)

    #  Expression Generator

    def _expr_IntLit(self, n: IntLit) -> str:
        return str(n.value)

    def _expr_HexLit(self, n: HexLit) -> str:
        return n.value

    def _expr_BytesLit(self, n: BytesLit) -> str:
        raw: list[int] = []
        val = n.value
        i = 0
        while i < len(val):
            ch = val[i]
            if ch == "\\" and i + 1 < len(val) and val[i + 1] == "x":
                hex_str = val[i + 2: i + 4]
                raw.append(int(hex_str, 16))
                i += 4
            else:
                raw.append(ord(ch) & 0xFF)
                i += 1
        return repr(bytes(raw))

    def _expr_StringLit(self, n: StringLit) -> str:
        return repr(n.value)

    def _expr_BoolLit(self, n: BoolLit) -> str:
        return "True" if n.value else "False"

    def _expr_NoneLit(self, _: NoneLit) -> str:
        return "None"

    def _expr_ListLit(self, n: ListLit) -> str:
        return "[" + ", ".join(self._gen(e) for e in n.elements) + "]"

    def _expr_Ident(self, n: Ident) -> str:
        if n.name in _PADDING_SCHEMES:
            return f'"{n.name}"'
        if n.name in self._cipher_params:
            return f"self.{n.name}"
        return n.name

    def _expr_Attribute(self, n: Attribute) -> str:
        return f"{self._gen(n.obj)}.{n.attr}"

    def _expr_Subscript(self, n: Subscript) -> str:
        return f"{self._gen(n.obj)}[{self._gen(n.index)}]"

    def _expr_BinOp(self, n: BinOp) -> str:
        return f"({self._gen(n.left)} {n.op} {self._gen(n.right)})"

    def _expr_UnaryOp(self, n: UnaryOp) -> str:
        expr = self._gen(n.operand)
        if n.op == "not":
            return f"(not {expr})"
        return f"({n.op}{expr})"

    def _expr_FuncCall(self, n: FuncCall) -> str:
        args = ", ".join(self._gen(a) for a in n.args)
        if isinstance(n.name, str):
            return f"{n.name}({args})"
        else:
            return f"{self._gen(n.name)}({args})"

    def _expr_PipelineExpr(self, n: PipelineExpr) -> str:
        current = self._gen(n.base)
        for step in n.steps:
            if isinstance(step, FuncCall):
                args = ", ".join(self._gen(a) for a in step.args)
                sep = ", " if args else ""
                current = f"{step.name}({current}{sep}{args})"
            elif isinstance(step, RepeatBlock):
                raise CodeGenError(
                    "repeat(...) block cannot appear in an inline pipeline "
                    "expression.  It is only valid inside a cipher encrypt block."
                )
            else:
                raise CodeGenError(
                    f"Invalid pipeline step type '{type(step).__name__}' "
                    "in inline pipeline expression."
                )
        return current

    #  Type Annotation Helper

    _SIMPLE_TYPES: dict[str, str] = {
        "Int":    "int",
        "Bool":   "bool",
        "String": "str",
        "Bytes":  "bytes",
        "Hex":    "int",
    }

    _SIMPLE_DEFAULTS: dict[str, str] = {
        "Int":    "0",
        "Bool":   "False",
        "String": '""',
        "Bytes":  "b''",
        "Hex":    "0",
    }

    def _type_hint(self, t) -> str:
        if t is None:
            return ""
        if isinstance(t, SimpleType):
            return self._SIMPLE_TYPES.get(t.name, "")
        if isinstance(t, ModIntType):
            return "ModInt"
        if isinstance(t, MatrixType):
            return "Matrix"
        return ""

    def _default_value(self, t) -> str:
        if isinstance(t, SimpleType):
            return self._SIMPLE_DEFAULTS.get(t.name, "None")
        if isinstance(t, ModIntType):
            return f"ModInt(0, {t.modulus})"
        if isinstance(t, MatrixType):
            return f"Matrix({t.rows}, {t.cols})"
        return "None"

    def _fmt_param(self, p: Param) -> str:
        hint = self._type_hint(p.type)
        s = f"{p.name}: {hint}" if hint else p.name
        if p.default_val is not None:
            s += f" = {self._gen(p.default_val)}"
        return s

    #  Statement Generator

    # Imports

    def _stmt_ImportStmt(self, n: ImportStmt):
        if n.names:
            self._write(f"from {n.module} import {', '.join(n.names)}")
        else:
            self._write(f"import {n.module}")

    # Simple Statements

    def _stmt_PassStmt(self, _):     self._write("pass")
    def _stmt_BreakStmt(self, _):    self._write("break")
    def _stmt_ContinueStmt(self, _): self._write("continue")

    def _stmt_ExprStmt(self, n: ExprStmt):
        self._write(self._gen(n.expr))

    def _stmt_VarDecl(self, n: VarDecl):
        rhs = self._gen(n.value) if n.value is not None else self._default_value(n.type)
        if n.value is not None and isinstance(n.type, ModIntType):
            rhs = f"ModInt({rhs}, {n.type.modulus})"
        if isinstance(n, ModIntType):
            return f"ModInt(0, {n.modulus})"
        if isinstance(n, ModIntType):
            return "ModInt"
        hint = self._type_hint(n.type)
        if hint:
            self._write(f"{n.name}: {hint} = {rhs}")
        else:
            self._write(f"{n.name} = {rhs}")

    def _stmt_AssignStmt(self, n: AssignStmt):
        self._write(f"{self._gen(n.target)} {n.op} {self._gen(n.value)}")

    def _stmt_ReturnStmt(self, n: ReturnStmt):
        if n.value is None:
            self._write("return")
        else:
            self._write(f"return {self._gen(n.value)}")

    # Control Flow

    def _stmt_IfStmt(self, n: IfStmt):
        self._write(f"if {self._gen(n.condition)}:")
        self._emit_block(n.body)
        for cond, body in n.elif_clauses:
            self._write(f"elif {self._gen(cond)}:")
            self._emit_block(body)
        if n.else_body:
            self._write("else:")
            self._emit_block(n.else_body)

    def _stmt_WhileStmt(self, n: WhileStmt):
        self._write(f"while {self._gen(n.condition)}:")
        self._emit_block(n.body)

    def _stmt_ForStmt(self, n: ForStmt):
        self._write(f"for {n.var} in {self._gen(n.iterable)}:")
        self._emit_block(n.body)

    def _stmt_MatchStmt(self, n: MatchStmt):
        subject = self._gen(n.subject)
        for i, clause in enumerate(n.cases):
            pattern = self._gen(clause.pattern)
            if i == 0:
                if pattern == "_":
                    self._write("if True:")
                else:
                    self._write(f"if {subject} == {pattern}:")
            else:
                if pattern == "_":
                    self._write("elif True:")
                else:
                    self._write(f"elif {subject} == {pattern}:")
            self._emit_block(clause.body)

    def _stmt_WithStmt(self, n: WithStmt):
        as_ = f" as {n.as_name}" if n.as_name else ""
        self._write(f"with {self._gen(n.expr)}{as_}:")
        self._emit_block(n.body)

    def _stmt_RepeatStmt(self, n: RepeatStmt):
        """repeat(N): block  →  for _i in range(N): <block>"""
        self._write(f"for _i in range({self._gen(n.count)}):")
        self._emit_block(n.body)

    # SBox/PBox

    def _stmt_SboxDef(self, n: SboxDef):
        entries = ", ".join(self._gen(e) for e in n.entries)
        self._write(f"{n.name} = [{entries}]")

    def _stmt_PboxDef(self, n: PboxDef):
        entries = ", ".join(self._gen(e) for e in n.entries)
        self._write(f"{n.name} = [{entries}]")

    # Function Definition

    def _stmt_FuncDef(self, n: FuncDef):
        params = ", ".join(self._fmt_param(p) for p in n.params)
        ret_hint = self._type_hint(n.return_type)
        ret = f" -> {ret_hint}" if ret_hint else ""
        self._write(f"def {n.name}({params}){ret}:")
        if n.body:
            self._emit_block(n.body)
        else:
            self._depth += 1
            self._write("pass")
            self._depth -= 1
        self._blank()

    #  Cipher Definition

    def _stmt_CipherDef(self, n: CipherDef):
        """
        Generate a Python class with three methods:
            class <n>:
                def __init__(self[, params]): ...  # store params as attributes
                def encrypt(self, data):      ...  # from DSL encrypt pipeline
                def decrypt(self, data):      ...  # auto-inverted pipeline
        """
        self._cipher_params = [p.name for p in n.params]

        self._write(f"class {n.name}:")
        self._depth += 1

        # __init__
        if n.params:
            params_str = ", ".join(self._fmt_param(p) for p in n.params)
            self._write(f"def __init__(self, {params_str}):")
        else:
            self._write("def __init__(self):")
        self._depth += 1
        if n.params:
            for p in n.params:
                self._write(f"self.{p.name} = {p.name}")
        else:
            self._write("pass")
        self._depth -= 1
        self._blank()

        # Encrypt
        pipeline = n.encrypt_block.pipeline
        self._write("def encrypt(self, data):")
        self._depth += 1
        self._emit_pipeline_stmts(pipeline, result_var="_result", seed="data")
        self._write("return _result")
        self._depth -= 1
        self._blank()

        # Decrypt
        self._write("def decrypt(self, data):")
        self._depth += 1
        try:
            inv_steps = self._invert_steps(pipeline.steps)
            inv_pipeline = PipelineExpr(base=pipeline.base, steps=inv_steps)
            self._emit_pipeline_stmts(inv_pipeline, result_var="_result", seed="data")
            self._write("return _result")
        except CodeGenError as exc:
            # Non-invertible step — emit a body that raises at runtime.
            self._write(f"raise NotImplementedError({repr(str(exc))})")
        self._depth -= 1

        self._depth -= 1
        self._blank()
        self._cipher_params = []

    #  Pipeline statement

    def _emit_pipeline_stmts(self, pipeline: PipelineExpr, result_var: str, seed: str):
        """
        Lower a PipelineExpr into a sequence of assignment statements:

            _result = <seed>
            _result = step1(_result, ...)
            for _round in range(N):      # RepeatBlock
                _result = sub(_result, ...)
            _result = step3(_result, ...)
        """
        self._write(f"{result_var} = {seed}")
        for step in pipeline.steps:
            self._emit_pipeline_step(step, result_var)

    def _emit_pipeline_step(self, step: ASTNode, result_var: str):
        """Emit one pipeline step that updates *result_var* in-place."""
        if isinstance(step, FuncCall):
            args = ", ".join(self._gen(a) for a in step.args)
            sep = ", " if args else ""
            self._write(f"{result_var} = {step.name}({result_var}{sep}{args})")
        elif isinstance(step, RepeatBlock):
            count = self._gen(step.count)
            self._write(f"for _round in range({count}):")
            self._depth += 1
            if isinstance(step.pipeline, PipelineExpr):
                self._emit_pipeline_step(step.pipeline.base, result_var)
                for sub in step.pipeline.steps:
                    self._emit_pipeline_step(sub, result_var)
            else:
                self._emit_pipeline_step(step.pipeline, result_var)
            self._depth -= 1
        else:
            raise CodeGenError(
                f"Invalid pipeline step type '{type(step).__name__}'. "
                "Expected FuncCall or RepeatBlock."
            )

    #  Automatic decrypt: pipeline inversion

    def _invert_steps(self, steps: list) -> list:
        return [self._invert_step(s) for s in reversed(steps)]

    def _invert_step(self, step: ASTNode) -> ASTNode:
        if isinstance(step, FuncCall):
            return self._invert_func_call(step)
        if isinstance(step, RepeatBlock):
            if isinstance(step.pipeline, PipelineExpr):
                all_steps = [step.pipeline.base] + step.pipeline.steps
                inv_all_steps = self._invert_steps(all_steps)
                inv_pipeline = PipelineExpr(base=inv_all_steps[0], steps=inv_all_steps[1:])
            else:
                inv_pipeline = self._invert_step(step.pipeline)
            return RepeatBlock(count=step.count, pipeline=inv_pipeline)
        raise CodeGenError(
            f"Cannot invert pipeline step of type '{type(step).__name__}'."
        )

    def _invert_func_call(self, fc: FuncCall) -> FuncCall:
        name, args = fc.name, fc.args
        if name == "xor":
            return FuncCall(name="xor", args=args)
        if name == "substitute":
            inv_arg = FuncCall(name="_cs_invert_sbox", args=args)
            return FuncCall(name="substitute", args=[inv_arg])
        if name == "permute":
            inv_arg = FuncCall(name="_cs_invert_pbox", args=args)
            return FuncCall(name="permute", args=[inv_arg])
        if name == "rotl":
            return FuncCall(name="rotr", args=args)
        if name == "rotr":
            return FuncCall(name="rotl", args=args)
        if name == "pad":
            return FuncCall(name="unpad", args=args)
        if name == "unpad":
            return FuncCall(name="pad", args=args)
        if name in ("to_bytes", "to_le_bytes", "to_be_bytes",
                    "to_hex", "to_string", "to_int"):
            raise CodeGenError(
                f"Type conversion '{name}' has no automatic inverse. "
                "Define decrypt() manually if needed."
            )
        raise CodeGenError(
            f"User-defined function '{name}' has no automatic inverse. "
            "Define decrypt() manually if needed."
        )

    #  Utility

    def _emit_block(self, stmts: list):
        """Emit an indented block; emits 'pass' if the list is empty."""
        self._depth += 1
        if not stmts:
            self._write("pass")
        else:
            for s in stmts:
                self._emit_stmt(s)
        self._depth -= 1
