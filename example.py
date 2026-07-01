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
        return data.rstrip(b"\x00")
    raise ValueError(f"unpad: unknown scheme {scheme!r}")


def to_bytes(value, length=None, byteorder="big") -> bytes:
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
    return to_bytes(value, length=length, byteorder="little")


def to_be_bytes(value, length=None) -> bytes:
    return to_bytes(value, length=length, byteorder="big")


def to_hex(value) -> str:
    if isinstance(value, int):
        return hex(value)
    if isinstance(value, bytes):
        return "0x" + value.hex()
    if isinstance(value, str):
        return "0x" + value.encode("utf-8").hex()
    raise TypeError(f"to_hex: unsupported type {type(value).__name__}")


def to_string(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, int):
        return hex(value)
    return str(value)


def to_int(value) -> int:
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

s = [1, 0, 3, 2, 5, 4, 7, 6]
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

    def decrypt(self, data):
        _result = data
        _result = xor(_result, self.key)
        for _round in range(3):
            _result = substitute(_result, _cs_invert_sbox(s))
            _result = xor(_result, self.key)
        _result = xor(_result, self.iv)
        _result = unpad(_result, "PKCS7")
        return _result

mycipher = MyCipher(b'\xaa', b'U')
plaintext = b'\x00\x01\x02\x03'
encrypted = mycipher.encrypt(plaintext)
decrypted = mycipher.decrypt(encrypted)
print('Plaintext :', plaintext)
print('Encrypted :', encrypted)
print('Decrypted :', decrypted)