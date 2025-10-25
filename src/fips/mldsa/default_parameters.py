from .ml_dsa import MLDSA
from .hash_ml_dsa import HashMLDSA


DEFAULT_PARAMETERS = {
    "MLDSA_128": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 4, # no. of rows in A
        "l": 4, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 131072, # coefficient range of y
        "gamma2": 95232, # low order rounding range
        "_lambda_" : 128, # collision strength of c_tilda
        "tau": 39,  # number of ±1s in c
        "omega": 80,  # Max number of 1s in hint
    },
    "MLDSA_192": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 6, # no. of rows in A
        "l": 5, # no. of columns in A
        "eta": 4, # private key range
        "gamma1": 524288, # coefficient range of y
        "gamma2": 261888, # low order rounding range
        "_lambda_" : 192, # collision strength of c_tilda
        "tau": 49,  # number of ±1s in c
        "omega": 55,  # Max number of 1s in hint
    },
    "MLDSA_256": {
        "q": 8380417, # modulus
        "d": 13, # no. of dropped bits from t
        "N": 256, # size of each polynomial

        "k": 8, # no. of rows in A
        "l": 7, # no. of columns in A
        "eta": 2, # private key range
        "gamma1": 524288, # coefficient range of y
        "gamma2": 261888, # low order rounding range
        "_lambda_" : 256, # collision strength of c_tilda
        "tau": 60,  # number of ±1s in c
        "omega": 75,  # Max number of 1s in hint
    },
}

MLDSA_128 = MLDSA(DEFAULT_PARAMETERS["MLDSA_128"])
MLDSA_192 = MLDSA(DEFAULT_PARAMETERS["MLDSA_192"])
MLDSA_256 = MLDSA(DEFAULT_PARAMETERS["MLDSA_256"])

HASH_MLDSA_128_WITH_SHA512 = HashMLDSA(DEFAULT_PARAMETERS["MLDSA_128"])
HASH_MLDSA_192_WITH_SHA512 = HashMLDSA(DEFAULT_PARAMETERS["MLDSA_192"])
HASH_MLDSA_256_WITH_SHA512 = HashMLDSA(DEFAULT_PARAMETERS["MLDSA_256"])
