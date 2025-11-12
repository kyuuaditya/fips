import secrets
random_message = secrets.token_bytes(500)

def corrupt_signature(sig: bytes) -> bytes:
    """Flips a bit in the signature to invalidate it."""
    if not sig:
        return b'\x00'
    
    # Flip a bit in the middle of the signature
    middle_index = len(sig) // 2
    mod_byte_val = sig[middle_index] ^ 0x01 # Flip the least significant bit
    mod_byte = bytes([mod_byte_val])

    return sig[:middle_index] + mod_byte + sig[middle_index + 1:]

from fips.mldsa import MLDSA_256

pk , sk = MLDSA_256.ml_dsa_keygen()

print("length public key: ",len(pk), ", length secret key: ", len(sk))

signature = MLDSA_256.ml_dsa_sign(sk, MLDSA_256.convert.bytes_to_bits(random_message), b"abcb43524532")

print("length signature: ", len(signature))

print(MLDSA_256.ml_dsa_verify(pk, MLDSA_256.convert.bytes_to_bits(random_message), signature, b"abcb43524532"))
