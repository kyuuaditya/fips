import hashlib

class Conversion:
    def __init__(self):
        self.N = 256 # fixed for all
        self.q = 8380417 # fixed for all

    def H(self, input_bytestring: bytes, output_bytestring_length: int) -> bytes:
        """
        Implementation the H(str, l) hashing using SHAKE256.

        Args:
            input_bytestring (bytes): The bytestring to hash.
            output_bytestring_length (int): The desired length of the output hash in bytes.
        Returns:
            Output (bytes): The resulting hash as a byte string.
        Raises:
            TypeError: If input is not a bytes object.
        """
        if not isinstance(input_bytestring, (bytes, bytearray)):
            raise TypeError("Input must be a bytes or bytearray object.")

        # 1. Initialize the SHAKE256 hash object
        shake = hashlib.shake_256()

        # 2. Provide the input data ('str') to the object
        shake.update(input_bytestring)

        # 3. Request the final hash with the desired length
        return shake.digest(output_bytestring_length)   

    def bytes_to_bits(self, z: bytes) -> str:
        """
        Converts a byte string z into a bit string in little-endian order.
    
        Args:
            z (bytes): A byte string (Python `bytes` object).
    
        Returns:
            str (bit string): A bit string ('0' and '1') of length 8 * len(z), in little-endian order.
    
        Raises:
            TypeError: If z is not a bytes object.
        """
        if not isinstance(z, (bytes, bytearray)):
            raise TypeError("Input z must be a bytes or bytearray object.")
    
        bits = []
        for byte in z:
            for i in range(8):
                bits.append(str((byte >> i) & 1))  # Little-endian bit order

        return ''.join(bits)

    def bits_to_integer(self, y: str, alpha: int) -> int:
        """
        Converts a bit string of length alpha (in little-endian order) to an integer.

        Args:
            y (bit string): Bit string to convert to an integer.
            alpha (int): Number of bits to consider.

        Returns:
            integer (int): The integer value represented by the bit string.

        Raises:
            ValueError: If the length of y does not match alpha or if y contains invalid characters.
            TypeError: If y is not a string or alpha is not an integer.
        """
        # Input validation
        if not isinstance(y, str):
            raise TypeError("Input y must be a string.")
        if not isinstance(alpha, int):
            raise TypeError("Input alpha must be an integer.")
        if alpha <= 0:
            raise ValueError("alpha must be a positive integer.")
        if len(y) != alpha:
            raise ValueError(f"Bit string y must have exactly {alpha} bits.")
        if any(bit not in "01" for bit in y):
            raise ValueError("Bit string y must contain only '0' and '1' characters.")

        x = 0
        for i in range(1, alpha + 1):
            bit = int(y[alpha - i])  
            x = 2 * x + bit
        return x

    def integer_to_bits(self, x: int, alpha: int):
        """
        Algorithm 9: FIPS 204
        Computes the base-2 representation of x mod 2^alpha in little-endian bit string format.

        Args:
            x (int): A non-negative integer.
            alpha (int): Number of bits to represent.

        Returns:
            str (bits): Bit string of length alpha in little-endian order (e.g., "10100000").

        Raises:
            ValueError: If x is negative or alpha is not a positive integer.
            ValueError: If x is too big to be represented in alpha bits.
            TypeError: If x or alpha is not an integer.
        """

        # input check
        if not isinstance(x, int) or not isinstance(alpha, int):
            raise TypeError("Both x and alpha must be integers.")
        if x < 0:
            raise ValueError("x must be non-negative.")
        if alpha <= 0:
            raise ValueError("alpha must be a positive integer.")
        if x >= 2 ** alpha:
            raise ValueError(f"x = {x} cannot be represented in {alpha} bits.")
        
        x_mod = x
        bits = []
        for _ in range(alpha):
            bits.append(str(x_mod % 2))
            x_mod //= 2

        return ''.join(bits)

    def bits_to_bytes(self, y: str) -> bytes:
        """
        Converts a bit string y into a byte string using little-endian order.

        Args:
            y (str): Bit string consisting of '0' and '1'.

        Returns:
            bytes (bytes): Byte string (little-endian) of length ceil(len(y) / 8).

        Raises:
            TypeError: If y is not a string.
            ValueError: If y contains characters other than '0' or '1'.
        """
        if not isinstance(y, str):
            raise TypeError("Input y must be a string.")
        if any(bit not in "01" for bit in y):
            raise ValueError("Bit string y must contain only '0' and '1'.")

        alpha = len(y)
        byte_len = (alpha + 7) // 8  # Equivalent to ceil(alpha / 8)
        z = [0] * byte_len

        for i in range(alpha):
            byte_index = i // 8
            bit_index = i % 8
            z[byte_index] |= int(y[i]) << bit_index

        return bytes(z)

    def integer_to_bytes(self, x: int, alpha: int) -> bytes:
        """
        Computes a base-256 representation of x mod 256^alpha in little-endian order.
        Args:
            x (int): A non-negative integer.
            alpha (int): Number of bytes in the output.
        Returns:
            bytes (bytes): Byte string of length alpha in little-endian order.
        Raises:
            ValueError: If x is negative or alpha is not positive.
            TypeError: If x or alpha is not an integer.
        """
        # Input validation
        if not isinstance(x, int) or not isinstance(alpha, int):
            raise TypeError("Both x and alpha must be integers.")
        if x < 0:
            raise ValueError("x must be a non-negative integer.")
        if alpha <= 0:
            raise ValueError("alpha must be a positive integer.")
        if x >= 256 ** alpha:
            raise ValueError(f"x = {x} cannot be represented in {alpha} bytes.")

        x_mod = x % (256 ** alpha)
        byte_list = []
        for _ in range(alpha):
            byte_list.append(x_mod % 256)
            x_mod //= 256
        return bytes(byte_list)

    def centered_modulus(self, z):     
        """
        Computes the centered modulus z mod± q for an integer or a list of integers.

        This operation maps an integer x to the unique value r in the range
        [-(q-1)/2, (q-1)/2] such that x is congruent to r (mod q).

        Args:
            z (int or list): An integer or a list of integers to be reduced.

        Returns:
            z (int or list): The result of the centered modulus operation. If the input z was a
            list, the output will be a list of the same size. Returns None if the
            input type is invalid.
        Raises:
            TypeError: If z is not an integer or a list of integers or a list of list of integers.
        """

        # This is the upper bound of the centered range, which is also our offset.
        half_q = (self.q - 1) // 2

        # Define a helper function to perform the operation on a single integer.
        def _reduce_single_int(x):
            # This is a more direct mathematical way to compute the centered modulus.
            # 1. Add half_q to shift the range.
            # 2. Perform the standard modulus operation.
            # 3. Subtract half_q to shift the range back to being centered at zero.
            # print(x)
            # print(half_q)
            return (x + half_q) % self.q - half_q

        # Apply the operation based on the input type.
        if isinstance(z, int):
            return _reduce_single_int(z)
        elif isinstance(z[0], int):
            return [_reduce_single_int(p) for p in z]
        elif isinstance(z[0], list):
            return [[_reduce_single_int(p) for p in z[k]] for k in range(len(z))]
        else:
            raise TypeError("Input z must be an integer or a list of integers or a list of list of integers.")

    def abs_for_list (self, z: list) -> list:
        """
        Computes the absolute values of a list of integers.
        Args:
            z (list): A list of integers.
        Returns:
            |z| (list): A list containing the absolute values of the input integers.
        """
        # checking input type
        if not isinstance(z, list):
            raise TypeError("Input z must be a list of integers.")
        for p in z:
            if not isinstance(p, int):
                raise TypeError("All elements in the list z must be integers.")

        for p in range (len(z)):
            z[p] = abs(z[p])

        return z
    
    def infinity_norm(self, z: list) -> int:
        """
        helper function to calcute the l infinity norm of a 2d list.
        Args:
            z (list): A list of list of integers.
        Returns:
            infinity_norm (int): The infinity norm (maximum absolute value) among all lists.
        Raises:
            TypeError: If z is not a list of lists of integers.
            TypeError: If any element in the sublists is not an integer.
            TypeError: If elements of z[x] are not lists.
        """
        if not isinstance(z, list):
            raise TypeError("Input z must be a list.")
        for sublist in z:
            if not isinstance(sublist, list):
                raise TypeError("Input z must be a list of lists of integers.")
            for p in sublist:
                if not isinstance(p, int):
                    raise TypeError("All elements in the list z must be integers.")

        max_value = 0

        for i in range (len(z)):
            if max_value < max(self.abs_for_list(self.centered_modulus(z[i]))):
                max_value = max(self.abs_for_list(self.centered_modulus(z[i])))

        return max_value # returns the max value among all lists.
    
    def calc_ones(self, h: list) -> int:
        """
        a helper function to calculate the number of 1s inside a list[ list [ int ] ].
        Args:
            h (list): A 2D list containing 0s and 1s.
        Returns:
            int: The count of 1s in the 2D list.
        Raises:
            TypeError: If h is not a list of lists of integers.
            TypeError: If any element in the sublists is not an integer.
            TypeError: If elements of h[x] are not 0 or 1.
        """
        if not isinstance(h, list):
            raise TypeError("Input h must be a list.")
        for sublist in h:
            if not isinstance(sublist, list):
                raise TypeError("Input h must be a list of lists of integers.")
            for p in sublist:
                if not isinstance(p, int) and p not in (0, 1):
                    raise TypeError("All elements in the list h must be integers.")
        count = 0
        for i in range(len(h)):
            for j in range(len(h[i])):
                if h[i][j] == 1:
                    count = count + 1

        return count
    
