# CryptoScript DSL

*Note: For detailed instructions on installation, setup, and how the language works and functions, please refer to the [User Guide](docs/CryptoScript_DSL_User_Guide.pdf).*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Target User Group](#2-target-user-group)
3. [Architecture Overview](#3-architecture-overview)
4. [DSL Language Specification](#4-dsl-language-specification)
5. [Build and Run Instructions](#5-build-and-run-instructions)
6. [User Survey Summary](#6-user-survey-summary)
7. [Sample Program & Output](#7-sample-program--output)
8. [Project Demo Video](#9-project-demo-video)

---

## 1. Project Overview

**CryptoScript** is a Domain-Specific Language (DSL) designed for expressing cryptographic algorithms concisely and readably. It transpiles to Python, leveraging Python's arbitrary-precision integers and standard library.

**Problems with Python for cryptography:**
- Clunky byte/integer/hex conversions written manually everywhere.
- Repetitive modulo operations for finite-field arithmetic.
- Nested function calls that obscure cipher data-flow.
- No native concept of a cipher with an automatically derived decrypt.

**CryptoScript adds:**
- **Dedicated cryptographic types**: `Bytes`, `Hex`, `ModInt[n]`, `Matrix[T, r, c]`.
- **Pipeline operator (`|>`)** for readable left-to-right data flow.
- **`cipher` blocks** that auto-derive the decrypt method from the encrypt pipeline.
- **`sbox` / `pbox` declarations** for substitution and permutation tables.
- **`repeat` blocks** for round-based cipher structures.
- **Built-in transform primitives**: `xor`, `substitute`, `permute`, `rotl`, `rotr`, `pad`, `unpad`.
- **Type-checked compilation** that catches mismatches at compile time.
- **Single-line comments** using `#`.

---
## 2. Target User Group
Cryptographers, security researchers, and students who need to implement ciphers and cryptographic algorithms not wanting to limit themselves by native Python's syntax limitations.

## 3. Architecture Overview

```
Source (.crypto file)
       │
       ▼
  ┌─────────┐
  │  Lexer  │  (lexer.py)           — source text → flat token stream
  └────┬────┘
       ▼
  ┌─────────┐
  │  Parser │  (parser.py)          — token stream → AST
  └────┬────┘
       ▼
  ┌──────────────┐
  │ Type Checker │  (type_checker.py) — AST → type errors / pass
  └──────┬───────┘
         ▼
  ┌─────────┐
  │ CodeGen │  (codegen.py)         — AST → Python source string
  └────┬────┘
       ▼
  Output (.py file or exec())
```

All four passes share AST node classes from `ast_nodes.py`. Each node uses the **Visitor pattern** via `accept(visitor)`.

---

## 4. DSL Language Specification

### 4.1 Keywords

| Keyword | Description |
|---|---|
| `cipher` | Defines a cipher class with auto-generated encrypt and decrypt |
| `encrypt` | Forward transformation pipeline inside a `cipher` block |
| `sbox` | Substitution box declaration |
| `pbox` | Permutation box declaration |
| `repeat` | Repeats a pipeline block or statement body N times |

All standard Python control-flow keywords are also supported.

### 4.2 Data Types

| Type | Description | Python equivalent |
|---|---|---|
| `Int` | Arbitrary-precision integer | `int` |
| `Bool` | Boolean | `bool` |
| `String` | UTF-8 text | `str` |
| `Bytes` | Raw byte array | `bytes` |
| `Hex` | Hex value (interchangeable with `Int`) | `int` |
| `ModInt[n]` | Integer mod `n`; `+`, `-`, `*`, `**` auto-apply mod | `ModInt` class |
| `Matrix[T, r, c]` | `r×c` matrix of `T` elements | `Matrix` class |

```python
x: Int = 42
key: Bytes = b"\xAA\xBB"
n: ModInt[13] = 10
m: Matrix[Int, 3, 3]     # defaults to zero matrix
```

### 4.3 Operators

All standard Python operators are supported, plus:

| Operator | Description |
|---|---|
| `\|>` | Pipeline — passes left-hand value as first arg to the right-hand call |

```python
# Without pipeline:
result = xor(substitute(permute(data, p), s), key)

# With pipeline:
result = data |> permute(p) |> substitute(s) |> xor(key)
```

### 4.4 Transform Primitives

| Primitive | Input | Description |
|---|---|---|
| `substitute(sbox)` | `Bytes` | Replace each byte via sbox lookup |
| `permute(pbox)` | `Bytes` | Rearrange bytes via pbox positions |
| `xor(key)` | `Bytes` | XOR with key (key repeats if shorter) |
| `rotl(n, bits=32)` | any | Rotate bits left |
| `rotr(n, bits=32)` | any | Rotate bits right |
| `pad(scheme)` | `Bytes` | Pad to block size (`PKCS7` or `ZERO`) |
| `unpad(scheme)` | `Bytes` | Remove padding |

### 4.5 Type Conversions

| Function | Description |
|---|---|
| `to_bytes(expr)` | `Int`/`Hex`/`String` → `Bytes` (big-endian for int; UTF-8 for str) |
| `to_le_bytes(expr)` | Same but little-endian |
| `to_be_bytes(expr)` | Same but explicitly big-endian |
| `to_hex(expr)` | `Int`/`Bytes`/`String` → hex string e.g. `"0xff"` |
| `to_string(expr)` | `Bytes` → UTF-8; `Int` → hex string |
| `to_int(expr)` | `Bytes` → big-endian int; `String` → `int(v, 0)` |

### 4.6 Padding Schemes

| Name | Description |
|---|---|
| `PKCS7` | Adds N bytes each with value N to reach the block boundary |
| `ZERO` | Appends `\x00` bytes to the next block boundary |

### 4.7 Comments

```python
# Full-line comment
sbox s = [1, 0, 3, 2]   # inline comment
```

Everything from `#` to end of line is stripped by the lexer — completely invisible to the parser and type checker.

---

## 5. Build and Run Instructions

### Requirements

- Python 3.10+
- `pytest` (for tests)

### Setup

```bash
git clone https://github.com/Software-Group-10/CryptoScript.git
cd CryptoScript
source scripts/setup.sh
```

The setup script creates a `Crypto/` virtual environment, installs dependencies, and registers `transpile` / `run` shell aliases.

### Usage

```bash
# Run a .crypto file directly
run <your_cs_file.crypto>

# Transpile a .crypto file to a .py file
transpile <your_cs_file.crypto>

# Then run the transpiled output normally
python <your_py_file.py>
```

### Tests

```bash
source Crypto/bin/activate
pytest tests/unit_tests/        # all tests
pytest tests/unit_tests/ -v     # verbose
```

## 6. User Survey Summary

A **"CryptoScript: Developer Experience & Syntax Survey"** ([Google Form Link](https://forms.gle/Lj239S2KGEU1HYmg6)) was circulated to users and **responses** were collected.

### Q — Which transformation or primitive do you feel is missing?

| Response |
|---|
| "Dealing with blocks of data in block ciphers would be a great addition" |
| "Inherent support for block based ciphers" |
| "Data conversion in ciphers can't be used" |

### Q — Were the error messages helpful when you had syntax errors or type mismatches?

There was mixed feedback regarding error messages with some users complaining that they were confusing while dubbuging

**Action taken:** Error messages across all compiler stages were revised — each now shows the full offending source line, a `^` caret at the exact problem location, and a plain-English explanation of what went wrong.

### Q — Any additional feedback or bugs?

| Response | Category |
|---|---|
| "error messages could have been better" | Error reporting |
| "Fix setup.bash, call the command `transpile` (it's not compiling, it's transpiling)" | Tooling / naming |
| "We using this in libbabel." | Real-world adoption |
| "Would have liked support for comments" | Language feature |

**Actions taken:**
- **`#` comment support added** — stripped at the lexer stage, invisible to the parser.
- **Error messages improved** — see above.
- **`transpile` naming** — CryptoScript performs source-to-source transpilation (`.crypto` → `.py`). The `compile` command name is changed to `transpile` noting the technical difference.

---

## 7. Sample Program & Output

### Source (`cipher.crypto`)

**`cipher.crypto`**
```python
sbox s = [1, 0, 3, 2, 5, 4, 7, 6]

cipher MyCipher(key: Bytes, iv: Bytes) -> Bytes:
    encrypt:
        data |> pad(PKCS7) |> xor(iv) |> repeat(3):
            xor(key) |> substitute(s)
        |> xor(key)

mycipher = MyCipher(b"\xAA", b"\x55")
plaintext = b"\x00\x01\x02\x03"
encrypted = mycipher.encrypt(plaintext)
decrypted = mycipher.decrypt(encrypted)
print("Plaintext :", plaintext)
print("Encrypted :", encrypted)
print("Decrypted :", decrypted)
```

**Running it:**
```bash
run cipher.crypto
```

```
Plaintext : b'\x00\x01\x02\x03'
Encrypted : b'UTWVYYYYYYYYYYYY'
Decrypted : b'\x00\x01\x02\x03'
```

**Generated Python (`transpile cipher.crypto`):**
```python
class MyCipher:
    def __init__(self, key: bytes, iv: bytes):
        self.key = key
        self.iv = iv

    def encrypt(self, data):
        _result = data
        _result = pad(_result, "PKCS7")
        _result = xor(_result, self.iv)
        for _round in range(3):
            _result = xor(_result, self.key)
            _result = substitute(_result, s)
        _result = xor(_result, self.key)
        return _result

    def decrypt(self, data):          # auto-generated
        _result = data
        _result = xor(_result, self.key)
        for _round in range(3):
            _result = substitute(_result, _cs_invert_sbox(s))
            _result = xor(_result, self.key)
        _result = xor(_result, self.iv)
        _result = unpad(_result, "PKCS7")
        return _result
```

---

## 8. Project Demo Video

A video walkthrough of CryptoScript is available as part of the course presentation. It covers the motivation, DSL syntax, the cipher-block auto-inversion feature, and a live demo of compiling and running a cipher program.

**[Link to be added]**
