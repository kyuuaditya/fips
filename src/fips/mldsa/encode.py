from .packing import Packing

class Encode:
    def __init__(self, eta, k, l, gamma1, gamma2, omega, _lambda_):
        self.d = 13 # fixed for all
        self.N = 256 # fixed for all
        self.q = 8380417 # fixed for all

        self.eta = eta 
        self.k = k
        self.l = l
        self.gamma1 = gamma1
        self.gamma2 = gamma2
        self.omega = omega
        self._lambda_ = _lambda_

        self.packing = Packing(self.omega, self.k)

    def pk_encode(self, rho: bytes, t1_vec: list) -> bytes:
        """
        Implements Algorithm 22: pkEncode(rho, t₁).

        Encodes the public key into a single bytestring.
        Args:
            rho (bytes): The 32-byte seed.
            t1_vec (list): The vector of k polynomials for t₁.
        Returns:
            public_key (bytes): The final encoded public key as a bytestring.
        Raises: 
            ValueError: if rho or t1_vec are of incorrect types or lengths.
        """
        if not isinstance(rho, (bytes, bytearray)) or len(rho) != 32:
            raise ValueError("rho must be a 32-byte  bytestring.")
        if not isinstance(t1_vec, list) or len(t1_vec) != self.k:
            raise ValueError(f"t1 must be a list of {self.k} polynomials.")

        # 1: pk ← ρ
        # Using a bytearray for efficient concatenation
        pk = bytearray(rho)

        # Calculate the number of bits needed to store each t₁ coefficient
        max_bit = pow(2, (self.q - 1).bit_length() - self.d) - 1 # This is 23 - 13 = 10

        # 2: for i from 0 to k - 1 do
        for poly_t1 in t1_vec:
            # 3: pk ← pk || SimpleBitPack(...)
            packed_poly = self.packing.simple_bit_pack(poly_t1, max_bit)
            pk.extend(packed_poly)

        # 5: return pk
        return bytes(pk)

    def sk_encode(self, rho: bytes, K_seed: bytes, tr: bytes, s1_vec: list, s2_vec: list, t0_vec: list) -> bytes:
        """
        Implements Algorithm 24: skEncode.
        Encodes all private key components into a single byte string.

        Args:
            rho (bytes): The 32-byte seed.
            K_seed (bytes): The 32-byte K seed.
            tr (bytes): The 64-byte tr value.
            s1_vec (list): The vector of l polynomials for s₁.
            s2_vec (list): The vector of k polynomials for s₂.
            t0_vec (list): The vector of k polynomials for t₀.
        Returns:
            private_key(bytes): The final encoded private key as a bytestring.

        Raises: 
            ValueError: if rho, K_seed, tr, s1_vec, s2_vec, or t0_vec are of incorrect types or lengths.
        """
        if not isinstance(rho, (bytes, bytearray)) or len(rho) != 32:
            raise ValueError("rho must be a 32-byte bytestring.")
        if not isinstance(K_seed, (bytes, bytearray)) or len(K_seed) != 32:
            raise ValueError("K_seed must be a 32-byte bytestring.")
        if not isinstance(tr, (bytes, bytearray)) or len(tr) != 64:
            raise ValueError("tr must be a 64-byte bytestring.")
        if not isinstance(s1_vec, list) or len(s1_vec) != self.l:
            raise ValueError(f"s1 must be a list of {self.l} polynomials.")
        if not isinstance(s2_vec, list) or len(s2_vec) != self.k:
            raise ValueError(f"s2 must be a list of {self.k} polynomials.")
        if not isinstance(t0_vec, list) or len(t0_vec) != self.k:
            raise ValueError(f"t0 must be a list of {self.k} polynomials.")

        # 1: sk ← ρ || K || tr
        sk = bytearray(rho + K_seed + tr)

        # 2-4: Pack and append s₁
        for poly in s1_vec:
            sk.extend(self.packing.bit_pack(poly, self.eta, self.eta))

        # 5-7: Pack and append s₂
        for poly in s2_vec:
            sk.extend(self.packing.bit_pack(poly, self.eta, self.eta))

        # 8-10: Pack and append t₀
        for poly in t0_vec:
            sk.extend(self.packing.bit_pack(poly, pow(2, self.d - 1) - 1, pow(2, self.d - 1)))

        # 11: return sk
        return bytes(sk)

    def sk_decode(self, private_key: bytes):
        """
        reverses the procedure performed by sk_encode.
        Args:
            private_key (bytes): The byte string representing the private key.
        Returns:
            ( rho, K_seed, tr, s1, s2, t0_vec ) (Tuple[ bytes, bytes, bytes, list, list , list]): A tuple containing (rho, K_seed, tr, s1, s2, t0_vec).
        Raises:
            ValueError: if private_key is of incorrect type.
        """
        if not isinstance(private_key, (bytes, bytearray)):
            raise ValueError("private_key must be a bytestring.")   
        
        if self.eta == 2:
            s_bytes = 96
        else:
            s_bytes = 128

        # find length of all the vectors
        s1_len = s_bytes * self.l 
        s2_len = s_bytes * self.k
        t0_len = 416 * self.k

        # check length of private_key
        if len(private_key) != 2 * 32 + 64 + s1_len + s2_len + t0_len:
            raise ValueError("SK packed bytes is of the wrong length")
        
        # Split bytes between seeds and vectors
        sk_seed_bytes, sk_vec_bytes = private_key[:128], private_key[128:]

        # Unpack seed bytes
        rho, K_seed, tr = (
            sk_seed_bytes[:32],
            sk_seed_bytes[32:64],
            sk_seed_bytes[64:128],
        )

        # Unpack vector bytes
        s1_bytes = sk_vec_bytes[:s1_len]
        s2_bytes = sk_vec_bytes[s1_len : s1_len + s2_len]
        t0_bytes = sk_vec_bytes[-t0_len:]
        # print(s1_len, " ", s2_len, " ", t0_len)

        # Unpack bytes to vectors
        s1 = [0 for _ in range(int(s1_len / s_bytes))]
        for i in range(int(s1_len / s_bytes)):
            s1[i] = self.packing.bit_unpack(s1_bytes[i * s_bytes: (i + 1) * s_bytes], self.eta, self.eta)

        s2 = [0 for _ in range(int(s2_len / s_bytes))]
        for i in range(int(s2_len / s_bytes)):
            s2[i] = self.packing.bit_unpack(s2_bytes[i * s_bytes: (i + 1) * s_bytes], self.eta, self.eta)

        t0_vec = [0 for _ in range(int(t0_len / 416))]
        for i in range(int(t0_len / 416)):
            t0_vec[i] = self.packing.bit_unpack(t0_bytes[i * 416 : (i + 1) * 416], pow(2, self.d - 1) - 1, pow(2, self.d - 1))

        return rho, K_seed, tr, s1, s2, t0_vec
    
    def w1_encode(self, w:list):
        """
        Algorithm 28 FIPS 204

        Encodes a polynomial vector w1 into a byte string. 
        Args:
            w (list): The list of k polynomials representing w.
        Returns:
            w1 (bytes): The encoded byte string w1.
        Raises: 
            ValueError: if w is of incorrect type or length.
        """
        if not isinstance(w, list) or len(w) != self.k:
            raise ValueError(f"w must be a list of {self.k} polynomials.")
        
        w1 = b''
        for i in range(self.k):
            w1 = w1 + self.packing.simple_bit_pack(w[i], int((self.q - 1)/(2 * self.gamma2)) - 1)
        return w1

    def sig_encode(self, c_tilda: bytes, z: list, h: list):
        """
        encodes a signature into a byte string.

        Args:
            c_tilda (bytes): The byte string representing c_tilda.
            z (bytes): The list of l polynomials representing z.
            h (bytes): The list representing the hint vector h.
        Returns:
            signature (bytes): The final encoded signature as a bytestring.
        Raises: 
            ValueError: if c_tilda, z, or h are of incorrect types or lengths.
        """
        if not isinstance(c_tilda, (bytes, bytearray)) or len(c_tilda) != int(self._lambda_ / 4):
            raise ValueError(f"c_tilda must be a bytestring of length {int(self._lambda_ / 4)}.")
        if not isinstance(z, list) or len(z) != self.l:
            raise ValueError(f"z must be a list of {self.l} polynomials.")
        if not isinstance(h, list):
            raise ValueError("h must be a list.")    

        sigma = b""
        sigma = sigma + c_tilda
        for i in range(self.l):
            sigma = sigma + self.packing.bit_pack(z[i], self.gamma1 -1, self.gamma1)
        
        sigma = sigma + self.packing.hint_bit_pack(h)

        return sigma
    
    def pk_decode(self, pk: bytes) -> tuple[bytes, list[list[int]]]:
        """
        Algorithm 23 FIPS 204
        
        Reverses the procedure pkEncode
        Args:
            pk (bytes): public key byte string:
                Byte string of length 32 + k * length_p, where length_p = ceil(256 * bitlen(q-1)-d / 8)

        Returns:
            tuple (rho, t1): A tuple containing:
                - rho: 32-byte seed.
                - t1: List of k polynomials, each with 256 coefficients in the range [0, 2^(bitlen(q-1)-d) - 1].
        Raises: 
            ValueError: if pk is of incorrect type.
        """
        if not  isinstance(pk, (bytes, bytearray)):
            raise ValueError("pk must be a bytestring.")

        bitlen = (self.q - 1).bit_length() - self.d
        expected_len = 32 + 32 * self.k * bitlen

        if not isinstance(pk, (bytes, bytearray)) or len(pk) != expected_len:
            raise ValueError(f"pk must be a byte string of length {expected_len} bytes.")

        rho = pk[:32] # assign the first 32 bits
        t1 = [] # initialize empty list

        offset = 32
        for i in range(self.k):
            start = i * 32 * bitlen + offset
            end = start + 32 * bitlen
            segment = pk[start:end]
            coeffs = self.packing.simple_bit_unpack(segment, pow(2, bitlen) - 1)
            if len(coeffs) != 256:
                raise ValueError("Each unpacked polynomial must have 256 coefficients.")
            t1.append(coeffs)

        return rho, t1

    def sig_decode(self, signature: bytes):
        """
        Decodes a signature from a byte string and returns its components.

        Args:
            signature (bytes): The byte string representing the signature.

        Returns:
            tuple (c_tilda, z, h): A tuple containing the decoded components.
        Raises: 
            ValueError: if signature is of incorrect type.
        """
        if not isinstance(signature, (bytes, bytearray)):
            raise ValueError("signature must be a bytestring.")

        c_tilda = signature[:int(self._lambda_ / 4)]
        x_list = signature[int(self._lambda_ / 4) : int(self._lambda_ / 4) + (32 * (1 + int((self.gamma1 - 1).bit_length()))) * self.l]
        y = signature[-(self.omega + self.k):] # last remaining elements.

        z = []   
        size_x = 32 * (1 + (self.gamma1 -1).bit_length())

        for i in range(self.l):
            start = i * size_x
            end = start + size_x
            segment = x_list[start : end]
            coefficients = self.packing.bit_unpack(segment, self.gamma1 -1, self.gamma1)
            z.append(coefficients)
        
        h = self.packing.hint_bit_unpack(y)

        return (c_tilda, z, h)
    
