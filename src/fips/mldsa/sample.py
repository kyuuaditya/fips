import hashlib
import math

from .conversion import Conversion
from .packing import Packing

class Sample:
    def __init__(self, eta, gamma1, k, l, _lambda_, tau, omega):
        self.N = 256 # fixed for all 
        self.q = 8380417 # fixed for all
        
        self.eta = eta
        self.gamma1 = gamma1
        self.l = l
        self.k = k
        self._lambda_ = _lambda_
        self.tau = tau
        self.omega = omega

        self.convert = Conversion()
        self.packing = Packing(self.omega, self.k)
        self.rejections = 0

    def CoeffFromThreeBytes(self, b0: int, b1: int, b2:int) -> int:
        """
        generates a number z from three input bytes b0, b1, b2.
        
        such that z belongs to {0, 1, 2, ... , q - 1} U { None }
        Args:
            b0 (int): first byte (0 - 255). 
            b1 (int): second byte (0 - 255).
            b2 (int): third byte (0 - 255).
        Returns:
            z (int): sampled coefficient or 'None' if rejected.
        Raises:
            TypeError: if any of b0, b1, b2 is not an integer
        """
        # checks for validity of inputs.
        for i, b in enumerate((b0, b1, b2), start = 0):
            if not isinstance(b, int):
                raise TypeError (f"b{i} must be in an integer.")
            if not (0 <= b <= 255):
                raise ValueError (f"b{i} must be in the range 0 - 255.")
        
        # line 1: make a copy of b2.
        b2_prime = b2

        # line 2 to 4: making sure b2_prime is 7 bits, not 8.
        if b2_prime > 127:
            b2_prime = b2_prime - 128
        
        # line 5: evaluate z for sampling.
        z = (b2_prime << 16) + (b1 << 8) + b0
        
        # line 6 to 8: reject the sample z if it's greater than q. 
        if z < self.q:
            return z # accept sample
        else:
            return None # reject sample

    def RejNTTPoly (self, rho: bytes) -> bytes:
        """
        samples a polynomial from a bytestring of length 34.
        Args:
            rho (bytes): a bytestring of length 34.
        Returns:
            polynomial (list): a list of integers representing the polynomial.
        raises:
            TypeError: if rho is not a bytestring.
            ValueError: if length of rho is not 34 bytes.    
        """
        # input checks.
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        if not (len(rho) == 34):
            raise ValueError ("length of rho must be exatcly 34 bytes.")

        # line 1: initialize j = 0 and the polynomial with all 0 coefficients.
        j = 0
        polynomial = [0 for _ in range (self.N)]

        # line 2: initialize shake_128 ; G.init().
        ctx = hashlib.shake_128() 

        # line 3: hash rho with the shake_128 object ; # G.Abosrb(ctx, rho).
        ctx.update(rho)

        byte_stream = ctx.digest(894) # store the hash in byte_stream for faster calling.
        byte_position = 0 # temprary variable to keep track of position in byte_stream.
        
        # line 4: main rejection loop.
        while j < 256:
            if byte_position + 3 > len(byte_stream): # to prevent byte_stream from going out of index.
                byte_stream += ctx.digest(self.N)
                print("ran out of bytes in rejection sampling! - max 894 bytes allowed")

            # line 5: take out next 3 bytes form the hash ; G.squeeze(ctx, 3).
            selected_3_bytes = byte_stream[byte_position : byte_position + 3]
            byte_position +=3 # update byte position to get next 3 byte on next selection.

            # line 6: sample an integer from 3 selected bytes.
            polynomial[j] = self.CoeffFromThreeBytes(selected_3_bytes[0], selected_3_bytes[1], selected_3_bytes[2])
            
            # line 7 to 9: increment j if sample is accepted.
            if polynomial[j] != None:
                j = j + 1 # sample accepted.

        # line 11: return the constructed polynomial.
        return polynomial

    def expand_A (self, rho: bytes) -> bytes:
        """
        samples a k x l matrix of polynomials.
        Args:
            rho (bytes): a bytestring of length 32.
        Returns:
            A (Matrix): a k x l matrix of polynomials.
        raises:
            ValueError: if length of rho is not 32 bytes.
        """
        #input checks.
        if not (len(rho) == 32) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 32-bytes bytestring.")
        
        A = [[0 for _ in range(self.l)] for _ in range(self.k)] # initialize the matrix of polynomials with all 0s.

        # line 1 to 2: loop over k and then l. 
        for r in range(self.k):
            for s in range (self.l):
                # line 3: concatenate rho with s and r.
                rho_prime = rho + self.convert.integer_to_bytes(s, 1) + self.convert.integer_to_bytes(r, 1)

                # line 4: construct a polynomial from rho_prime.
                A[r][s] = self.RejNTTPoly(rho_prime)
        
        return A # return the matrix A.        
    
    def CoeffFromHalfByte(self, b: int) -> int:
        """
        generates an element of {-eta, -eta+1, ... , eta} U { None }
        Args:
            b (int): an integer in the range 0 - 15.
        Returns:
            z (int): sampled coefficient or 'None' if rejected.
        Raises:
            TypeError: if b is not an integer.
            ValueError: if b is not in the range 0 - 15.
        """
        if not isinstance(b, int):
                raise TypeError (f"{b} must be in an integer.")
        if not (0 <= b <= 15):
                raise ValueError (f"{b} must be in the range 0 - 15.")

        # line 1 and 2: rejection sampline from {-2, ... , 2 }
        if self.eta == 2 and b < 15:
            return 2 - (b % 5)
        
        # line 3: rejection sampline from {-4, ... , 4 }
        elif self.eta == 4 and b < 9:
            return 4 - b
        
        # line 4: sample is just rejected.
        else:
            return None

    def RejBoundedPoly (self, rho: bytes) -> bytes:
        """
        samples an element a with coefficients in [-eta, eta] computed via rejection sampling from rho.
        Args:
            rho (bytes): a bytestring of length 66.
        Returns:
            a (list): a list of integers representing the polynomial.
        Raises:
            TypeError: if rho is not a bytestring.
        """
        # input checks.
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        if not (len(rho) == 66):
            raise ValueError ("length of rho must be exatcly 66 bytes.")
        
        # line 1: initialize j and polynomial a.
        j = 0
        a = [0 for _ in range(self.N)]

        # line 2: initialize shake_256 ; H.init().
        ctx = hashlib.shake_256() # H.init()

        # line 3: hash rho with the shake_256 object ; # H.Abosrb(ctx, rho).
        ctx.update(rho) # H.Abosrb(ctx, rho)

        byte_stream = ctx.digest(self.N) # store the hash in byte_stream for faster calling.
        byte_position = 0 # temprary variable to keep track of position in byte_stream.

        # line 4: main rejection loop.
        while j < 256:
            if byte_position + 1 > len(byte_stream): # to prevent byte_stream from going out of index.
                byte_stream += ctx.digest(self.N)
            
            # line 5: take out next byte form the hash ; H.squeeze(ctx, 1).
            z = byte_stream[byte_position]
            byte_position += 1 # update byte position go get next byte on next selection.

            # line 6: sample a number from z.
            z0 = self.CoeffFromHalfByte(z % 16)

            # line 7: sample a number from z / 16 (floor).
            z1 = self.CoeffFromHalfByte(math.floor(z / 16))
            
            # line 8 to 11: rejection checking for z0.
            if z0 != None:
                a[j] = z0 # accepted.
                j = j + 1

            # line 12 to 15: rejection checking for z1.
            if z1 != None and j < 256:
                a[j] = z1 # accepted.
                j = j + 1
        
        # line 17: return the polynomial a.
        return a

    def expand_S (self, rho: bytes) -> tuple[list, list]:
        """
        Samples two vector polynomials s1 and s2 such that coefficients are in the interval [-eta, eta]. 
        Args:
            rho (bytes): a bytestring of length 64.
        Returns:
            s1 (list): a list of l polynomials representing the vector s1.
            s2 (list): a list of k polynomials representing the vector s2.
        Raises:
            ValueError: if length of rho is not 64 bytes.
        """
        #input checks.
        if not (len(rho) == 64) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 64-bytes bytestring.")

        # initialize both s1 and s2.
        s1 = [[0 for _ in range(self.N)] for _ in range (self.l)]
        s2 = [[0 for _ in range(self.N)] for _ in range (self.k)]

        # line 1 to 3: create a polynomial from a 66 byte concatenated bytestring.
        for r in range (self.l):
            s1[r] = self.RejBoundedPoly(rho + self.convert.integer_to_bytes(r,2))
        
        # line 4 to 6: create a polynomial from a 66 byte concatenated bytestring.
        for s in range (self.k):
            s2[s] = self.RejBoundedPoly(rho + self.convert.integer_to_bytes(s + self.l, 2))

        # line 7: return s1 and s2 polynomail vectors.
        return (s1, s2)
    
    def expand_mask(self, rho: bytes, mew: int):
        """
        Samples a vector y ∈ R^l such that each polynomial y[r] has coefficients between -gamma1 + 1 and gamma1
        Args:
            rho (bytes): a bytestring of length 64.
            mew (int): an integer used in the sampling process.
        Returns:
            y (list): a list of polynomials representing the vector y.
        Raises:
            ValueError: if length of rho is not 64 bytes.
            TypeError: if mew is not an integer.
            ValueError: if mew is a negative integer.
        """
        if not (len(rho) == 64) and not isinstance(rho, bytes):
            raise ValueError ("rho must be a 64-bytes bytestring.")
        if not isinstance(mew, int):
            raise TypeError ("mew must be an integer.")
        if mew < 0:
            raise ValueError ("mew must be a non-negative integer.")

        if self.gamma1 == (1 << 17):
            bit_count = 18
            total_bytes = 576  # (256 * 18) / 8
        else:
            bit_count = 20
            total_bytes = 640  # (256 * 20) / 8

        y = [0 for _ in range(self.l)]

        for r in range (self.l):
            rho_prime = rho + self.convert.integer_to_bytes(mew + r, 2)
            v = self.convert.H(rho_prime, total_bytes)
            y[r] = self.packing.bit_unpack(v, self.gamma1 - 1, self.gamma1)
            
        return y

    def SampleInBall(self, rho: bytes) -> list:
        """
        Samples a polynomial with coefficients form {-1, 0, 1} and hamming weight tau <= 64.
        Args:
            rho (bytes): a bytestring of length lambda / 4 bits.
        Returns:
            c (list): a list of integers representing the polynomial.
        Raises:
            ValueError: if length of rho is not lambda / 4 bits.
            TypeError: if rho is not a bytestring.
        """
        if not isinstance (rho, (bytes, bytearray)):
            raise TypeError ("expected a bytestring as input.")
        if not (len(rho) == int(self._lambda_ / 4)):
            raise ValueError (f"value of rho must be exatcly {int(self._lambda_ / 4)} bits")
        
        c = [0 for _ in range(self.N)]
        ctx = hashlib.shake_256() # H.init()
        ctx.update(rho) # H.Abosrb(ctx, rho)

        search_multiplier = 1
        byte_stream = ctx.digest(self.N * search_multiplier) # the amount that we should digest is arbitrary here but will cause differences 

        h = self.convert.bytes_to_bits(byte_stream[:8])

        byte_position = 8
        for i in range(256 - self.tau, 256):
            j = byte_stream[byte_position]
            byte_position = byte_position + 1

            while j > i:
                if byte_position + 1 > len(byte_stream): # to prevent byte_stream from going out of index.
                    search_multiplier = search_multiplier + 1
                    byte_stream = ctx.digest(self.N * search_multiplier)
                j = byte_stream[byte_position]
                byte_position = byte_position + 1
            
            c[i] = c[j]
            if int(h[i + self.tau - 256]) == 1: # taking this as equivalent to being (-1)^h[i+tau-256]
                c[j] = -1
            else:
                c[j] = 1
        
        return c

    

