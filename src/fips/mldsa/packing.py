from .conversion import Conversion

class Packing:
    def __init__(self, omega, k):
        self.N = 256 # fixed for all
        self.q = 8380417 # fixed for all

        self.omega = omega
        self.k = k

        self.convert = Conversion()

    def simple_bit_pack(self, w: list[int], b: int) -> bytes:
        """
        Implements Algorithm 16: SimpleBitPack.

        Packs a polynomial w ∈ R (length-256 list of ints), with each coefficient in [0, b],
        into a compact byte string using bit-packing.

        Args:
            w (list[int]): Polynomial coefficients, must be of length 256.
            b (int): Upper bound of coefficients. Must be ≥ 1.

        Returns:
            bytes (bytes): bytestring of length 32 * bitlen(b), representing packed bits.

        Raises:
            TypeError: If types are invalid.
            ValueError: If values/lengths are out of expected bounds.
        """
        # --- Validation ---
        if not isinstance(w, list) or not all(isinstance(c, int) for c in w):
            raise TypeError("w must be a list of integers.")
        if not isinstance(b, int):
            raise TypeError("b must be an integer.")
        if len(w) != 256:
            raise ValueError("Polynomial w must have exactly 256 coefficients.")
        if b < 1:
            raise ValueError("b must be at least 1.")
        if any(c < 0 or c > b for c in w):
            # print(w)
            raise ValueError(f"All coefficients must be in the range [0, {b}].")


        # --- Bit-packing ---
        bitlen = b.bit_length()  # Number of bits needed to represent b
        bitstring = ""

        for i in range(256):
            bits = self.convert.integer_to_bits(w[i], bitlen)
            bitstring += bits

        # Convert the full bitstring to bytes
        return self.convert.bits_to_bytes(bitstring)
    
    def bit_pack(self, w: list[int], a: int, b: int) -> bytes:
        """
        Implements Algorithm 17: BitPack.

        Packs a polynomial w (length-256) with coefficients in [-a, b]
        into a byte string using (a + b)-based encoding.

        Args:
            w (list[int]): List of 256 polynomial coefficients in [-a, b].
            a (int): Lower bound (non-negative).
            b (int): Upper bound (non-negative).

        Returns:
            bytes (bytes): Packed byte string of length 32 * bitlen(a + b).

        Raises:
            TypeError: If w is not a list of integers or a/b are not ints.
            ValueError: If length of w ≠ 256, or any coefficient is out of range.
        """

        # --- Input Validation ---
        if not isinstance(w, list) or not all(isinstance(x, int) for x in w):
            raise TypeError("w must be a list of integers.")
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("a and b must be integers.")
        if a < 0 or b < 0:
            raise ValueError("a and b must be non-negative integers.")
        if len(w) != 256:
            raise ValueError("w must have exactly 256 coefficients.")
        if any(x < -a or x > b for x in w):
            raise ValueError(f"Each coefficient must be in the range [-{a}, {b}].")

        # --- Bit Packing ---
        bitlen = (a + b).bit_length()
        z = ""

        for coeff in w:
            # Convert b - wᵢ to binary (Algorithm line 3)
            encoded = self.convert.integer_to_bits(b - coeff, bitlen)
            z += encoded

        # Convert full bit string to bytes
        return self.convert.bits_to_bytes(z)

    def bit_unpack(self, v: bytes, a: int, b: int) -> list[int]:
        """
        Algorithm 19: BitUnpack.

        Reconstructs a polynomial w (256 coefficients) from a packed byte string
        where the original coefficients were in [-a, b].

        Args:
            v (bytes): Packed byte string (length = 32 * bitlen(a + b)).
            a (int): Non-negative integer (lower bound).
            b (int): Non-negative integer (upper bound).

        Returns:
            polynomial (list[int]): List of 256 coefficients in the range [-a, b].

        Raises:
            TypeError: If input types are incorrect.
            ValueError: If v is invalid length or a/b are negative.
        """
        # --- Input Checks ---
        if not isinstance(v, (bytes, bytearray)):
            raise TypeError("Input v must be a byte string.")
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("a and b must be integers.")
        if a < 0 or b < 0:
            raise ValueError("a and b must be non-negative.")

        # --- Step 1: Compute bit length ---
        c = (a + b).bit_length()
        expected_len = 32 * c
        if len(v) != expected_len:
            raise ValueError(f"Expected input length = {expected_len} bytes for a + b = {a + b}, got {len(v)}.")

        # --- Step 2: Convert bytes to bitstring ---
        z = self.convert.bytes_to_bits(v)

        # --- Step 3–5: Decode coefficients ---
        w = []
        for i in range(256):
            start = i * c
            end = start + c
            bits = z[start:end]
            decoded = self.convert.bits_to_integer(bits, c)
            w.append(b - decoded)

        return w

    def hint_bit_pack(self, h: list[list[int]]) -> bytes:
        """
        Implements FIPS 204 Algorithm 20: HintBitPack(h)
    
        Args:
            h (list[list[int]]): A list of k polynomials, each of 256 binary coefficients.
    
        Returns:
            bytes (bytes): Byte string of length omega + k representing the packed hint vector.
    
        Raises:
            ValueError: If h is malformed or contains more than omega total 1s.
        """
        if not isinstance(h, list) or len(h) != self.k:
            raise ValueError(f"h must be a list of {self.k} polynomials.")
        if not all(isinstance(poly, list) and len(poly) == 256 for poly in h):
            raise ValueError("Each polynomial in h must be a list of 256 binary coefficients.")
        if not all(c in (0, 1) for poly in h for c in poly):
            raise ValueError("All coefficients in h must be 0 or 1.")
    
        y = [0] * (self.omega + self.k)
        index = 0
    
        for i in range(self.k):
            for j in range(256):
                if h[i][j] == 1:
                    if index >= self.omega:
                        raise ValueError("Number of 1s in h exceeds omega.")
                    y[index] = j
                    index += 1
            if index > 255:
                raise ValueError("index exceeds 255; encoding would overflow a byte.")
            y[self.omega + i] = index

        return bytes(y)

    def simple_bit_unpack(self, v: bytes, b: int) -> list[int]:
        """
        Implements Algorithm 18: SimpleBitUnpack.

        Reconstructs a polynomial with 256 coefficients from a packed byte string.

        Args:
            v (bytes): Byte string of length 32 * bitlen(b), result of simple_bit_pack.
            b (int): Upper bound for the original coefficients (must be ≥ 1).

        Returns:
            polynomial (list[int]): List of 256 unpacked coefficients in range [0, b].

        Raises:
            TypeError: If v is not bytes or b is not int.
            ValueError: If v has invalid length or b is invalid.
        """
        # --- Validation ---
        if not isinstance(v, (bytes, bytearray)):
            raise TypeError("Input v must be a byte string.")
        if not isinstance(b, int) or b < 1:
            raise ValueError("b must be a positive integer.")

        c = b.bit_length()  # bit length of b
        expected_length = 32 * c
        if len(v) != expected_length:
            raise ValueError(f"Input length must be {expected_length} bytes for b = {b}.")

        # --- Convert bytes to bitstring ---
        z = self.convert.bytes_to_bits(v)

        # --- Reconstruct coefficients ---
        w = []
        for i in range(256):
            start = i * c
            end = start + c
            bits = z[start:end]
            coeff = self.convert.bits_to_integer(bits, c)
            w.append(coeff)

        return w 

    def hint_bit_unpack(self, y: bytes):
        """
        Reverse of HintBitPack — reconstructs the hint vector h from the encoded bytes y.

        Args:
            y (bytes): Byte string of length omega + k that encodes h.
            omega (int): Parameter ω (number of 1s allowed in each vector).
            k (int): Number of polynomials (dimension).

        Returns:
            list of polynomials (list[list[int]]): h, a list of k polynomials, each being a list of ω-bit coefficients (0 or 1).
        Raises:
            ValueError: If y is malformed or does not conform to expected structure.
        """
        if not isinstance(y, (bytes, bytearray)):
            raise TypeError("Input y must be a byte string.")
        if len(y) != self.omega + self.k:
            raise ValueError(f"Invalid input length: expected {self.omega + self.k}, got {len(y)}")

        # Initialize h as a k×omega zero matrix (each polynomial has omega coefficients)
        h = [[0 for _ in range(self.N)] for _ in range(self.k)]
        index = 0

        for i in range(self.k):
            if y[self.omega + i] < index or y[self.omega + i] > self.omega:
                # malformed input
                print("first")
                return None
            

            First = index
            while index < y[self.omega + i]:
                if index > First:
                    if y[index - 1] >= y[index]:
                        # malformed input
                        print("second")
                        return None

                h[i][y[index]] = 1
                index = index + 1

        for i in range(index, self.omega):
            if y[i] != 0:
                print("forth")
                return None

        return h
    
    