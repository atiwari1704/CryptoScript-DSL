import sys
import os
import traceback

from cryptoscript.lexer import Lexer, LexerError
from cryptoscript.parser import Parser, ParseError
from cryptoscript.codegen import CodeGen, CodeGenError
from cryptoscript.type_checker import TypeChecker, TypeCheckError


USAGE = """Usage: cs <command> <file.crypto>

Commands:
  compile   Compile a .crypto file to a .py file
  run       Compile and run a .crypto file
"""


def _handle_runtime_error(e: Exception, cs_path: str):
    tb = traceback.extract_tb(e.__traceback__)
    frames = [frame.name for frame in tb]

    error_type = type(e).__name__
    error_msg = str(e)
    msg = _identify_error(e, error_type, error_msg, frames)

    # ── Print the error ───────────────────────────────────────────

    print(f"\nRuntime error in '{cs_path}':", file=sys.stderr)
    print(f"  {error_type}: {error_msg}", file=sys.stderr)
    if msg:
        print(f"\n  Hint: {msg}", file=sys.stderr)
    sys.exit(1)


def _identify_error(e, error_type, error_msg, frames):

    if "xor" in frames:
        if isinstance(e, ValueError) and "non-empty" in error_msg:
            return ("The key passed to xor() is empty (b\"\"). xor() requires a non-empty key.")
        if isinstance(e, TypeError):
            return ("xor() requires both arguments to be Bytes. Check that your key "
                    "and data are not Int or Hex values. Use to_bytes() to convert if needed.")
    if "substitute" in frames:
        if isinstance(e, IndexError):
            return ("substitute() tried to look up a byte value that exceeds the length of "
                    "your sbox. Your sbox should cover all possible values that the data can "
                    "contain (0-255 for arbitrary bytes).")
        if isinstance(e, TypeError):
            return ("substitute() requires Bytes as input, but received a non-Bytes value.")
    if "permute" in frames:
        if isinstance(e, IndexError):
            return ("permute() tried to access an index in your pbox that is larger than the "
                    "data length. Make sure every index in the pbox is within the range "
                    "0..len(data)-1.")
        if isinstance(e, TypeError):
            return ("permute() requires Bytes as input, but received a non-Bytes value.")
    if "_cs_invert_sbox" in frames and isinstance(e, IndexError):
        return ("decrypt() failed to invert your sbox. For automatic decryption to work, every "
                "value must be unique.")
    if "pad" in frames:
        if isinstance(e, ZeroDivisionError):
            return ("pad() was called with a block size of 0. The block size must be a "
                    "positive integer (default is 16).")
        if isinstance(e, TypeError):
            return ("pad() requires Bytes as input, but received a non-Bytes value.")
    if "unpad" in frames:
        if isinstance(e, ValueError) and "empty" in error_msg:
            return ("unpad() was called on empty data. Make sure you are decrypting non-empty "
                    "ciphertext.")
        if isinstance(e, ValueError):
            return ("unpad() found invalid padding. The ciphertext may be corrupted or was "
                    "not padded with this scheme.")
        if isinstance(e, TypeError):
            return ("unpad() requires Bytes as input, but received a non-Bytes value.")
    if "rotl" in frames:
        if isinstance(e, ZeroDivisionError):
            return ("rotl() was called with bits=0. The bit width must be a positive integer.")
    if "rotr" in frames:
        if isinstance(e, ZeroDivisionError):
            return ("rotr() was called with bits=0. The bit width must be a positive integer.")
    if "to_int" in frames and isinstance(e, ValueError):
        return ("to_int() could not convert the value to an integer. to_int() accepts Bytes, "
                "a hex string like '0x1F', or a decimal string like '42'. Other strings are "
                "not supported.")
    if "to_string" in frames and isinstance(e, UnicodeDecodeError):
        return ("to_string() could not decode the bytes as UTF-8. Your data contains non-UTF-8 "
                "bytes.")
    if "to_bytes" in frames:
        if isinstance(e, OverflowError):
            return ("to_bytes() failed because the integer value is too large to fit in the "
                    "requested number of bytes. ")
        if isinstance(e, ValueError):
            return ("to_bytes() was called with a negative length. The length must be a "
                    "positive integer.")
    if "__init__" in frames and isinstance(e, ZeroDivisionError):
        return ("ModInt was declared with a modulus of 0. The modulus must be a positive "
                "integer.")
    if "__mul__" in frames and isinstance(e, AssertionError):
        return ("Matrix multiplication failed due to incompatible dimensions. For A * B, the "
                "number of columns in A must equal the number of rows in B.")
    if "__add__" in frames and isinstance(e, AssertionError):
        return ("Matrix addition failed because the two matrices have different dimensions. "
                "Both matrices must have the same number of rows and columns.")
    if "__getitem__" in frames and isinstance(e, IndexError):
        return ("Matrix index is out of bounds.")
    if "decrypt" in frames and isinstance(e, NotImplementedError):
        return ("This cipher's decrypt() could not be auto-generated because the encrypt "
                "pipeline contains a step with no automatic inverse ({error_msg.split"
                "('CodeGen Error :')[-1].strip()}).")
    if isinstance(e, NameError):
        missing = error_msg.split("'")[1] if "'" in error_msg else ""
        return (f"'{missing}' is used but never declared. Make sure it is defined before "
                "this line.")
    if isinstance(e, ZeroDivisionError):
        return "Division by zero. Check your divisor is not 0."
    if isinstance(e, RecursionError):
        return ("Maximum recursion depth exceeded. Check that your recursive function has a "
                "proper base case.")
    if isinstance(e, MemoryError):
        return ("Ran out of memory.")
    if isinstance(e, OverflowError):
        return ("A number became too large to represent. Consider using ModInt to keep values "
                "bounded.")
    if isinstance(e, AttributeError):
        return (f"{error_msg}. You are calling a method or accessing a field that does not "
                "exist on this value. Check the type of the variable.")
    if isinstance(e, ModuleNotFoundError):
        module = error_msg.replace("No module named ", "").strip("'")
        return (f"Module '{module}' could not be found. Make sure it is installed in your "
                "virtual environment.")
    return None


def compile_source(source: str) -> str:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens, source).parse()
    TypeChecker(source).check(ast)
    return CodeGen().generate(ast)


# Compile .crypto file to .py file
def cmd_compile(cs_path: str):
    py_path = os.path.splitext(cs_path)[0] + ".py"
    with open(cs_path, "r") as f:
        source = f.read()
    generated = compile_source(source)
    with open(py_path, "w") as f:
        f.write(generated)
    print(f"Compiled:  {cs_path}")
    print(f"Output:    {py_path}")


# Run the file without generating the .py file
def cmd_run(cs_path: str):
    with open(cs_path, "r") as f:
        source = f.read()
    generated = compile_source(source)
    namespace = {"__file__": cs_path}
    try:
        exec(generated, namespace)
    except Exception as e:
        _handle_runtime_error(e, cs_path)


def main():
    args = sys.argv[1:]
    if len(args) != 2:
        print(USAGE)
        sys.exit(1)
    command, filepath = args
    if command not in ("compile", "run"):
        print(f"Error: unknown command '{command}'")
        print(USAGE)
        sys.exit(1)

    cs_path = os.path.abspath(filepath)
    if not os.path.isfile(cs_path):
        print(f"Error: file not found: {cs_path}", file=sys.stderr)
        sys.exit(1)

    try:
        if command == "compile":
            cmd_compile(cs_path)
        elif command == "run":
            cmd_run(cs_path)

    except LexerError as e:
        print(f"Lexer error:  {e}", file=sys.stderr)
        sys.exit(1)
    except ParseError as e:
        print(f"Parse error:  {e}", file=sys.stderr)
        sys.exit(1)
    except TypeCheckError as e:
        print(f"Type error    : {e}", file=sys.stderr)
        sys.exit(1)
    except CodeGenError as e:
        print(f"Codegen error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
