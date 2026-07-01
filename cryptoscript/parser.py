from cryptoscript.tokens import Token, TokenType
from cryptoscript.ast_nodes import *


#  Parser error
class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int = None, source_line: str = None):
        self.line = line
        loc = f"Parse error on line {line}"
        if source_line and col is not None:
            if source_line.strip():
                pointer = " " * col + "^" * max(1, len(source_line.split()[0]))
            else:
                pointer = " " * col + "^"
            super().__init__(f"{loc}:\n  {source_line}\n  {pointer}\n  {message}")
        else:
            super().__init__(f"{loc}: {message}")


#  Parser
class Parser:
    def __init__(self, tokens: list[Token], source: str = ""):
        self.tokens = tokens
        self.pos = 0
        self.source = source
        self._lines = source.splitlines()

    # ══════════════════════════════════════════════════════════════
    # Error Handling
    # ══════════════════════════════════════════════════════════════

    def _line_text(self, line: int) -> str:
        if 0 < line <= len(self._lines):
            return self._lines[line - 1]
        return ""

    def _parse_error(self, message: str, off: int = 0):
        tok = self._peek(off)
        line = tok.line
        src = self._line_text(line)
        col = src.index(tok.value) if tok.value and tok.value in src else 0
        return ParseError(message, line=line, col=col, source_line=src)

    # ══════════════════════════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════════════════════════

    def _peek(self, offset: int = 0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _check(self, *types: TokenType):
        return self._peek().type in types

    def _match(self, *types: TokenType):
        if self._check(*types):
            self._advance()
            return True
        return False

    def _expect(self, type_: TokenType):
        tok = self._peek()
        if tok.type == type_:
            return self._advance()

        msg = {
            TokenType.NEWLINE: (
                "Expected a new line here. "
            ),
            TokenType.COLON: (
                "Expected ':' here. "
            ),
            TokenType.INDENT: (
                "Expected an indented block here. "
                "The body of this block must be indented by 4 spaces."
            ),
            TokenType.DEDENT: (
                "Expected the block to end here. "
                "Check that your indentation is consistent."
            ),
            TokenType.RPAREN: (
                "Expected a closing ')'. "
                "Check that all your parentheses are matched."
            ),
            TokenType.RBRACKET: (
                "Expected a closing ']'. "
                "Check that all your brackets are matched."
            ),
            TokenType.IDENT: self._ident_msg(self._peek(-1)),
        }

        base = msg.get(type_, f"Expected {type_.name}, got '{tok.value}'.")
        raise self._parse_error(base, -1 * (type_ == TokenType.IDENT))

    def _ident_msg(self, tok: Token):
        keywords = ["cipher", "encrypt", "sbox", "pbox", "repeat",
                    "if", "for", "while", "def", "return"]
        if tok.value in keywords:
            return (f"'{tok.value}' is a reserved keyword and cannot"
                    "be used as a variable name. Try renaming it.")
        return f"Expected an identifier, got '{tok.value}' ({tok.type.name})."

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    def _expect_attr_name(self) -> str:
        tok = self._peek()
        if tok.value.isidentifier():
            return self._advance().value
        raise self._parse_error(f"Expected an attribute, got '{tok.value}' ({tok.type.name}).")

    #  All token types that can start a pipeline step
    PIPELINE_STEP_TOKENS = {
        TokenType.SUBSTITUTE,
        TokenType.PERMUTE,
        TokenType.XOR,
        TokenType.ROTL,
        TokenType.ROTR,
        TokenType.PAD,
        TokenType.UNPAD,
        TokenType.TO_BYTES,
        TokenType.TO_LE_BYTES,
        TokenType.TO_BE_BYTES,
        TokenType.TO_HEX,
        TokenType.TO_STRING,
        TokenType.TO_INT,
        TokenType.IDENT,
        TokenType.REPEAT,
    }

    # ══════════════════════════════════════════════════════════════
    # PARSER
    # ══════════════════════════════════════════════════════════════

    def parse(self):
        self._skip_newlines()
        statements = []
        while not self._check(TokenType.EOF):
            statements.append(self._parse_statement())
            self._skip_newlines()
        return Program(statements=statements)

    # ══════════════════════════════════════════════════════════════
    # BLOCK
    # ══════════════════════════════════════════════════════════════

    def _parse_block(self):
        self._expect(TokenType.INDENT)
        self._skip_newlines()
        stmts = []
        while not self._check(TokenType.DEDENT, TokenType.EOF):
            stmts.append(self._parse_statement())
            self._skip_newlines()
        self._expect(TokenType.DEDENT)
        return stmts

    # ══════════════════════════════════════════════════════════════
    # STATEMENTS
    # ══════════════════════════════════════════════════════════════

    def _parse_statement(self):
        t = self._peek().type

        if t == TokenType.IMPORT:
            return self._parse_import()
        elif t == TokenType.FROM:
            return self._parse_from_import()
        elif t == TokenType.DEF:
            return self._parse_func_def()
        elif t == TokenType.CIPHER:
            return self._parse_cipher_def()
        elif t == TokenType.SBOX:
            return self._parse_sbox_def()
        elif t == TokenType.PBOX:
            return self._parse_pbox_def()
        elif t == TokenType.IF:
            return self._parse_if()
        elif t == TokenType.WHILE:
            return self._parse_while()
        elif t == TokenType.FOR:
            return self._parse_for()
        elif t == TokenType.MATCH:
            return self._parse_match()
        elif t == TokenType.WITH:
            return self._parse_with()
        elif t == TokenType.RETURN:
            return self._parse_return()
        elif t == TokenType.REPEAT:
            return self._parse_repeat_stmt()
        elif t == TokenType.BREAK:
            self._advance()
            self._match(TokenType.NEWLINE)
            return BreakStmt()
        elif t == TokenType.CONTINUE:
            self._advance()
            self._match(TokenType.NEWLINE)
            return ContinueStmt()
        elif t == TokenType.PASS:
            self._advance()
            self._match(TokenType.NEWLINE)
            return PassStmt()
        else:
            return self._parse_assign_or_expr()

    # ══════════════════════════════════════════════════════════════
    # IMPORT
    # ══════════════════════════════════════════════════════════════

    def _parse_import(self):
        tok = self._advance()
        module = self._parse_module_path()
        self._expect(TokenType.NEWLINE)
        return ImportStmt(module=module, names=[], line=tok.line)

    def _parse_from_import(self):
        tok = self._advance()
        module = self._parse_module_path()
        self._expect(TokenType.IMPORT)
        names = [self._expect(TokenType.IDENT).value]
        while self._match(TokenType.COMMA):
            names.append(self._expect(TokenType.IDENT).value)
        self._expect(TokenType.NEWLINE)
        return ImportStmt(module=module, names=names, line=tok.line)

    def _parse_module_path(self):
        parts = [self._expect(TokenType.IDENT).value]
        while self._check(TokenType.DOT):
            self._advance()
            parts.append(self._expect(TokenType.IDENT).value)
        return ".".join(parts)

    # ══════════════════════════════════════════════════════════════
    # TYPE ANNOTATIONS
    # ══════════════════════════════════════════════════════════════

    def _parse_type(self):
        tok = self._peek()

        # ModInt[n]
        if tok.type == TokenType.MODINT:
            self._advance()
            self._expect(TokenType.LBRACKET)
            tok = self._peek()
            if tok.type == TokenType.INT_LIT:
                modulus = int(self._advance().value)
            elif tok.type == TokenType.IDENT:
                modulus = self._advance().value
            else:
                raise ParseError("Expected integer or variable name inside ModInt[...], "
                                 f"got '{tok.value}'", tok.line)
            self._expect(TokenType.RBRACKET)
            return ModIntType(modulus=modulus)

        # Matrix[elem_type, rows, cols]
        if tok.type == TokenType.MATRIX:
            self._advance()
            self._expect(TokenType.LBRACKET)
            elem = self._parse_type()
            self._expect(TokenType.COMMA)
            rows = int(self._expect(TokenType.INT_LIT).value)
            self._expect(TokenType.COMMA)
            cols = int(self._expect(TokenType.INT_LIT).value)
            self._expect(TokenType.RBRACKET)
            return MatrixType(elem_type=elem, rows=rows, cols=cols, line=tok.line)

        # Simple types
        simple = {
            TokenType.INT: "Int",
            TokenType.BOOL: "Bool",
            TokenType.STRING: "String",
            TokenType.BYTES: "Bytes",
            TokenType.HEX: "Hex",
        }
        if tok.type in simple:
            self._advance()
            return SimpleType(name=simple[tok.type], line=tok.line)

        raise self._parse_error(f"Expected an type declaration, got '{tok.value}' "
                                f"({tok.type.name}).")

    # ══════════════════════════════════════════════════════════════
    # VARIABLE DECLARATION AND ASSIGNMENT
    # ══════════════════════════════════════════════════════════════

    def _parse_assign_or_expr(self):
        # VarDecl: IDENT : type
        if (self._check(TokenType.IDENT) and
                self._peek(1).type == TokenType.COLON):
            return self._parse_var_decl()

        # Otherwise parse expression first
        expr = self._parse_expr()

        # Check for assignment operator after the expression
        assign_ops = {
            TokenType.EQUALS: "=",
            TokenType.PLUS_EQ: "+=",
            TokenType.MINUS_EQ: "-=",
            TokenType.STAR_EQ: "*=",
            TokenType.SLASH_EQ: "/=",
            TokenType.DOUBLESLASH_EQ: "//=",
            TokenType.PERCENT_EQ: "%=",
            TokenType.DOUBLESTAR_EQ: "**=",
            TokenType.AMP_EQ: "&=",
            TokenType.PIPE_EQ: "|=",
            TokenType.CARET_EQ: "^=",
            TokenType.LSHIFT_EQ: "<<=",
            TokenType.RSHIFT_EQ: ">>=",
        }
        if self._peek().type in assign_ops:
            op = assign_ops[self._advance().type]
            val = self._parse_expr()
            self._expect(TokenType.NEWLINE)
            return AssignStmt(target=expr, op=op, value=val, line=val.line)

        self._expect(TokenType.NEWLINE)
        return ExprStmt(expr=expr, line=expr.line)

    def _parse_var_decl(self):
        name = self._advance().value      # IDENT
        self._expect(TokenType.COLON)
        type_node = self._parse_type()
        value = None
        if self._match(TokenType.EQUALS):
            value = self._parse_expr()
        self._expect(TokenType.NEWLINE)
        return VarDecl(name=name, type=type_node, value=value, line=type_node.line)

    # ══════════════════════════════════════════════════════════════
    # FUNCTION
    # ══════════════════════════════════════════════════════════════

    def _parse_param(self):
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.COLON)
        type_node = self._parse_type()
        default = None
        if self._match(TokenType.EQUALS):
            default = self._parse_expr()
        return Param(name=name, type=type_node, default_val=default, line=type_node.line)

    def _parse_param_list(self):
        params = []
        if self._check(TokenType.RPAREN):
            return params
        params.append(self._parse_param())
        while self._match(TokenType.COMMA):
            if self._check(TokenType.RPAREN):
                break
            params.append(self._parse_param())
        return params

    def _parse_func_def(self):
        tok = self._advance()  # consume 'def'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.LPAREN)
        params = self._parse_param_list()
        self._expect(TokenType.RPAREN)
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()
        return FuncDef(name=name, params=params, return_type=return_type,
                       body=body, line=tok.line)

    # ══════════════════════════════════════════════════════════════
    # SBOX AND PBOX
    # ══════════════════════════════════════════════════════════════

    def _parse_box_entries(self):
        self._expect(TokenType.LBRACKET)
        entries = []
        if not self._check(TokenType.RBRACKET):
            entries.append(self._parse_expr())
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RBRACKET):
                    break
                entries.append(self._parse_expr())
        self._expect(TokenType.RBRACKET)
        return entries

    def _parse_sbox_def(self):
        tok = self._advance()  # consume 'sbox'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.EQUALS)
        entries = self._parse_box_entries()
        self._expect(TokenType.NEWLINE)
        return SboxDef(name=name, entries=entries, line=tok.line)

    def _parse_pbox_def(self):
        tok = self._advance()  # consume 'pbox'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.EQUALS)
        entries = self._parse_box_entries()
        self._expect(TokenType.NEWLINE)
        return PboxDef(name=name, entries=entries, line=tok.line)

    # ══════════════════════════════════════════════════════════════
    # CIPHER
    # ══════════════════════════════════════════════════════════════

    def _parse_cipher_def(self):
        tok = self._advance()  # consume 'cipher'
        name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.LPAREN)
        params = self._parse_param_list()
        self._expect(TokenType.RPAREN)
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)

        # Body of cipher must contain the encrypt block
        self._expect(TokenType.INDENT)
        self._skip_newlines()
        encrypt = self._parse_encrypt_block()
        self._skip_newlines()
        self._expect(TokenType.DEDENT)

        return CipherDef(name=name, params=params, return_type=return_type,
                         encrypt_block=encrypt, line=tok.line)

    def _parse_encrypt_block(self):
        self._expect(TokenType.ENCRYPT)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        self._skip_newlines()
        pipeline = self._parse_pipeline()
        self._skip_newlines()
        self._expect(TokenType.DEDENT)
        return EncryptBlock(pipeline=pipeline, line=pipeline.line)

    # ══════════════════════════════════════════════════════════════
    # REPEAT
    # ══════════════════════════════════════════════════════════════

    def _parse_repeat_stmt(self):
        self._advance()  # consume 'repeat'
        self._expect(TokenType.LPAREN)
        count = self._parse_expr()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()
        return RepeatStmt(count=count, body=body, line=count.line)

    def _parse_repeat_block(self):
        self._advance()  # consume 'repeat'
        self._expect(TokenType.LPAREN)
        count = self._parse_expr()
        self._expect(TokenType.RPAREN)
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        self._skip_newlines()
        pipeline = self._parse_pipeline()
        self._skip_newlines()
        self._expect(TokenType.DEDENT)
        return RepeatBlock(count=count, pipeline=pipeline, line=count.line)

    # ══════════════════════════════════════════════════════════════
    # CONTROL FLOW
    # ══════════════════════════════════════════════════════════════

    def _parse_if(self):
        tok = self._advance()  # consume 'if'
        condition = self._parse_expr()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()

        elif_clauses = []
        else_body = []

        self._skip_newlines()
        while self._check(TokenType.ELIF):
            self._advance()
            elif_cond = self._parse_expr()
            self._expect(TokenType.COLON)
            self._expect(TokenType.NEWLINE)
            elif_body = self._parse_block()
            elif_clauses.append((elif_cond, elif_body))
            self._skip_newlines()

        if self._check(TokenType.ELSE):
            self._advance()
            self._expect(TokenType.COLON)
            self._expect(TokenType.NEWLINE)
            else_body = self._parse_block()

        return IfStmt(condition=condition, body=body, elif_clauses=elif_clauses,
                      else_body=else_body, line=tok.line)

    def _parse_while(self):
        tok = self._advance()
        condition = self._parse_expr()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()
        return WhileStmt(condition=condition, body=body, line=tok.line)

    def _parse_for(self):
        tok = self._advance()
        var = self._expect(TokenType.IDENT).value
        self._expect(TokenType.IN)
        iterable = self._parse_expr()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()
        return ForStmt(var=var, iterable=iterable, body=body, line=tok.line)

    def _parse_match(self):
        tok = self._advance()  # consume 'match'
        subject = self._parse_expr()
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        self._expect(TokenType.INDENT)
        self._skip_newlines()
        cases = []
        while self._check(TokenType.CASE):
            self._advance()
            pattern = self._parse_primary()
            self._expect(TokenType.COLON)
            self._expect(TokenType.NEWLINE)
            body = self._parse_block()
            cases.append(CaseClause(pattern=pattern, body=body, line=pattern.line))
            self._skip_newlines()
        self._expect(TokenType.DEDENT)
        return MatchStmt(subject=subject, cases=cases, line=tok.line)

    def _parse_with(self):
        tok = self._advance()
        expr = self._parse_expr()
        as_name = None
        if self._match(TokenType.AS):
            as_name = self._expect(TokenType.IDENT).value
        self._expect(TokenType.COLON)
        self._expect(TokenType.NEWLINE)
        body = self._parse_block()
        return WithStmt(expr=expr, as_name=as_name, body=body, line=tok.line)

    def _parse_return(self):
        tok = self._advance()
        if self._check(TokenType.NEWLINE):
            self._advance()
            return ReturnStmt(value=None, line=tok.line)
        value = self._parse_expr()
        self._expect(TokenType.NEWLINE)
        return ReturnStmt(value=value, line=tok.line)

    def _parse_expr(self):
        return self._parse_pipeline()

    #  |> pipeline
    def _parse_pipeline(self):
        base = self._parse_or()
        if not self._check(TokenType.PIPELINE):
            return base
        steps = []
        while self._check(TokenType.PIPELINE):
            self._advance()  # consume |>
            if self._check(TokenType.REPEAT):
                steps.append(self._parse_repeat_block())
            else:
                steps.append(self._parse_pipeline_step())
        return PipelineExpr(base=base, steps=steps, line=base.line)

    def _parse_pipeline_step(self):
        tok = self._peek()

        valid = {
            TokenType.SUBSTITUTE,
            TokenType.PERMUTE,
            TokenType.XOR,
            TokenType.ROTL,
            TokenType.ROTR,
            TokenType.PAD,
            TokenType.UNPAD,
            TokenType.TO_BYTES,
            TokenType.TO_LE_BYTES,
            TokenType.TO_BE_BYTES,
            TokenType.TO_HEX,
            TokenType.TO_STRING,
            TokenType.TO_INT,
            TokenType.IDENT,
        }
        if tok.type not in valid:
            raise self._parse_error(f"Invalid Transform or Function Name, "
                                    f"got '{tok.value}' ({tok.type.name}).")
        name = self._advance().value
        self._expect(TokenType.LPAREN)
        args = self._parse_arg_list()
        self._expect(TokenType.RPAREN)
        return FuncCall(name=name, args=args, line=tok.line)

    #  or
    def _parse_or(self):
        left = self._parse_and()
        while self._check(TokenType.OR):
            op = self._advance().value
            left = BinOp(left=left, op=op, right=self._parse_and(), line=left.line)
        return left

    #  and
    def _parse_and(self):
        left = self._parse_not()
        while self._check(TokenType.AND):
            op = self._advance().value
            left = BinOp(left=left, op=op, right=self._parse_not(), line=left.line)
        return left

    #  not
    def _parse_not(self):
        if self._check(TokenType.NOT):
            op = self._advance()
            return UnaryOp(op=op.value, operand=self._parse_not(), line=op.line)
        return self._parse_comparison()

    # comparison
    def _parse_comparison(self):
        left = self._parse_bitwise_or()
        comp = {
            TokenType.EQEQ: "==",
            TokenType.NEQ: "!=",
            TokenType.LT: "<",
            TokenType.GT: ">",
            TokenType.LTE: "<=",
            TokenType.GTE: ">=",
            TokenType.IN: "in",
            TokenType.IS: "is",
        }
        while self._peek().type in comp:
            op = comp[self._advance().type]
            left = BinOp(left=left, op=op, right=self._parse_bitwise_or(), line=left.line)
        return left

    #  bitwise or ( | )
    def _parse_bitwise_or(self):
        left = self._parse_bitwise_xor()
        while self._check(TokenType.PIPE):
            self._advance()
            left = BinOp(left=left, op="|", right=self._parse_bitwise_xor(), line=left.line)
        return left

    #  bitwise xor  ( ^ )
    def _parse_bitwise_xor(self):
        left = self._parse_bitwise_and()
        while self._check(TokenType.CARET):
            self._advance()
            left = BinOp(left=left, op="^", right=self._parse_bitwise_and(), line=left.line)
        return left

    #  bitwise and ( & )
    def _parse_bitwise_and(self):
        left = self._parse_shift()
        while self._check(TokenType.AMP):
            self._advance()
            left = BinOp(left=left, op="&", right=self._parse_shift(), line=left.line)
        return left

    #  shift  (  << ,  >> )
    def _parse_shift(self):
        left = self._parse_arith()
        while self._check(TokenType.LSHIFT, TokenType.RSHIFT):
            op = self._advance().value
            left = BinOp(left=left, op=op, right=self._parse_arith(), line=left.line)
        return left

    #  addition / subtraction
    def _parse_arith(self):
        left = self._parse_term()
        while self._check(TokenType.PLUS, TokenType.MINUS):
            op = self._advance().value
            left = BinOp(left=left, op=op, right=self._parse_term(), line=left.line)
        return left

    #  multiplication / division
    def _parse_term(self):
        left = self._parse_factor()
        while self._check(TokenType.STAR, TokenType.SLASH,
                          TokenType.DOUBLESLASH, TokenType.PERCENT):
            op = self._advance().value
            left = BinOp(left=left, op=op, right=self._parse_factor(), line=left.line)
        return left

    #  exponentiation  ** (right-associative)
    def _parse_factor(self):
        base = self._parse_unary()
        if self._check(TokenType.DOUBLESTAR):
            op = self._advance()
            exp = self._parse_factor()   # right-associative
            return BinOp(left=base, op=op.value, right=exp, line=op.line)
        return base

    #  unary ( -x   ~x   +x )
    def _parse_unary(self):
        if self._check(TokenType.MINUS,
                       TokenType.TILDE,
                       TokenType.PLUS):
            op = self._advance()
            return UnaryOp(op=op.value, operand=self._parse_unary(), line=op.line)
        return self._parse_primary()

    #  primary  atom + trailers (.attr  [idx]  (args))
    def _parse_primary(self):
        node = self._parse_atom()

        while self._check(TokenType.DOT, TokenType.LBRACKET, TokenType.LPAREN):
            if self._check(TokenType.DOT):
                self._advance()
                attr = self._expect_attr_name()
                node = Attribute(obj=node, attr=attr, line=node.line)
            elif self._check(TokenType.LBRACKET):
                self._advance()
                index = self._parse_expr()
                self._expect(TokenType.RBRACKET)
                node = Subscript(obj=node, index=index, line=node.line)
            elif self._check(TokenType.LPAREN):
                self._advance()
                args = self._parse_arg_list()
                self._expect(TokenType.RPAREN)
                if isinstance(node, Ident):
                    node = FuncCall(name=node.name, args=args, line=node.line)
                elif isinstance(node, Attribute):
                    node = FuncCall(name=node, args=args, line=node.line)
                else:
                    raise self._parse_error("Invalid Function Call")
        return node

    #  atoms
    def _parse_atom(self):
        tok = self._peek()

        # Int
        if tok.type == TokenType.INT_LIT:
            self._advance()
            return IntLit(value=int(tok.value), line=tok.line)

        # Hex
        if tok.type == TokenType.HEX_LIT:
            self._advance()
            return HexLit(value=tok.value, line=tok.line)

        # Bytes
        if tok.type == TokenType.BYTES_LIT:
            self._advance()
            return BytesLit(value=tok.value, line=tok.line)

        # String
        if tok.type == TokenType.STRING_LIT:
            self._advance()
            return StringLit(value=tok.value, line=tok.line)

        # Bool
        if tok.type == TokenType.TRUE:
            self._advance()
            return BoolLit(value=True, line=tok.line)
        if tok.type == TokenType.FALSE:
            self._advance()
            return BoolLit(value=False, line=tok.line)
        if tok.type == TokenType.BOOL_LIT:
            self._advance()
            return BoolLit(value=(tok.value == "True"), line=tok.line)

        # None
        if tok.type == TokenType.NONE:
            self._advance()
            return NoneLit(line=tok.line)

        # Padding scheme
        if tok.type in (TokenType.PKCS7, TokenType.ZERO):
            self._advance()
            return Ident(name=tok.value, line=tok.line)

        # Identifier
        if tok.type == TokenType.IDENT:
            self._advance()
            return Ident(name=tok.value, line=tok.line)

        # Primitive / conversion names used as standalone identifiers
        primitive_tokens = {
            TokenType.SUBSTITUTE, TokenType.PERMUTE,
            TokenType.XOR,        TokenType.ROTL,
            TokenType.ROTR,       TokenType.PAD,
            TokenType.UNPAD,      TokenType.TO_BYTES,
            TokenType.TO_LE_BYTES, TokenType.TO_BE_BYTES,
            TokenType.TO_HEX,     TokenType.TO_STRING,
            TokenType.TO_INT,
        }
        if tok.type in primitive_tokens:
            self._advance()
            return Ident(name=tok.value, line=tok.line)

        # Parenthesised expression
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expr()
            self._expect(TokenType.RPAREN)
            return expr

        # List
        if tok.type == TokenType.LBRACKET:
            return self._parse_list_lit()

        raise self._parse_error(f"Unexpected token, got '{tok.value}' ({tok.type.name}).")

    def _parse_list_lit(self):
        self._expect(TokenType.LBRACKET)
        elements = []
        if not self._check(TokenType.RBRACKET):
            elements.append(self._parse_expr())
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RBRACKET):
                    break
                elements.append(self._parse_expr())
        self._expect(TokenType.RBRACKET)
        return ListLit(elements=elements)

    def _parse_arg_list(self):
        args = []
        if self._check(TokenType.RPAREN):
            return args
        args.append(self._parse_expr())
        while self._match(TokenType.COMMA):
            if self._check(TokenType.RPAREN):
                break
            args.append(self._parse_expr())
        return args
