from cryptoscript.ast_nodes import *


class TypeCheckError(Exception):
    def __init__(self, message: str, line: int = None, source_line: str = None):
        self.line = line
        if line and source_line:
            super().__init__(
                f"Type error on line {line}:\n"
                f"  {source_line}\n"
                f"  {message}"
            )
        elif line:
            super().__init__(f"Type error on line {line}: {message}")
        else:
            super().__init__(f"Type error: {message}")


# Check if both types are compatible
def types_compatible(declared, actual) -> bool:
    if declared is None or actual is None:
        return True
    if isinstance(declared, SimpleType) and isinstance(actual, SimpleType):
        if {declared.name, actual.name} <= {"Hex", "Int"}:
            return True
        return declared.name == actual.name
    if isinstance(declared, ModIntType) and isinstance(actual, SimpleType):
        if actual.name in ("Int", "Hex"):
            return True
    if isinstance(declared, SimpleType) and isinstance(actual, ModIntType):
        if declared.name in ("Int", "Hex"):
            return True

    if not isinstance(declared, type(actual)):
        return False
    if isinstance(declared, ModIntType):
        return declared.modulus == actual.modulus
    if isinstance(declared, MatrixType):
        return (declared.rows == actual.rows and
                declared.cols == actual.cols)
    return False


class TypeChecker:

    def __init__(self, source: str):
        self.env: dict = {}
        self.func_sigs: dict = {}
        self._current_func_return = None
        self._lines: list[str] = source.splitlines()

    def _err(self, message: str, line: int = None):
        src = ""
        if line and 0 < line <= len(self._lines):
            src = self._lines[line - 1]
        return TypeCheckError(message, line=line, source_line=src)

    # Input types required by each pipeline transform (None -> all types are valid)
    PIPELINE_INPUT_TYPES = {
        "xor":        SimpleType("Bytes"),
        "substitute": SimpleType("Bytes"),
        "permute":    SimpleType("Bytes"),
        "pad":        SimpleType("Bytes"),
        "unpad":      SimpleType("Bytes"),
        "rotl":       None,
        "rotr":       None,
        "to_hex":     None,
        "to_bytes":   None,
        "to_int":     None,
        "to_string":  None,
        "to_le_bytes": None,
        "to_be_bytes": None,
    }

    # Output types of each pipeline transform (None -> output type = input type)
    PIPELINE_OUTPUT_TYPES = {
        "xor":        SimpleType("Bytes"),
        "substitute": SimpleType("Bytes"),
        "permute":    SimpleType("Bytes"),
        "pad":        SimpleType("Bytes"),
        "unpad":      SimpleType("Bytes"),
        "rotl":       None,
        "rotr":       None,
        "to_hex":     SimpleType("Hex"),
        "to_bytes":   SimpleType("Bytes"),
        "to_int":     SimpleType("Int"),
        "to_string":  SimpleType("String"),
        "to_le_bytes": SimpleType("Bytes"),
        "to_be_bytes": SimpleType("Bytes"),
    }

    # Return types of known built-in calls
    BUILTIN_RETURN_TYPES = {
        "xor":         SimpleType("Bytes"),
        "substitute":  SimpleType("Bytes"),
        "permute":     SimpleType("Bytes"),
        "pad":         SimpleType("Bytes"),
        "unpad":       SimpleType("Bytes"),
        "rotl":        SimpleType("Int"),
        "rotr":        SimpleType("Int"),
        "to_hex":      SimpleType("Hex"),
        "to_bytes":    SimpleType("Bytes"),
        "to_int":      SimpleType("Int"),
        "to_string":   SimpleType("String"),
        "to_le_bytes": SimpleType("Bytes"),
        "to_be_bytes": SimpleType("Bytes"),
        "len":         SimpleType("Int"),
        "range":       None,
        "print":       None,
    }

    # Arithmetic operators
    NUMERIC_OPS = {'+', '-', '*', '/', '//', '%', '**', '<<', '>>', '&', '|', '^'}

    # Operators whose result is always Bool
    BOOL_RESULT_OPS = {'==', '!=', '<', '>', '<=', '>=', 'in', 'is', 'and', 'or'}

    def check(self, program: Program):
        for stmt in program.statements:
            self._check_stmt(stmt)

    # Statements

    def _check_stmt(self, node):
        if isinstance(node, VarDecl):
            self._check_var_decl(node)
        elif isinstance(node, AssignStmt):
            self._check_assign(node)
        elif isinstance(node, ExprStmt):
            self._check_expr_stmt(node)
        elif isinstance(node, ReturnStmt):
            self._check_return(node)
        elif isinstance(node, FuncDef):
            self._check_func_def(node)
        elif isinstance(node, CipherDef):
            self._check_cipher_def(node)
        elif isinstance(node, SboxDef):
            self._check_sbox_def(node)
        elif isinstance(node, PboxDef):
            self._check_pbox_def(node)
        elif isinstance(node, IfStmt):
            self._check_if(node)
        elif isinstance(node, WhileStmt):
            self._check_while(node)
        elif isinstance(node, ForStmt):
            self._check_for(node)
        elif isinstance(node, RepeatStmt):
            self._check_repeat_stmt(node)
        elif isinstance(node, MatchStmt):
            self._check_match(node)
        elif isinstance(node, WithStmt):
            self._check_with(node)

    def _check_stmt_list(self, stmts):
        for s in stmts:
            self._check_stmt(s)

    def _check_var_decl(self, node: VarDecl):
        if isinstance(node.type, ModIntType) and isinstance(node.type.modulus, str):
            modulus_name = node.type.modulus
            modulus_type = self.env.get(modulus_name)
            if modulus_type is None:
                raise self._err(f"ModInt modulus '{modulus_name}' is not defined. "
                                "Declare it as an Int before using it here.", line=node.line)
            if not types_compatible(SimpleType("Int"), modulus_type):
                raise self._err(f"ModInt modulus '{modulus_name}' must be an Int, "
                                f"got {self._fmt(modulus_type)}.", line=node.line)
        if node.value is not None:
            actual = self._infer(node.value)
            if actual is not None and not types_compatible(node.type, actual):
                raise self._err(f"Type mismatch in declaration of '{node.name}': declared "
                                f"{self._fmt(node.type)}, got {self._fmt(actual)}", node.line)
        self.env[node.name] = node.type

    def _check_assign(self, node: AssignStmt):
        actual = self._infer(node.value)
        if isinstance(node.target, Ident):
            name = node.target.name
            if name in self.env:
                declared = self.env[name]
                if actual is not None and not types_compatible(declared, actual):
                    raise self._err(f"Type mismatch in assignment to '{name}': expected "
                                    f"{self._fmt(declared)}, got "
                                    f"{self._fmt(actual)}", node.line)
            else:
                if actual is not None:
                    self.env[name] = actual
        elif isinstance(node.target, Subscript):
            self._infer(node.value)

    def _check_expr_stmt(self, node: ExprStmt):
        self._infer(node.expr)

    def _check_return(self, node: ReturnStmt):
        if node.value is None:
            return
        actual = self._infer(node.value)
        if (self._current_func_return is not None and
                actual is not None and
                not types_compatible(self._current_func_return, actual)):
            raise self._err(f"Return type mismatch: function declared to return "
                            f"{self._fmt(self._current_func_return)}, but returns "
                            f"{self._fmt(actual)}", node.line)

    def _check_func_def(self, node: FuncDef):
        saved_env = dict(self.env)
        saved_return_type = self._current_func_return

        for p in node.params:
            if p.type is None:
                raise self._err(f"Parameter '{p.name}' in function '{node.name}' "
                                f"must have a type annotation.", node.line)
            self.env[p.name] = p.type

        self._current_func_return = node.return_type
        self._check_stmt_list(node.body)

        self.func_sigs[node.name] = (
            [p.type for p in node.params],
            node.return_type
        )

        self.env = saved_env
        self._current_func_return = saved_return_type

    def _check_cipher_def(self, node: CipherDef):
        saved_env = dict(self.env)
        # 'data' is the implicit pipeline input — always Bytes
        self.env["data"] = SimpleType("Bytes")
        for p in node.params:
            if p.type is None:
                raise self._err(f"Cipher parameter '{p.name}' must have a "
                                f"type annotation", node.line)
            self.env[p.name] = p.type
        # Check the pipeline
        pipeline = node.encrypt_block.pipeline
        if isinstance(pipeline, PipelineExpr):
            self._check_pipeline(pipeline)
        self.func_sigs[node.name] = (
            [p.type for p in node.params],
            node.return_type,
        )

        self.env = saved_env

    def _check_sbox_def(self, node: SboxDef):
        for i, entry in enumerate(node.entries):
            t = self._infer(entry)
            if t is not None and not types_compatible(SimpleType("Int"), t):
                raise self._err(f"sbox '{node.name}' entry {i} must be an Int or "
                                f"Hex literal, got {self._fmt(t)}", node.line)

    def _check_pbox_def(self, node: PboxDef):
        for i, entry in enumerate(node.entries):
            t = self._infer(entry)
            if t is not None and not types_compatible(SimpleType("Int"), t):
                raise self._err(f"pbox '{node.name}' entry {i} must be an Int literal, "
                                f"got {self._fmt(t)}", node.line)
        # Pbox entries should be non-negative integers
        for i, entry in enumerate(node.entries):
            if isinstance(entry, UnaryOp) and entry.op == '-':
                raise self._err(f"pbox '{node.name}' entry {i} is negative. Pbox indices "
                                f"must be non-negative integers.", node.line)

    def _check_if(self, node: IfStmt):
        self._infer(node.condition)
        self._check_stmt_list(node.body)
        for cond, body in node.elif_clauses:
            self._infer(cond)
            self._check_stmt_list(body)
        self._check_stmt_list(node.else_body)

    def _check_while(self, node: WhileStmt):
        self._infer(node.condition)
        self._check_stmt_list(node.body)

    def _check_for(self, node: ForStmt):
        self.env[node.var] = SimpleType("Int")  # conservative — range gives ints
        self._check_stmt_list(node.body)

    def _check_repeat_stmt(self, node: RepeatStmt):
        count_type = self._infer(node.count)
        if count_type is not None and not types_compatible(SimpleType("Int"), count_type):
            raise self._err(f"repeat() count must be an Int, got {self._fmt(count_type)}",
                            node.line)
        self._check_stmt_list(node.body)

    def _check_match(self, node: MatchStmt):
        self._infer(node.subject)
        for clause in node.cases:
            self._check_stmt_list(clause.body)

    def _check_with(self, node: WithStmt):
        self._infer(node.expr)
        if node.as_name:
            self.env[node.as_name] = None  # type unknown
        self._check_stmt_list(node.body)

    # Pipeline

    def _check_pipeline(self, pipeline: PipelineExpr):
        current_type = self._infer(pipeline.base)
        for step in pipeline.steps:
            current_type = self._check_pipeline_step(step, current_type, pipeline)
        return current_type

    def _check_pipeline_step(self, step, input_type, pipeline):
        if isinstance(step, RepeatBlock):
            if isinstance(step.pipeline, PipelineExpr):
                self._check_pipeline(step.pipeline)
            return input_type   # repeat doesn't change the outer type

        if not isinstance(step, FuncCall):
            return input_type

        required = self.PIPELINE_INPUT_TYPES.get(step.name)
        if (required is not None and
                input_type is not None and
                not types_compatible(required, input_type)):
            raise self._err(f"Pipeline step '{step.name}' requires {self._fmt(required)}, "
                            f"but received {self._fmt(input_type)}", pipeline.line)

        out = self.PIPELINE_OUTPUT_TYPES.get(step.name)
        return out if out is not None else input_type

    # Type Inference

    def _infer(self, node) -> "type_node | None":
        if isinstance(node, IntLit):
            return SimpleType("Int")
        if isinstance(node, HexLit):
            return SimpleType("Hex")
        if isinstance(node, BytesLit):
            return SimpleType("Bytes")
        if isinstance(node, StringLit):
            return SimpleType("String")
        if isinstance(node, BoolLit):
            return SimpleType("Bool")
        if isinstance(node, NoneLit):
            return None
        if isinstance(node, ListLit):
            return None
        if isinstance(node, Ident):
            return self.env.get(node.name)
        if isinstance(node, BinOp):
            return self._infer_binop(node)
        if isinstance(node, UnaryOp):
            return self._infer_unaryop(node)
        if isinstance(node, FuncCall):
            return self._infer_funccall(node)
        if isinstance(node, PipelineExpr):
            return self._check_pipeline(node)
        if isinstance(node, Subscript):
            return self._infer_subscript(node)
        return None   # unknown — skip the check

    def _infer_binop(self, node: BinOp):
        left = self._infer(node.left)
        right = self._infer(node.right)
        if node.op in self.BOOL_RESULT_OPS:
            return SimpleType("Bool")
        if node.op in self.NUMERIC_OPS:
            if left is not None and right is not None:
                if isinstance(left, SimpleType) and left.name == "Bytes":
                    raise self._err(f"Cannot apply '{node.op}' to Bytes. Use xor() "
                                    f"for byte-level operations, or to_int() to convert to Int "
                                    f"first.", node.line)
                if isinstance(right, SimpleType) and right.name == "Bytes":
                    raise self._err(f"Cannot apply '{node.op}' to Bytes. Use xor() "
                                    f"for byte-level operations, or to_int() to convert to Int "
                                    f"first.", node.line)
                if node.op == "**":  # Exponentiation can have 2 different mod field integers
                    return left
                if isinstance(left, ModIntType) and isinstance(right, ModIntType):
                    if left.modulus != right.modulus:
                        raise self._err(f"Cannot mix ModInt[{left.modulus}] and "
                                        f"ModInt[{right.modulus}] in arithmetic. Both operands "
                                        f"must have the same modulus.", node.line)
                    return left
                if isinstance(left, ModIntType):
                    return left
                if isinstance(right, ModIntType):
                    return right
                if (isinstance(left, SimpleType) and left.name in ("Int", "Hex") and
                        isinstance(right, SimpleType) and right.name in ("Int", "Hex")):
                    return SimpleType("Int")

        return None

    def _infer_unaryop(self, node: UnaryOp):
        operand = self._infer(node.operand)
        if node.op == "not":
            return SimpleType("Bool")
        if node.op in ("-", "+", "~"):
            if isinstance(operand, SimpleType) and operand.name == "Bytes":
                raise self._err(f"Cannot apply unary '{node.op}' to Bytes. "
                                f"Convert to Int first with to_int().", node.line)
            return operand
        return None

    def _infer_funccall(self, node: FuncCall):
        if isinstance(node.name, str):
            name = node.name
        else:
            return None
        self._check_call_args(name, node.args, node)
        if name in self.func_sigs:
            _, return_type = self.func_sigs[name]
            return return_type
        if name in self.BUILTIN_RETURN_TYPES:
            return self.BUILTIN_RETURN_TYPES[name]

        return None

    def _check_call_args(self, name: str, args: list, node: FuncCall):
        if name not in self.func_sigs:
            return
        param_types, _ = self.func_sigs[name]

        if len(args) != len(param_types):
            raise self._err(f"'{name}' expects {len(param_types)} argument(s), "
                            f"got {len(args)}.", node.line)

        for i, (arg, expected) in enumerate(zip(args, param_types)):
            actual = self._infer(arg)
            if (expected is not None and
                    actual is not None and
                    not types_compatible(expected, actual)):
                raise self._err(f"Argument {i + 1} of '{name}': expected "
                                f"{self._fmt(expected)}, got {self._fmt(actual)}", node.line)

    def _infer_subscript(self, node: Subscript):
        obj_type = self._infer(node.obj)
        index_type = self._infer(node.index)
        if (index_type is not None and
                not types_compatible(SimpleType("Int"), index_type)):
            raise self._err(f"Subscript index must be an Int, got "
                            f"{self._fmt(index_type)}", node.line)
        if isinstance(obj_type, SimpleType) and obj_type.name == "Bytes":
            return SimpleType("Int")
        if isinstance(obj_type, MatrixType):
            return None
        return None

    # Formatting

    def _fmt(self, t) -> str:
        if t is None:
            return "unknown"
        if isinstance(t, SimpleType):
            return t.name
        if isinstance(t, ModIntType):
            return f"ModInt[{t.modulus}]"
        if isinstance(t, MatrixType):
            return f"Matrix[{t.rows}x{t.cols}]"
        return str(t)
