import secrets
random_message = secrets.token_bytes(500)

from fips.mldsa import MLDSA_256

pk , sk = MLDSA_256.ml_dsa_keygen()

print(len(pk), " ", len(sk))

signature = MLDSA_256.ml_dsa_sign(sk, MLDSA_256.convert.bytes_to_bits(random_message), b"abcb43524532")

print(len(signature))

print(MLDSA_256.ml_dsa_verify(pk, MLDSA_256.convert.bytes_to_bits(random_message), signature, b"abcb43524532"))
