# import json
# from fips.mldsa import MLDSA_128, MLDSA_192, MLDSA_256

# def run_kat_tests(json_filename: str):
#     """
#     Loads, parses, and executes the KAT tests from a JSON file.
#     """
#     try:
#         with open(json_filename, 'r') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print(f"FATAL: JSON file not found at '{json_filename}'")
#         return
#     except json.JSONDecodeError:
#         print(f"FATAL: Could not decode JSON from '{json_filename}'. Check for syntax errors.")
#         return

#     print(f"Starting KAT tests for {data.get('algorithm', 'N/A')} - {data.get('mode', 'N/A')}")
    
#     total_tests = 0
#     passed_tests = 0

#     # Navigate the JSON structure
#     for group in data.get('testGroups', []):
#         group_id = group.get('tgId', 'N/A')
#         param_set = group.get('parameterSet', 'N/A')
#         print(f"\n--- Testing Group {group_id} ({param_set}) ---")
        
#         for test in group.get('tests', []):
#             total_tests += 1
#             tc_id = test.get('tcId', 'N/A')
            
#             try:
#                 # 1. Extract hex strings from JSON
#                 seed_hex = test['seed']
#                 expected_pk_hex = test['pk']
#                 expected_sk_hex = test['sk']
                
#                 # 2. Convert hex strings to raw bytes
#                 seed_bytes = bytes.fromhex(seed_hex)
#                 expected_pk_bytes = bytes.fromhex(expected_pk_hex)
#                 expected_sk_bytes = bytes.fromhex(expected_sk_hex)
                
#                 # 3. Call your implementation
#                 if group_id == 1:
#                     (generated_pk, generated_sk) = MLDSA_128.ml_dsa_keygen_internal(seed_bytes)
#                 elif group_id == 2:
#                     (generated_pk, generated_sk) = MLDSA_192.ml_dsa_keygen_internal(seed_bytes)
#                 elif group_id == 3:
#                     (generated_pk, generated_sk) = MLDSA_256.ml_dsa_keygen_internal(seed_bytes)
#                 else:
#                     raise ValueError(f"invalid group_id in {json_filename}")

#                 # 4. Compare results
#                 is_pk_match = (generated_pk == expected_pk_bytes)
#                 is_sk_match = (generated_sk == expected_sk_bytes)
                
#                 if is_pk_match and is_sk_match:
#                     print(f"[TCID: {tc_id}] - PASS")
#                     passed_tests += 1
#                 else:
#                     print(f"[TCID: {tc_id}] - FAIL")
#                     if not is_pk_match:
#                         print(f"  Mismatch: Public Key (pk)")
#                         # Uncomment for detailed debugging
#                         # print(f"    Expected: {expected_pk_bytes.hex()}")
#                         # print(f"    Got:      {generated_pk.hex()}")
#                     if not is_sk_match:
#                         print(f"  Mismatch: Secret Key (sk)")
#                         # Uncomment for detailed debugging
#                         # print(f"    Expected: {expected_sk_bytes.hex()}")
#                         # print(f"    Got:      {generated_sk.hex()}")

#             except (KeyError, TypeError) as e:
#                 print(f"[TCID: {tc_id}] - ERROR: Test vector is malformed. {e}")
#             except ValueError as e:
#                 print(f"[TCID: {tc_id}] - ERROR: Failed to decode hex string. {e}")
#             except Exception as e:
#                 print(f"[TCID: {tc_id}] - ERROR: Your function failed. {e}")

#     # --- Final Summary ---
#     print("\n" + "="*30)
#     print("      Test Summary")
#     print("="*30)
#     print(f"  Total Tests: {total_tests}")
#     print(f"  Passed:      {passed_tests}")
#     print(f"  Failed:      {total_tests - passed_tests}")
#     print("="*30)

# if __name__ == "__main__":
#     # --- CONFIGURATION ---
#     # Change this to the path of your test vector file
#     JSON_FILE_PATH = "././assets/ML-DSA-keyGen-FIPS204/internalProjection.json" 
    
#     run_kat_tests(JSON_FILE_PATH)

# import pytest
# import json
# from fips.mldsa import MLDSA_128, MLDSA_192, MLDSA_256

# # --- CONFIGURATION ---
# # Path from your original script
# JSON_FILE_PATH = "././assets/ML-DSA-keyGen-FIPS204/internalProjection.json"

# def load_kat_test_cases():
#     """
#     Loads and flattens the test cases from the JSON file
#     for pytest parameterization.
#     """
#     try:
#         with open(JSON_FILE_PATH, 'r') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         # Exit pytest with a clear error if the file is missing
#         pytest.exit(f"FATAL: JSON file not found at '{JSON_FILE_PATH}'")
#     except json.JSONDecodeError:
#         pytest.exit(f"FATAL: Could not decode JSON from '{JSON_FILE_PATH}'. Check syntax.")
    
#     test_cases = []
    
#     # Navigate the JSON structure, same as your script
#     for group in data.get('testGroups', []):
#         group_id = group.get('tgId')
#         param_set = group.get('parameterSet', 'UnknownParamSet')
        
#         # Critical check: group_id drives the logic
#         if group_id is None:
#             print(f"WARNING: Skipping a testGroup with no 'tgId' in {JSON_FILE_PATH}")
#             continue

#         for test in group.get('tests', []):
#             tc_id = test.get('tcId', 'UnknownTCID')
            
#             # Ensure the required keys exist before adding the test
#             if not all(k in test for k in ('seed', 'pk', 'sk')):
#                 print(f"WARNING: Skipping TCID {tc_id} in group {group_id} due to missing keys.")
#                 continue
                
#             # Use pytest.param to create readable test IDs in the output
#             # (e.g., "test_mldsa_keygen[ML-DSA-44-TCID-1]")
#             test_cases.append(pytest.param(
#                 group_id, 
#                 test, 
#                 id=f"{param_set}-TCID-{tc_id}"
#             ))
    
#     if not test_cases:
#         pytest.exit(f"No valid test cases were found in {JSON_FILE_PATH}")
        
#     return test_cases

# # --- Pytest Parameterized Test ---

# @pytest.mark.parametrize("group_id, test", load_kat_test_cases())
# def test_mldsa_keygen_internal(group_id, test):
#     """
#     Runs a single KeyGen KAT test vector pulled from the JSON file.
#     Each vector is run as a separate, individual test.
#     """
#     try:
#         # 1. & 2. Extract and decode hex strings
#         seed_bytes = bytes.fromhex(test['seed'])
#         expected_pk_bytes = bytes.fromhex(test['pk'])
#         expected_sk_bytes = bytes.fromhex(test['sk'])
#     except (KeyError, ValueError) as e:
#         # Fail this specific test if data is bad
#         pytest.fail(f"Test vector parsing error for TCID {test.get('tcId')}: {e}")
#         return

#     # 3. Call your implementation
#     # This logic is identical to your original script
#     if group_id == 1:
#         (generated_pk, generated_sk) = MLDSA_128.ml_dsa_keygen_internal(seed_bytes)
#     elif group_id == 2:
#         (generated_pk, generated_sk) = MLDSA_192.ml_dsa_keygen_internal(seed_bytes)
#     elif group_id == 3:
#         (generated_pk, generated_sk) = MLDSA_256.ml_dsa_keygen_internal(seed_bytes)
#     else:
#         pytest.fail(f"Invalid group_id '{group_id}' for TCID {test.get('tcId')}. No function to call.")
#         return

#     # 4. Compare results using pytest's assert
#     # This provides much more detailed failure info (a diff)
#     # than your original print statements.
#     assert generated_pk == expected_pk_bytes, "Public Key (pk) mismatch"
#     assert generated_sk == expected_sk_bytes, "Secret Key (sk) mismatch"



import pytest
import json
from fips.mldsa import MLDSA_128, MLDSA_192, MLDSA_256

# --- CONFIGURATION ---
JSON_FILE_PATH = "././assets/ML-DSA-keyGen-FIPS204/internalProjection.json"

@pytest.fixture(scope="module")
def kat_groups():
    """
    Loads and groups all test cases by their 'tgId' (1, 2, or 3).
    This fixture runs only once per test session.
    """
    try:
        with open(JSON_FILE_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pytest.exit(f"FATAL: JSON file not found at '{JSON_FILE_PATH}'")
    except json.JSONDecodeError:
        pytest.exit(f"FATAL: Could not decode JSON from '{JSON_FILE_PATH}'. Check syntax.")
    
    groups = {1: [], 2: [], 3: []}
    
    for group in data.get('testGroups', []):
        group_id = group.get('tgId')
        
        if group_id in groups:
            for test in group.get('tests', []):
                # Ensure the required keys exist before adding the test
                if all(k in test for k in ('tcId', 'seed', 'pk', 'sk')):
                    groups[group_id].append(test)
                else:
                    print(f"WARNING: Skipping a test in group {group_id} due to missing keys.")
        else:
            print(f"WARNING: Skipping unknown group_id: {group_id}")
            
    return groups

def _run_test_group(test_cases, keygen_function):
    """
    Helper function to run all tests in a list and collect failures.
    This prevents the test from stopping on the first failure.
    """
    failures = []
    
    for test in test_cases:
        tc_id = test['tcId']
        try:
            # 1. & 2. Extract and decode hex strings
            seed_bytes = bytes.fromhex(test['seed'])
            expected_pk_bytes = bytes.fromhex(test['pk'])
            expected_sk_bytes = bytes.fromhex(test['sk'])
            
            # 3. Call the specific implementation
            (generated_pk, generated_sk) = keygen_function(seed_bytes)

            # 4. Compare results
            if generated_pk != expected_pk_bytes:
                failures.append(f"[TCID: {tc_id}] Public Key (pk) mismatch")
            if generated_sk != expected_sk_bytes:
                failures.append(f"[TCID: {tc_id}] Secret Key (sk) mismatch")

        except (KeyError, ValueError, TypeError) as e:
            failures.append(f"[TCID: {tc_id}] Test vector parsing error: {e}")
        except Exception as e:
            failures.append(f"[TCID: {tc_id}] Function call failed: {e}")

    return failures

# --- The 3 Test Functions You Requested ---

def test_mldsa_group_1_dsa44(kat_groups):
    """
    Runs all ML-DSA-44 (group_id 1) test cases as a single test.
    """
    test_cases = kat_groups.get(1)
    if not test_cases:
        pytest.skip("No test cases found for group 1 (ML-DSA-44)")
    
    failures = _run_test_group(test_cases, MLDSA_128.ml_dsa_keygen_internal)
    
    # Assert at the very end
    assert not failures, f"Found {len(failures)} failures in ML-DSA-44:\n  " + "\n  ".join(failures)

def test_mldsa_group_2_dsa65(kat_groups):
    """
    Runs all ML-DSA-65 (group_id 2) test cases as a single test.
    """
    test_cases = kat_groups.get(2)
    if not test_cases:
        pytest.skip("No test cases found for group 2 (ML-DSA-65)")

    failures = _run_test_group(test_cases, MLDSA_192.ml_dsa_keygen_internal)
    
    # Assert at the very end
    assert not failures, f"Found {len(failures)} failures in ML-DSA-65:\n  " + "\n  ".join(failures)

def test_mldsa_group_3_dsa87(kat_groups):
    """
    Runs all ML-DSA-87 (group_id 3) test cases as a single test.
    """
    test_cases = kat_groups.get(3)
    if not test_cases:
        pytest.skip("No test cases found for group 3 (ML-DSA-87)")

    failures = _run_test_group(test_cases, MLDSA_256.ml_dsa_keygen_internal)
    
    # Assert at the very end
    assert not failures, f"Found {len(failures)} failures in ML-DSA-87:\n  " + "\n  ".join(failures)