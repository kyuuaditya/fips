from fips.mldsa import MLDSA_192 as fips
import secrets
import random

import time
elapsed_time = 0

# complete test
public_key, private_key = fips.ml_dsa_keygen()
print ("public key size: ", len(public_key))
print ("private key size: ", len(private_key))

passed = 0
number_of_experiments = 100
total_signature_size = 0

for _ in range(number_of_experiments):
    message_size = random.randint(1, 1000)
    random_message = secrets.token_bytes(message_size)

    start_time = time.perf_counter()
    signature = fips.ml_dsa_sign(private_key, fips.convert.bytes_to_bits(random_message), b"abcb43524532")
    end_time = time.perf_counter()
    elapsed_time += (end_time - start_time)

    verification_check = fips.ml_dsa_verify(public_key, fips.convert.bytes_to_bits(random_message), signature, b"abcb43524532")
    total_signature_size += len(signature)
    if verification_check == True: 
        passed += 1
print("average signature size: ", int(total_signature_size / number_of_experiments))
print("passed: ",passed, " out of ", number_of_experiments)

average_sign_time = elapsed_time / number_of_experiments
print(f"Average sign time: {average_sign_time:.6f} seconds")
