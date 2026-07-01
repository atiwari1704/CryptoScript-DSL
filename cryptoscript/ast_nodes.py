# ══════════════════════════════════════════════════════════════════════
#  AST NODE
# ══════════════════════════════════════════════════════════════════════

class ASTNode:
    def accept(self, visitor):
        method = getattr(visitor, f"visit_{type(self).__name__}",
                         visitor.generic_visit)
        return method(self)


# ══════════════════════════════════════════════════════════════════════
#  TYPE ANNOTATIONS
# ══════════════════════════════════════════════════════════════════════

class SimpleType(ASTNode):
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"Simple Type ({self.name})"


class ModIntType(ASTNode):
    def __init__(self, modulus, line=None):
        self.modulus = modulus
        self.line = line

    def __repr__(self):
        return f"ModInt Type (modulus={self.modulus})"


class MatrixType(ASTNode):
    def __init__(self, elem_type, rows, cols, line=None):
        self.elem_type = elem_type
        self.rows = rows
        self.cols = cols
        self.line = line

    def __repr__(self):
        return f"Matrix Type ({self.elem_type}, {self.rows}x{self.cols})"

# ══════════════════════════════════════════════════════════════════════
#  LITERALS
# ══════════════════════════════════════════════════════════════════════


class IntLit(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Int Lit ({self.value})"


class HexLit(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Hex Lit ({self.value})"


class BytesLit(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Bytes Lit ({self.value!r})"


class StringLit(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"String Lit ({self.value!r})"


class BoolLit(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Bool Lit ({self.value})"


class NoneLit(ASTNode):
    def __init__(self, line=None):
        self.line = line

    def __repr__(self):
        return "None Lit ()"


class ListLit(ASTNode):
    def __init__(self, elements=None, line=None):
        self.elements = elements or []
        self.line = line

    def __repr__(self):
        return f"ListLit ({self.elements})"

# ══════════════════════════════════════════════════════════════════════
#  IDENTIFIERS & ACCESS
# ══════════════════════════════════════════════════════════════════════


class Ident(ASTNode):
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"Ident ({self.name})"


class Attribute(ASTNode):
    def __init__(self, obj, attr, line=None):
        self.obj = obj
        self.attr = attr
        self.line = line

    def __repr__(self):
        return f"Attribute ({self.obj}.{self.attr})"


class Subscript(ASTNode):
    def __init__(self, obj, index, line=None):
        self.obj = obj
        self.index = index
        self.line = line

    def __repr__(self):
        return f"Subscript ({self.obj}[{self.index}])"

# ══════════════════════════════════════════════════════════════════════
#  EXPRESSIONS
# ══════════════════════════════════════════════════════════════════════


class BinOp(ASTNode):
    def __init__(self, left, op, right, line=None):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def __repr__(self):
        return f"Bin Op ({self.left} {self.op} {self.right})"


class UnaryOp(ASTNode):
    def __init__(self, op, operand, line=None):
        self.op = op
        self.operand = operand
        self.line = line

    def __repr__(self):
        return f"Unary Op ({self.op} {self.operand})"


class FuncCall(ASTNode):
    def __init__(self, name, args=None, line=None):
        self.name = name
        self.line = line
        self.args = args or []

    def __repr__(self):
        return f"FuncCall ({self.name}, args={self.args})"


class PipelineExpr(ASTNode):
    def __init__(self, base, steps=None, line=None):
        self.base = base
        self.line = line
        self.steps = steps or []

    def __repr__(self):
        return f"Pipeline Expr ({self.base} |> {self.steps})"

# ══════════════════════════════════════════════════════════════════════
#  STATEMENTS
# ══════════════════════════════════════════════════════════════════════


class ExprStmt(ASTNode):
    def __init__(self, expr, line=None):
        self.expr = expr
        self.line = line

    def __repr__(self):
        return f"Expr Stmt ({self.expr})"


class VarDecl(ASTNode):
    def __init__(self, name, type, value=None, line=None):
        self.name = name
        self.type = type
        self.line = line
        self.value = value

    def __repr__(self):
        return f"Var Decl ({self.name}: {self.type} = {self.value})"


class AssignStmt(ASTNode):
    def __init__(self, target, op, value, line=None):
        self.target = target
        self.op = op
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Assign Stmt ({self.target} {self.op} {self.value})"


class ReturnStmt(ASTNode):
    def __init__(self, value=None, line=None):
        self.line = line
        self.value = value

    def __repr__(self):
        return f"Return Stmt ({self.value})"


class BreakStmt(ASTNode):
    def __repr__(self):
        return "Break Stmt ()"


class ContinueStmt(ASTNode):
    def __repr__(self):
        return "Continue Stmt ()"


class PassStmt(ASTNode):
    def __repr__(self):
        return "Pass Stmt ()"

# ══════════════════════════════════════════════════════════════════════
#  IMPORT
# ══════════════════════════════════════════════════════════════════════


class ImportStmt(ASTNode):
    def __init__(self, module, names=None, line=None):
        self.line = line
        self.module = module
        self.names = names or []

    def __repr__(self):
        if self.names:
            return f"Import Stmt (from {self.module} import {self.names})"
        return f"Import Stmt (import {self.module})"

# ══════════════════════════════════════════════════════════════════════
#  FUNCTION DEFINITION
# ══════════════════════════════════════════════════════════════════════


class Param(ASTNode):
    def __init__(self, name, type, default_val=None, line=None):
        self.name = name
        self.type = type
        self.line = line
        self.default_val = default_val

    def __repr__(self):
        return f"Param ({self.name}: {self.type} = {self.default_val})"


class FuncDef(ASTNode):
    def __init__(self, name, params, return_type, body=None, line=None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.line = line
        self.body = body or []

    def __repr__(self):
        return (f"Func Def ({self.name}, params={self.params},"
                f"returns={self.return_type})")

# ══════════════════════════════════════════════════════════════════════
#  SBOX / PBOX
# ══════════════════════════════════════════════════════════════════════


class SboxDef(ASTNode):
    def __init__(self, name, entries=None, line=None):
        self.name = name
        self.line = line
        self.entries = entries or []

    def __repr__(self):
        return f"Sbox Def ({self.name}, {len(self.entries)} entries)"


class PboxDef(ASTNode):
    def __init__(self, name, entries=None, line=None):
        self.name = name
        self.line = line
        self.entries = entries or []

    def __repr__(self):
        return f"Pbox Def ({self.name}, {len(self.entries)} entries)"

# ══════════════════════════════════════════════════════════════════════
#  CIPHER DEFINITION
# ══════════════════════════════════════════════════════════════════════


class EncryptBlock(ASTNode):
    def __init__(self, pipeline, line=None):
        self.pipeline = pipeline
        self.line = line

    def __repr__(self):
        return f"Encrypt Block({self.pipeline})"


class CipherDef(ASTNode):
    def __init__(self, name, params, return_type, encrypt_block, line=None):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.encrypt_block = encrypt_block
        self.line = line

    def __repr__(self):
        return (f"Cipher Def ({self.name}, params={self.params},"
                f"returns={self.return_type})")

# ══════════════════════════════════════════════════════════════════════
#  REPEAT
# ══════════════════════════════════════════════════════════════════════


class RepeatStmt(ASTNode):
    def __init__(self, count, body=None, line=None):
        self.count = count
        self.line = line
        self.body = body or []

    def __repr__(self):
        return f"Repeat Stmt (count={self.count})"


class RepeatBlock(ASTNode):
    def __init__(self, count, pipeline, line=None):
        self.count = count
        self.pipeline = pipeline
        self.line = line

    def __repr__(self):
        return f"Repeat Block (count={self.count}, pipeline={self.pipeline})"


# ══════════════════════════════════════════════════════════════════════
#  CONTROL FLOW
# ══════════════════════════════════════════════════════════════════════

class IfStmt(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None, line=None):
        self.condition = condition
        self.body = body
        self.line = line
        self.elif_clauses = elif_clauses or []
        self.else_body = else_body or []

    def __repr__(self):
        return f"If Stmt (condition={self.condition})"


class WhileStmt(ASTNode):
    def __init__(self, condition, body=None, line=None):
        self.condition = condition
        self.line = line
        self.body = body or []

    def __repr__(self):
        return f"While Stmt (condition={self.condition})"


class ForStmt(ASTNode):
    def __init__(self, var, iterable, body=None, line=None):
        self.var = var
        self.iterable = iterable
        self.line = line
        self.body = body or []

    def __repr__(self):
        return f"For Stmt ({self.var} in {self.iterable})"


class CaseClause(ASTNode):
    def __init__(self, pattern, body=None, line=None):
        self.pattern = pattern
        self.line = line
        self.body = body or []

    def __repr__(self):
        return f"Case Clause (pattern={self.pattern})"


class MatchStmt(ASTNode):
    def __init__(self, subject, cases=None, line=None):
        self.subject = subject
        self.line = line
        self.cases = cases or []

    def __repr__(self):
        return f"Match Stmt (subject={self.subject})"


class WithStmt(ASTNode):
    def __init__(self, expr, as_name=None, body=None, line=None):
        self.expr = expr
        self.line = line
        self.as_name = as_name
        self.body = body or []

    def __repr__(self):
        return f"With Stmt ({self.expr} as {self.as_name})"

# ══════════════════════════════════════════════════════════════════════
#  PROGRAM
# ══════════════════════════════════════════════════════════════════════


class Program(ASTNode):
    def __init__(self, statements=None):
        self.statements = statements or []

    def __repr__(self):
        return f"Program ({len(self.statements)} statements)"

# ══════════════════════════════════════════════════════════════════════
#  VISITOR BASE CLASS
# ══════════════════════════════════════════════════════════════════════


class ASTVisitor:
    def visit(self, node):
        return node.accept(self)

    def generic_visit(self, node):
        raise NotImplementedError(f"{type(self).__name__}"
                                  f" has no visitor for '{type(node).__name__}'")
