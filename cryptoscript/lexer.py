from cryptoscript.tokens import Token, TokenType, KEYWORDS

# ------------------------------------------------------------------
#  LEXER ERROR
# ------------------------------------------------------------------


class LexerError(Exception):
    def __init__(self, message: str, line: int, col: int = None, source_line: str = None):
        self.line = line
        self.col = col
        self.source_line = source_line
        # Display Message
        loc = f"Lexer error on line {line}"
        if source_line and col is not None:
            pointer = " " * col + "^"
            super().__init__(
                f"{loc}:\n  {source_line}\n  {pointer}\n  {message}"
            )
        else:
            super().__init__(f"{loc}: {message}")


# ------------------------------------------------------------------
#  LEXER
# ------------------------------------------------------------------
class Lexer:

    def __init__(self, input: str):
        self.input = input
        self.pos = 0
        self.line = 1
        self.tokens: list[Token] = []
        self.indent_stack: list[int] = [0]

    # --------------------------------------------------------------
    # Error Handling
    # --------------------------------------------------------------

    def _current_line_text(self):
        start = self.input.rfind("\n", 0, self.pos) + 1
        end = self.input.find("\n", self.pos)
        end = end if end != -1 else len(self.input)
        return self.input[start:end]

    def _current_col(self):
        start = self.input.rfind("\n", 0, self.pos) + 1
        return self.pos - start

    def _lex_error(self, message: str):
        return LexerError(message, self.line, self._current_col(), self._current_line_text())

    # --------------------------------------------------------------
    #  HELPERS
    # --------------------------------------------------------------

    def _current(self):
        if self.pos < len(self.input):
            return self.input[self.pos]
        return ""

    def _peek(self, off: int = 1):
        idx = self.pos + off
        if idx < len(self.input):
            return self.input[idx]
        return ""

    def _advance(self):
        if self.pos >= len(self.input):
            raise self._lex_error("Unexpected EOF")
        ch = self.input[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def _add_token(self, type: TokenType, value: str):
        self.tokens.append(Token(type, value, self.line))

    def _handle_indentation(self):
        # Find the indentation in this line
        level = 0
        while self._current() in (" ", "\t"):
            if self._current() == "\t":
                level += 4
            else:
                level += 1
            self.pos += 1

        # If this is an empty line then return
        if self._current() in ("\n", ""):
            return

        # Compare with current indentation level
        current_level = self.indent_stack[-1]
        if level > current_level:   # If greater than current level, then add an INDENT token
            self.indent_stack.append(level)
            self._add_token(TokenType.INDENT, "")
        # If smaller then check if there is a matching block and
        # add as many DEDENT tokens as pops from the stack
        elif level < current_level:
            while self.indent_stack[-1] > level:
                self.indent_stack.pop()
                self._add_token(TokenType.DEDENT, "")
            if self.indent_stack[-1] != level:
                raise self._lex_error("Indentation error. This line's indentation doesn't match"
                                      " any enclosing block. Check for mixed tabs and spaces.")

    def _scan_identifier_or_keyword(self):

        # Consume until I can and form a word
        start = self.pos
        while self._current().isalnum() or self._current() == "_":
            self.pos += 1
        word = self.input[start:self.pos]

        # Check if it is a Keyword
        token_type = KEYWORDS.get(word)
        if token_type is None:  # If it is not a Keyword then it is a Identifier
            token_type = TokenType.IDENT
        self._add_token(token_type, word)

    def _scan_number(self):
        HEX_DIGITS = set("0123456789abcdefABCDEF")
        start = self.pos
        if self._current() == "0" and self._peek() in ("x", "X"):  # Check if it is Hex
            self.pos += 2  # consume '0x'
            if self._current() not in HEX_DIGITS:
                raise self._lex_error("Invalid hex literal. Expected "
                                      "hex digits (0-9, a-f) after '0x'.")
            # Keep consuming till I can
            while self._current() in HEX_DIGITS:
                self.pos += 1

            if self._current().isalpha() or self._current() == "_":
                raise self._lex_error("Invalid hex literal. Expected "
                                      "hex digits (0-9, a-f) after '0x'.")
            self._add_token(TokenType.HEX_LIT, self.input[start:self.pos])
        else:  # If an integer
            while self._current().isdigit():
                self.pos += 1

            if self._current().isalpha() or self._current() == "_":
                raise self._lex_error("Invalid int literal. Expected "
                                      "int digits (0-9)")
            self._add_token(TokenType.INT_LIT, self.input[start:self.pos])

    def _scan_string(self):

        # Consume the 1st quote
        quote_used = self._advance()

        # Consume and form the string
        str = []
        while True:
            ch = self._current()
            if ch == "":
                raise self._lex_error("Invalid string. Expected a "
                                      f"closing quote : {quote_used} here")
            if ch == "\n":
                raise self._lex_error("Invalid string. Expected a "
                                      f"closing quote : {quote_used} here")
            if ch == quote_used:
                self._advance()
                break
            if ch == "\\":
                self._advance()
                esc = self._advance()
                escapes = {
                    "n": "\n", "t": "\t", "r": "\r",
                    "\\": "\\", "'": "'", '"': '"'
                }
                if esc not in escapes:
                    raise self._lex_error(f"Invalid string. "
                                          f"Unexpected escape sequence : \\{esc}")
                str.append(escapes[esc])
            else:
                str.append(self._advance())

        self._add_token(TokenType.STRING_LIT, "".join(str))

    def _scan_bytes(self):

        # Consume b & the 1st quote
        self._advance()
        quote_used = self._advance()

        bstr = []
        while True:
            ch = self._current()
            if ch == "":
                raise self._lex_error(f"Invalid bytestring. Expected "
                                      f"a closing quote : {quote_used} here")
            if ch == "\n":
                raise self._lex_error(f"Invalid bytestring. Expected "
                                      f"a closing quote : {quote_used} here")
            if ch == quote_used:
                self._advance()
                break
            if ch == "\\":
                self._advance()
                esc = self._current()
                if esc == "x":  # Hex Sequence
                    self._advance()
                    h1 = self._advance()
                    h2 = self._advance()
                    if h1 not in "0123456789abcdefABCDEF" or \
                       h2 not in "0123456789abcdefABCDEF":
                        raise self._lex_error("Invalid bytestring. Expected "
                                              "hex digits (0-9, a-f) after \'\\x\'.")
                    bstr.append(f"\\x{h1}{h2}")
                else:
                    escapes = {
                        "n": "\n", "t": "\t", "r": "\r",
                        "\\": "\\", "'": "'", '"': '"'
                    }
                    if esc not in escapes:
                        raise self._lex_error(f"Invalid bytestring. Unexpected "
                                              f"escape sequence : \\{esc}")
                    bstr.append(escapes[esc])
            else:
                bstr.append(self._advance())

        self._add_token(TokenType.BYTES_LIT, "".join(bstr))

    def _scan_operator_or_delimiter(self):
        ch = self._advance()
        if ch == "*" and self._current() == "*":  # ** & **=
            self._advance()
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.DOUBLESTAR_EQ, "**=")
            else:
                self._add_token(TokenType.DOUBLESTAR, "**")
        elif ch == "*" and self._current() == "=":  # *=
            self._advance()
            self._add_token(TokenType.STAR_EQ, "*=")
        elif ch == "*":  # *
            self._add_token(TokenType.STAR, "*")
        elif ch == "/" and self._current() == "/":  # // & //=
            self._advance()
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.DOUBLESLASH_EQ, "//=")
            else:
                self._add_token(TokenType.DOUBLESLASH, "//")
        elif ch == "/" and self._current() == "=":  # /=
            self._advance()
            self._add_token(TokenType.SLASH_EQ, "/=")
        elif ch == "/":  # /
            self._add_token(TokenType.SLASH, "/")
        elif ch == "+" and self._current() == "=":  # +=
            self._advance()
            self._add_token(TokenType.PLUS_EQ, "+=")
        elif ch == "+":  # +
            self._add_token(TokenType.PLUS, "+")
        elif ch == "-" and self._current() == ">":  # ->
            self._advance()
            self._add_token(TokenType.ARROW, "->")
        elif ch == "-" and self._current() == "=":  # -=
            self._advance()
            self._add_token(TokenType.MINUS_EQ, "-=")
        elif ch == "-":  # -
            self._add_token(TokenType.MINUS, "-")
        elif ch == "%" and self._current() == "=":  # %=
            self._advance()
            self._add_token(TokenType.PERCENT_EQ, "%=")
        elif ch == "%":  # %
            self._add_token(TokenType.PERCENT, "%")
        elif ch == ">" and self._current() == ">":  # >> & >>=
            self._advance()
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.RSHIFT_EQ, ">>=")
            else:
                self._add_token(TokenType.RSHIFT, ">>")
        elif ch == ">":  # >= & >
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.GTE, ">=")
            else:
                self._add_token(TokenType.GT, ">")
        elif ch == "<" and self._current() == "<":  # << & <<=
            self._advance()
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.LSHIFT_EQ, "<<=")
            else:
                self._add_token(TokenType.LSHIFT, "<<")
        elif ch == "<":  # <= & <
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.LTE, "<=")
            else:
                self._add_token(TokenType.LT, "<")
        elif ch == "|":  # |>, |= & |
            if self._current() == ">":
                self._advance()
                self._add_token(TokenType.PIPELINE, "|>")
            elif self._current() == "=":
                self._advance()
                self._add_token(TokenType.PIPE_EQ, "|=")
            else:
                self._add_token(TokenType.PIPE, "|")
        elif ch == "&" and self._current() == "=":  # &=
            self._advance()
            self._add_token(TokenType.AMP_EQ, "&=")
        elif ch == "&":  # &
            self._add_token(TokenType.AMP, "&")
        elif ch == "^" and self._current() == "=":  # ^=
            self._advance()
            self._add_token(TokenType.CARET_EQ, "^=")
        elif ch == "^":  # ^
            self._add_token(TokenType.CARET, "^")
        elif ch == "=":  # == & =
            if self._current() == "=":
                self._advance()
                self._add_token(TokenType.EQEQ, "==")
            else:
                self._add_token(TokenType.EQUALS, "=")
        elif ch == "!" and self._current() == "=":  # !=
            self._advance()
            self._add_token(TokenType.NEQ, "!=")
        elif ch == "~":  # ~
            self._add_token(TokenType.TILDE, "~")
        elif ch == "(":  # (
            self._add_token(TokenType.LPAREN, "(")
        elif ch == ")":  # )
            self._add_token(TokenType.RPAREN, ")")
        elif ch == "[":  # [
            self._add_token(TokenType.LBRACKET, "[")
        elif ch == "]":  # ]
            self._add_token(TokenType.RBRACKET, "]")
        elif ch == "{":  # {
            self._add_token(TokenType.LBRACE, "{")
        elif ch == "}":  # }
            self._add_token(TokenType.RBRACE, "}")
        elif ch == ",":  # ,
            self._add_token(TokenType.COMMA, ",")
        elif ch == ":":  # :
            self._add_token(TokenType.COLON, ":")
        elif ch == ".":  # .
            self._add_token(TokenType.DOT, ".")
        elif ch == ";":  # ;
            self._add_token(TokenType.SEMICOLON, ";")
        else:
            raise self._lex_error(f"Unexpected character '{ch}'." +
                                  ("Did you mean to use a string?"
                                   "Wrap it in quotes." if ch == "'" else ""))

    # --------------------------------------------------------------
    #  TOKENIZER
    # --------------------------------------------------------------

    def tokenize(self):

        while self._current() != "":

            # Add all indentations
            self._handle_indentation()

            # Add tokens
            while self._current() not in ("\n", ""):

                # Current character
                ch = self._current()

                # Tokenise the current character(word)
                if ch in (" ", "\t", "\r"):
                    self.pos += 1
                elif ch == "#":  # Comments
                    while self._current() not in ("\n", ""):
                        self.pos += 1
                elif ch == "b" and self._peek() in ('"', "'"):  # Byte Literals
                    self._scan_bytes()
                elif ch.isalpha() or ch == "_":  # Keywords and Identifiers
                    self._scan_identifier_or_keyword()
                elif ch.isdigit():  # Numeric Literals
                    self._scan_number()
                elif ch in ('"', "'"):  # String Literals
                    self._scan_string()
                else:
                    self._scan_operator_or_delimiter()

            # For new line
            if self._current() == "\n":
                self._add_token(TokenType.NEWLINE, "\n")
                self._advance()

        # Remove all indentations
        while self.indent_stack[-1] > 0:
            self.indent_stack.pop()
            self._add_token(TokenType.DEDENT, "")

        if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
            self._add_token(TokenType.NEWLINE, "\n")

        # Add End of File
        self._add_token(TokenType.EOF, "")

        return self.tokens
