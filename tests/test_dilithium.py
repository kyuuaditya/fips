import unittest
import random
import secrets
from fips.mldsa import MLDSA_128, MLDSA_192, MLDSA_256

class TestDilithium(unittest.TestCase):
    """
    Test Dilithium for internal
    consistency by generating signatures
    and verifying them!
    """

    def generic_test_dilithium(self, Dilithium):
        msg = b"Signed by dilithium" + secrets.token_bytes(random.randint(1, 1000))

        # Perform signature process
        pk, sk = Dilithium.ml_dsa_keygen()
        sig = Dilithium.ml_dsa_sign(sk, Dilithium.convert.bytes_to_bits(msg), b"random context byte string")
        check_verify = Dilithium.ml_dsa_verify(pk, Dilithium.convert.bytes_to_bits(msg), sig, b"random context byte string")

        # Generate some fail cases
        pk_bad, _ = Dilithium.ml_dsa_keygen()
        check_wrong_pk = Dilithium.ml_dsa_verify(pk_bad, Dilithium.convert.bytes_to_bits(msg), sig, b"random context byte string")
        check_wrong_msg = Dilithium.ml_dsa_verify(pk, Dilithium.convert.bytes_to_bits(b"wrong message"), sig, b"random context byte string")

        # Check that signature works
        self.assertTrue(check_verify)
        # Check changing the key breaks verify
        self.assertFalse(check_wrong_pk)
        # Check changing the message breaks verify
        self.assertFalse(check_wrong_msg)

    def test_dilithium2(self):
        for _ in range(5):
            self.generic_test_dilithium(MLDSA_128)

    def test_dilithium3(self):
        for _ in range(5):
            self.generic_test_dilithium(MLDSA_192)

    def test_dilithium5(self):
        for _ in range(5):
            self.generic_test_dilithium(MLDSA_256)

if __name__ == "__main__":
    unittest.main()
