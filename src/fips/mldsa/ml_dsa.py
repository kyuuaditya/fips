import secrets

from .conversion import Conversion
from .sample import Sample
from .ntt import NTT
from .encode import Encode
from .operation import Operations

class MLDSA:
    def __init__(self, default_parameters: dict):
        self.q = default_parameters["q"]
        self.d = default_parameters["d"]
        self.N = default_parameters["N"]

        self.k = default_parameters["k"]
        self.l = default_parameters["l"]
        self.eta = default_parameters["eta"]
        self.gamma1 = default_parameters["gamma1"]
        self.gamma2 = default_parameters["gamma2"]
        self._lambda_ = default_parameters["_lambda_"]
        self.tau = default_parameters["tau"]
        self.omega = default_parameters["omega"]
        
        self.beta = self.tau * self.eta

        # ! initialize all other classes here later.
        self.convert = Conversion()
        self.sample = Sample(self.eta, self.gamma1, self.k, self.l, self._lambda_, self.tau, self.omega) 
        self.ntt = NTT()
        self.encode = Encode(self.eta, self.k, self.l, self.gamma1, self.gamma2, self.omega, self._lambda_)
        self.operation = Operations(self.gamma2)

        self.ZETAS = [
        0, 4808194, 3765607, 3761513, 5178923, 5496691, 5234739, 5178987, 
        7778734, 3542485, 2682288, 2129892, 3764867, 7375178, 557458, 7159240, 
        5010068, 4317364, 2663378, 6705802, 4855975, 7946292, 676590, 7044481, 
        5152541, 1714295, 2453983, 1460718, 7737789, 4795319, 2815639, 2283733, 
        3602218, 3182878, 2740543, 4793971, 5269599, 2101410, 3704823, 1159875, 
        394148, 928749, 1095468, 4874037, 2071829, 4361428, 3241972, 2156050, 
        3415069, 1759347, 7562881, 4805951, 3756790, 6444618, 6663429, 4430364, 
        5483103, 3192354, 556856, 3870317, 2917338, 1853806, 3345963, 1858416, 
        3073009, 1277625, 5744944, 3852015, 4183372, 5157610, 5258977, 8106357, 
        2508980, 2028118, 1937570, 4564692, 2811291, 5396636, 7270901, 4158088, 
        1528066, 482649, 1148858, 5418153, 7814814, 169688, 2462444, 5046034, 
        4213992, 4892034, 1987814, 5183169, 1736313, 235407, 5130263, 3258457, 
        5801164, 1787943, 5989328, 6125690, 3482206, 4197502, 7080401, 6018354, 
        7062739, 2461387, 3035980, 621164, 3901472, 7153756, 2925816, 3374250, 
        1356448, 5604662, 2683270, 5601629, 4912752, 2312838, 7727142, 7921254, 
        348812, 8052569, 1011223, 6026202, 4561790, 6458164, 6143691, 1744507, 
        1753, 6444997, 5720892, 6924527, 2660408, 6600190, 8321269, 2772600, 
        1182243, 87208, 636927, 4415111, 4423672, 6084020, 5095502, 4663471, 
        8352605, 822541, 1009365, 5926272, 6400920, 1596822, 4423473, 4620952, 
        6695264, 4969849, 2678278, 4611469, 4829411, 635956, 8129971, 5925040, 
        4234153, 6607829, 2192938, 6653329, 2387513, 4768667, 8111961, 5199961, 
        3747250, 2296099, 1239911, 4541938, 3195676, 2642980, 1254190, 8368000, 
        2998219, 141835, 8291116, 2513018, 7025525, 613238, 7070156, 6161950, 
        7921677, 6458423, 4040196, 4908348, 2039144, 6500539, 7561656, 6201452, 
        6757063, 2105286, 6006015, 6346610, 586241, 7200804, 527981, 5637006, 
        6903432, 1994046, 2491325, 6987258, 507927, 7192532, 7655613, 6545891, 
        5346675, 8041997, 2647994, 3009748, 5767564, 4148469, 749577, 4357667, 
        3980599, 2569011, 6764887, 1723229, 1665318, 2028038, 1163598, 5011144, 
        3994671, 8368538, 7009900, 3020393, 3363542, 214880, 545376, 7609976, 
        3105558, 7277073, 508145, 7826699, 860144, 3430436, 140244, 6866265, 
        6195333, 3123762, 2358373, 6187330, 5365997, 6663603, 2926054, 7987710, 
        8077412, 3531229, 4405932, 4606686, 1900052, 7598542, 1054478, 7648983]

    def ml_dsa_keygen_internal(self, input_seed: bytes) -> tuple[bytes, bytes]:
        """
        Algorithm 6 FIPS 204

        Generates a public-private key pair from a seed.
        Args:
            input_seed (bytes): 32 bytes input bytestring.
        Returns:
            ( public_key, private_key ) (Tuple[ bytes, bytes]): Tuple of key pair containing public key and private key.
        Raises:
            ValueError: If the input seed is not 32 bytes.
            TypeError: If the input seed is not a byte string.
        """
        if not isinstance (input_seed, (bytes, bytearray)):
            raise TypeError ("expected a byte string.")
        if len(input_seed) != 32:
            raise ValueError ("expected a 32-bytes bytestring.")

        # line 1: hash the input seed concatenated with k and l as bytes with shake_256 into a 128-bytes bytestring.
        Hash_result = self.convert.H(input_seed + self.convert.integer_to_bytes(self.k,1) + self.convert.integer_to_bytes(self.l,1), 128)

        # line 2: expand the Hash_result into 3 different parts.
        rho = Hash_result[0:32]         # a. Get ρ (rho):           The first 32 bytes
        rho_prime = Hash_result[32:96]  # b. Get ρ' (rho_prime):    The next 64 bytes
        K_seed = Hash_result[96:]       # c. Get K_seed:            The last 32 bytes

        # line 3: generate the matrix A (k x l) and store polynomials as list of coefficients.
        A_cap = self.sample.expand_A(rho)

        # line 4: generate and store s1 and s2 polynomial vectors.
        s1, s2 = self.sample.expand_S(rho_prime)

        # line 5 compute vector t as 'A.s1 + s2'. 
            # a. Transform s₁ into the NTT domain
        s1_ntt = [self.ntt.NTT(p) for p in s1] 
            # b. Compute the matrix-vector product Â ◦ NTT(s₁)
        product_ntt = [[0] * self.N for _ in range(self.k)] # initialize product of A_cap and NTT(s1)
        for i in range(self.k):
            for j in range(self.l):
                temprary_list = self.ntt.MultiplyNTT(A_cap[i][j], s1_ntt[j])
                for k in range(self.N):
                    product_ntt[i][k] = (product_ntt[i][k] + temprary_list[k]) % self.q
            # c. Transform the result back from the NTT domain
        product_ntt_inv = [self.ntt.inv_NTT(p) for p in product_ntt]
            # d. Add the second secret vector s₂
        t_vec = [self.ntt.AddNTT(product_ntt_inv[i], s2[i]) for i in range(self.k)]

        # line 6: decompose t into (t1, t0) such that r = (r1.2^d + r0) mod q
        t1_vector, t0_vector = self.ntt.power2round_vec(t_vec)

        # line 8: encode public_key
        public_key = self.encode.pk_encode(rho, t1_vector)

        # line 9: hash public key into 64 bytes to be used for private key generation.
        tr = self.convert.H(public_key, 64)

        # line 10: encode private_key
        private_key = self.encode.sk_encode(rho, K_seed, tr, s1, s2, t0_vector)
        
        # line 11: return both public and private keys.
        return public_key, private_key 

    def ml_dsa_keygen(self) -> tuple[bytes, bytes]:
        """
        Algorithm 1 FIPS 204

        Generates a public-private key pair for ML-DSA.
        Returns:
            ( public_key, private_key ) (Tuple[ bytes, bytes]): Tuple of key pair containing public key and private key.
        Raises:
            ValueError: If random seed generation fails.    
        """
        # 1: ξ ← B^32  (choose random 32-byte seed)
        try:
            random_32_byte_seed = secrets.token_bytes(32) # random seed

        # line 2: if ξ = Null then
        except Exception as e:
            # line 3: return None with an error.
            raise ValueError(f"Error: Failed to generate random seed. {e}")

        # 5: return ML-DSA.KeyGen_internal(ξ)
        return self.ml_dsa_keygen_internal(random_32_byte_seed)

    def ml_dsa_sign_internal(self, private_key: bytes, Message, input_seed):
        """
        Algorithm 7 FIPS 204
        
        Deterministic algorithm to generate a signature for a formatted message M'. 
        Args:
            private_key (bytes): The private key bytestring.
            Message (bitstring): The message to be signed in bits.
            input_seed (bytes): A 32-byte random seed for signature generation.
        Returns:
            signature (bytes): The generated ML-DSA signature as a bytestring.
        Raises:
            TypeError: If the private key or random input seed is invalid.
            ValueError: If the input seed is not 32 bytes.
            TypeError: If the message is not a bit string.
            ValueError: If the message has other than '0' and '1' characters.
        """
        if not isinstance (private_key, (bytes, bytearray)):
            raise TypeError("Invalid private key format.")
        if not isinstance (input_seed, (bytes, bytearray)):
            raise TypeError("Invalid random seed format.")
        if len(input_seed) != 32:
            raise ValueError("Invalid random seed length.")
        if not isinstance (Message, str):
            raise TypeError("Invalid message format.")
        if not all(bit in ('0', '1') for bit in Message):
            raise ValueError("Message must be a bit string.")

        # line 1: breaking the private key into 6 sub bytestrings.
        rho, K_seed, tr, s1_vec, s2_vec, t0_vec = self.encode.sk_decode(private_key)

        # line 2 to 4: performing polynomial wise NTT conversion.
        s1_cap = [self.ntt.NTT(p) for p in s1_vec]
        s2_cap = [self.ntt.NTT(p) for p in s2_vec]
        t0_cap = [self.ntt.NTT(p) for p in t0_vec]

        # line 5: sample a k x l matrix from input seed rho.
        A_hat = self.sample.expand_A(rho)

        # line 6: hash the message after concatenating it after tr with shake 256 into a 64-bytes bytestring.
        mew = self.convert.H(self.convert.bits_to_bytes(self.convert.bytes_to_bits(tr) + Message), 64)
        
        # line 7: compute a private random seed by hashing (K + input random seed + mew) with shake 256 into a 64-byte bytestring.
        rho_prime_prime = self.convert.H(K_seed + input_seed + mew, 64)

        # line 8 and 9: initialize kappa, z and H.
        kappa = 0
        z = None
        h = None

        # line 10: rejection sampling loop.
        while z == None and h == None:

            # line 11: generate a vector of l polynomials using private random seed.
            y = self.sample.expand_mask(rho_prime_prime, kappa)

            # line 12: create a vector of k polynomials by multiplying A and y in NTT domain.
            y_copy = [[y[i][j] for j in range (self.N)] for i in range (self.l)] # create a copy of vector y.
            y_ntt = [self.ntt.NTT(p) for p in y_copy] # apply the NTT conversion on copy of vector y.

            product_ntt = [[0] * self.N for _ in range(self.k)] # temporary vector to store result of NTT conversion.
            for i in range(self.k):
                for j in range(self.l): # temporary polynomial to store result of each multiplication in the loop.
                    temprary_list = self.ntt.MultiplyNTT(A_hat[i][j], y_ntt[j]) 
                    for k in range(self.N): # take sum of all temporary polynomials.
                        product_ntt[i][k] = (product_ntt[i][k] + temprary_list[k]) % self.q 
            
            w = [self.ntt.inv_NTT(p) for p in product_ntt] # NTT inverse function applied on the temporary the temporary vector.

            # line 13 and 14: component wise conversion to high bits.
            w_1 = [[self.operation.highBits(w[i][j]) for j in range (self.N)] for i in range (self.k)]

            # line 15: encode the vector polynomial w_1 into a byte string and hash it after concatenating it after mew into a bytestring of size lambda / 4 using shake 256. 
            c_tilda = self.convert.H(mew + self.encode.w1_encode(w_1), int(self._lambda_ / 4))

            # line 16: takes an input seed rho of length lambda / 4 and converts it into a polynomial c.
            c = self.sample.SampleInBall(c_tilda)

            # line 17: convert polynomial c into NTT domain.
            c_copy = [c[j] for j in range (self.N)] # create a copy of the polynomial c.
            c_ntt  = self.ntt.NTT(c_copy) # apply the NTT conversion on copy of polynomial c.

            # line 18: multiply polynomial c_ntt [256] with matrix s1 [l][256] int NTT domain and apply NTT inverse.
            product_cs1 = [[0] * self.N for _ in range(self.l)] # initialize cs1
            for j in range(self.l): # temporary polynomial to store result of each multiplication in the loop.
                temprary_list = self.ntt.MultiplyNTT(c_ntt, s1_cap[j])
                for k in range(self.N): # take sum of all temporary polynomials.
                    product_cs1[j][k] = temprary_list[k] % self.q

            product_cs1_inv = [self.ntt.inv_NTT(p) for p in product_cs1] # NTT inverse function applied on temporary vector.

            # line 19: multiply polynomial c_ntt [256] with matrix s2 [k][256] in NTT domain and apply NTT inverse.
            product_cs2 = [[0] * self.N for _ in range(self.k)] # initialize cs2
            for j in range(self.k): # temporary polynomial to store resutl of each multiplicaiton in the loop.
                temprary_list = self.ntt.MultiplyNTT(c_ntt, s2_cap[j])
                for k in range(self.N): # take sum of all temporary polynomials.
                    product_cs2 [j][k] =  temprary_list[k] % self.q        

            product_cs2_inv = [self.ntt.inv_NTT(p) for p in product_cs2] # NTT inverse function applied on temporary vector.

            # line 20: sum of 2 vectors of polynomials.
            z = [[0] * self.N for _ in range(self.l)] # initialize the empty vector.
            for i in range(self.l):
                for j in range(self.N):
                    z[i][j] = (y[i][j] + product_cs1_inv[i][j]) % self.q

            # line 21 and 22: component wise conversion to high bits after taking difference of vector w and vector cs2.
            r0 = [[0] * self.N for _ in range(self.k)] # initialize the empty vector.
            for i in range(self.k):
                for j in range(self.N):
                    r0[i][j] = self.operation.lowBits((w[i][j] - product_cs2_inv[i][j]) % self.q)

            # line 23: check l infinity norm for z and r0 
            if ((self.convert.infinity_norm(z) >= self.gamma1 - self.beta) or (self.convert.infinity_norm(r0) >= self.gamma2 - self.beta)): # main rejection loop terminates for else case here.
                z = None
                h = None
            # line 24: it's literally just an "else" statement.
            else:
                # line 25: multiply polynomial c_ntt [256] with matrix t0 [k][256] int NTT domain and apply NTT inverse.
                product_ct0 = [[0] * self.N for _ in range(self.k)] # initialize ct0
                for j in range(self.k): # temporary polynomial to store result of each multiplication in the loop.
                    temprary_list = self.ntt.MultiplyNTT(c_ntt, t0_cap[j])
                    for k in range(self.N): # take sum of all temporary polynomials.
                        product_ct0[j][k] = temprary_list[k] % self.q

                product_ct0_inv = [self.ntt.inv_NTT(p) for p in product_ct0] # NTT inverse function applied on temporary vector.

                # line 26 and 27: apply make hint componentwise everywehre to obtain vector binary polynomial h.
                h = [[0] * self.N for _ in range(self.k)] # initialize the empty vector.
                for i in range(self.k):
                    for j in range(self.N):
                        h[i][j] = self.operation.make_hint(-product_ct0_inv[i][j], w[i][j] - product_cs2_inv[i][j] + product_ct0_inv[i][j])
                        # print(h)
                # # line 28: reject if any of the 2 conditions is true.
                if (self.convert.infinity_norm(product_ct0_inv) >= self.gamma2 or self.convert.calc_ones(h) > self.omega):
                    z = None
                    h = None

            # line 31: increment counter        
            kappa = kappa + self.l
            
        # line 33: 
        sigma = self.encode.sig_encode(c_tilda, self.convert.centered_modulus(z), h)
        
        return sigma
    
    def ml_dsa_sign(self, private_key: bytes, Message, ctx:bytes) -> bytes:
        """
        Algorithm 2 FIPS 204

        Generates an ML-DSA signature over a message using the provided private key.
        Args:
            private_key (bytes): The private key bytestring.
            Message (bitstring): The message to be signed in bits.
            ctx (bytes): Context bytestring of length at most 255.
        Returns:
            signature (bytes): The generated ML-DSA signature as a bytestring.
        Raises:
            ValueError: If the private key or random seed is invalid.
            TypeError: If the message is not a bit string.
            ValueError: If the message has other than '0' and '1' characters.
            TypeError: If the context is not a bytestring.
            ValueError: If the context length is more than 255.
        """
        if not isinstance (private_key, (bytes, bytearray)):
            raise TypeError("Invalid private key format.")
        if not isinstance (Message, str):
            raise TypeError("Invalid message format.")
        if not all(bit in ('0', '1') for bit in Message):
            raise ValueError("Message must be a bit string.")
        if not isinstance(ctx, bytes):
            raise TypeError("Invalid context format.")
        if len(ctx) > 255:
            raise ValueError(f"ctx bytes must have length at most 255, ctx has length {len(ctx) = }")
        
        try:
            random_32_byte_seed = secrets.token_bytes(32) 
        except Exception as e:
            # return none and error indication.
            print(f"Error: Failed to generate random seed. {e}")
            return None
        Message_modified = self.convert.bytes_to_bits(self.convert.integer_to_bytes(0, 1) + self.convert.integer_to_bytes(len(ctx), 1) + ctx) + Message

        rho = self.ml_dsa_sign_internal(private_key, Message_modified, random_32_byte_seed)

        return rho

    def ml_dsa_verify_internal(self, public_key: bytes, message, signature: bytes) -> bool:
        """
        Algorithm 8 FIPS 204

        Internal function to verify a signature for a formatted message M'.
        Args:
            public_key (bytes): The public key bytestring.
            message (bitstring): The message in bits.
            signature (bytes): The signature bytestring.
        Returns:
            result (bool): True if the signature is valid, False otherwise.
        Raises:
            ValueError: If the public key or signature is invalid.
            TypeError: If the message is not a bit string.
            ValueError: If the message has other than '0' and '1' characters.
        """
        if not isinstance(public_key, bytes):
            raise ValueError("Invalid public key format.")
        if not isinstance (message, str):
            raise TypeError("Invalid message format.")
        if not all(bit in ('0', '1') for bit in message):
            raise ValueError("message must be a bit string.")
        if not isinstance(signature, bytes):
            raise ValueError("Invalid signature format.")

        rho, t1 = self.encode.pk_decode(public_key)

        c_tilda, z, h = self.encode.sig_decode(signature)

        if (h == None): 
            return False
        
        A_hat = self.sample.expand_A(rho)

        tr = self.convert.H(public_key, 64)

        mew = self.convert.H(self.convert.bits_to_bytes(self.convert.bytes_to_bits(tr) + message), 64)

        c = self.sample.SampleInBall(c_tilda)

        # a. Transform s₁ into the NTT domain
        z_ntt = [self.ntt.NTT(p) for p in z] 
            # b. Compute the matrix-vector product Â ◦ NTT(s₁)
        product_ntt = [[0] * self.N for _ in range(self.k)] # initialize product of A_cap and NTT(s1)
        for i in range(self.k):
            for j in range(self.l):
                temprary_list = self.ntt.MultiplyNTT(A_hat[i][j], z_ntt[j])
                for k in range(self.N):
                    product_ntt[i][k] = (product_ntt[i][k] + temprary_list[k]) % self.q

        c_ntt = self.ntt.NTT(c)
        d_on_pow_2 = [pow(2,self.d) for _ in range(self.N)]

        scalar_multiple = self.ntt.MultiplyNTT(c_ntt, d_on_pow_2)
        
        t1_ntt = [self.ntt.NTT(p) for p in t1] 

        product_2 = [[0 for _ in range(self.N)] for _ in range(self.k)]
        for i in range(len(t1)):
            product_2[i] = self.ntt.MultiplyNTT(scalar_multiple, t1_ntt[i])

        w_approx = [[0 for _ in range(self.N)] for _ in range(self.k)]
        
        for i in range(self.k):
            w_approx[i] = self.ntt.inv_NTT(self.ntt.SubNTT(product_ntt[i], product_2[i]))

        w1 = [[0 for _ in range(self.N)] for _ in range(self.k)]
        for i in range(self.k):
            for j in range(self.N):
                w1[i][j] = self.operation.use_hint(h[i][j], w_approx[i][j])
            
        c_hash_encoded = self.convert.H(mew + self.encode.w1_encode(w1), int(self._lambda_ / 4))
        
        return (self.convert.infinity_norm(z) < (self.gamma1 - self.beta)) and (c_hash_encoded == c_tilda)

    def ml_dsa_verify(self, public_key: bytes, message, signature: bytes, ctx: bytes) -> bool:
        """
        Algorithm 3 FIPS 204

        Verifies an ML-DSA signature over a message using the provided public key.
        Args:
            public_key (bytes): The public key bytestring.
            message (bitstring): The message in bits.
            signature (bytes): The signature bytestring.
            ctx (bytes): Context bytestring of length at most 255.
        Returns:
            bool: True if the signature is valid, False otherwise.
        Raises:
            ValueError: If the public key or signature is invalid.
            TypeError: If the context is not a bytestring.
        """
        if not isinstance(public_key, bytes):
            raise ValueError("Invalid public key format.")
        if not isinstance (message, str):
            raise TypeError("Invalid message format.")
        if not all(bit in ('0', '1') for bit in message):
            raise ValueError("message must be a bit string.")
        if not isinstance(signature, bytes):
            raise ValueError("Invalid signature format.")
        if not isinstance(ctx, bytes):
            raise TypeError("Invalid context format.")
        if len(ctx) > 255:
                raise ValueError(f"ctx bytes must have length at most 255, ctx has length {len(ctx) = }")

        Message_modified = self.convert.bytes_to_bits(self.convert.integer_to_bytes(0, 1) + self.convert.integer_to_bytes(len(ctx), 1) + ctx) + message
        
        return self.ml_dsa_verify_internal(public_key, Message_modified, signature)
    
