

class Operations:
    def __init__(self, gamma2):
        self.N = 256 # fixed for all
        self.q = 8380417 # fixed for all

        self.gamma2 = gamma2

    def decompose(self, r: int) -> tuple[int, int]:
        """
        Algorithm 36 FIPS 204

        Decomposes r into (r1, r0) such that:
            r ≡ r1*(2*gamma2) + r0 (mod q)
        Args:
            r (int): An integer in the range [0, q-1].
        Returns:
            tuple (int, int): r1, r0 where:
                r1: The high bits.
                r0: The low bits in the range [-2^(d-1)+1, 2^(d-1)].
        Raises:
            TypeError: If r is not an integer.
        """
        if not isinstance(r, int):
            raise TypeError("Input r must be an integer.")

        r_plus = r % self.q

        mod_val = 2 * self.gamma2
        r0 = r_plus % mod_val

        # Adjust to the centered range [-2^(d-1)+1, 2^(d-1)]
        if r0 > mod_val // 2:
            r0 -= mod_val
        
        if (r_plus - r0) == self.q - 1:
            r1 = 0
            r0 = r0 - 1
        else:
            r1 = int((r_plus - r0) / (2 * self.gamma2))

        return r1, r0
    
    def highBits(self, r:int) -> int:
        """
        returns the high bits r1 from the decomposition of r.
        Args:
            r (int): An integer in the range [0, q-1].
        Returns:
            r1 (int): The high bits r1.
        Raises:
            TypeError: If r is not an integer.
        """
        if not isinstance(r, int):
            raise TypeError("Input r must be an integer.")
        
        r1, r0 = self.decompose(r)
        return r1
    
    def lowBits(self, r:int) -> int:
        """
        returns the low bits r0 from the decomposition of r.
        Args:
            r (int): An integer in the range [0, q-1].
        Returns:
            r0 (int): The low bits r0.
        Raises:
            TypeError: If r is not an integer.
        """
        if not isinstance(r, int):
            raise TypeError("Input r must be an integer.")

        r1, r0 = self.decompose(r)
        return r0
    
    def make_hint(self, z: int, r:int) -> bool:
        """
        computes hint bit indicating whether adding z to r alters the high bits of r.
        Args:
            z (int): An integer in the range [0, q-1].
            r (int): An integer in the range [0, q-1].
        Returns:
            bool (bool): True if the high bits change, False otherwise.
        Raises:
            TypeError: If z or r is not an integer.
        """
        # make some input checks here.
        if not isinstance(z, int):
            raise TypeError("Input z must be an integer.")
        if not isinstance(r, int):
            raise TypeError("Input r must be an integer.")

        r1 = self.highBits(r)
        v1 = self.highBits(r + z)
        return v1 != r1
    
    def use_hint(self, h: bool, r:int) -> int:
        """
        Returns the high bits of r adjusted according to hint h. 
        Args:
            h (bool): The hint bit.
            r (int): An integer in the range [0, q-1].
        Returns:
            r1 (int): The adjusted high bit.
        Raises:
            TypeError: If h is not a boolean.
            TypeError: If r is not an integer.
        """
        if not isinstance(h, (int, bool)):
            raise TypeError("Input h must be a boolean or integer(0, 1).")
        if not isinstance(r, int):
            raise TypeError("Input r must be an integer.")

        m = int((self.q - 1) / (2 * self.gamma2))

        r1, r0 = self.decompose(r)

        if h == 1 and r0 > 0:
            return (r1 + 1) % m
        if h == 1 and r0 <= 0:
            return (r1 - 1) % m
        return r1

