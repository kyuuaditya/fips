

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

        _, r0 = self.decompose(r)
        return r0
    
    def lowBits_polynomial(self, r: list):
        """
        returns the low bits r0 from the decomposition of r.
        Args:
            r (list): a polnomial where all coefficients are integers in the range [0, q-1].
        Returns:
            r0 (list): The low bits r0.
        Raises:
            TypeError: If r is not an list.
        """

        if not isinstance(r, list):
            raise TypeError("Input r must be an list.")

        r0 = [0 for _ in range(self.N)]
        for i in range(self.N):
            r0[i] = self.lowBits(r[0])
        return r0
    
    def lowBits_vector(self, r: list):
        """
        returns the low bits r0 from the decomposition of r.
        Args:
            r (list): a polnomial where all coefficients are integers in the range [0, q-1].
        Returns:
            r0 (list): The low bits r0.
        Raises:
            TypeError: If r is not an list.
        """

        if not (isinstance(r, list) or isinstance(r[0], list)):
            raise TypeError("Input r must be an list of polynomials.")

        r0 = [[0 for _ in range(self.N)] for _ in range(len(r))]
        for i in range(len(r)):
            r0[i] = self.lowBits_polynomial(r[i])
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
    
    def make_hint_polynomial(self, z_poly: list[int], r_poly: list[int]) -> list[bool]:
        """
        computes hint polynomial indicating whether adding z to r alters the high bits of r for each coefficient.
        Args:
            z_poly (list[int]): A list of integers representing the polynomial z.
            r_poly (list[int]): A list of integers representing the polynomial r.
        Returns:
            hint_poly (list[bool]): A list of booleans indicating whether the high bits change for each coefficient.
        Raises:
            TypeError: If z_poly or r_poly is not a list of integers.
            ValueError: If z_poly and r_poly are not of the same length.
        """
        if not isinstance(z_poly, list) or not all(isinstance(x, int) for x in z_poly):
            raise TypeError("Input z_poly must be a list of integers.")
        if not isinstance(r_poly, list) or not all(isinstance(x, int) for x in r_poly):
            raise TypeError("Input r_poly must be a list of integers.")
        if len(z_poly) != len(r_poly):
            raise ValueError("Input polynomials must be of the same length.")

        hint_poly = []
        for z_coeff, r_coeff in zip(z_poly, r_poly):
            hint = self.make_hint(z_coeff, r_coeff)
            hint_poly.append(hint)
        
        return hint_poly
    
    def make_hint_vector(self, z_vec: list[list[int]], r_vec: list[list[int]]) -> list[list[bool]]:
        """
        computes hint vector indicating whether adding z to r alters the high bits of r for each coefficient in each polynomial.
        Args:
            z_vec (list[list[int]]): A list of lists of integers representing the vector of polynomials z.
            r_vec (list[list[int]]): A list of lists of integers representing the vector of polynomials r.
        Returns:
            hint_vec (list[list[bool]]): A list of lists of booleans indicating whether the high bits change for each coefficient in each polynomial.
        Raises:
            TypeError: If z_vec or r_vec is not a list of lists of integers.
            ValueError: If z_vec and r_vec are not of the same length.
        """
        if not isinstance(z_vec, list) or not all(isinstance(poly, list) and all(isinstance(x, int) for x in poly) for poly in z_vec):
            raise TypeError("Input z_vec must be a list of lists of integers.")
        if not isinstance(r_vec, list) or not all(isinstance(poly, list) and all(isinstance(x, int) for x in poly) for poly in r_vec):
            raise TypeError("Input r_vec must be a list of lists of integers.")
        if len(z_vec) != len(r_vec):
            raise ValueError("Input vectors must be of the same length.")

        hint_vec = []
        for z_poly, r_poly in zip(z_vec, r_vec):
            hint_poly = self.make_hint_polynomial(z_poly, r_poly)
            hint_vec.append(hint_poly)
        
        return hint_vec
    
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

