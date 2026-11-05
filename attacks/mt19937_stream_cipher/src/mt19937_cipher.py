#!/usr/bin/env python3
"""
Assignment 10 - Part A: MT19937 Stream Cipher & 16-Bit Seed Recovery Attack
CryptoLabX - Group 07
Primary Contributor (Part A): Kunal Sachan (2024ucp1547)
Collaborator: Yashwant Gour (2024ucp1732)

Description:
    This module implements a toy symmetric stream cipher based on the Mersenne Twister
    (MT19937) pseudo-random number generator (PRNG). It includes:
    1. Built-in MT19937 8-bit keystream generation and symmetric XOR encryption/decryption.
    2. Plaintext generation with a variable random prefix (5-20 printable chars) followed
       by 14 consecutive 'A' characters.
    3. Known-plaintext 16-bit seed brute-force recovery attack (testing all 65,536 seeds).
    4. Plaintext and seed verification logic.
    5. Pure-Python reference MT19937 generator for deep algorithmic analysis.
"""

import os
import sys
import time
import string
import random
from typing import Tuple, Optional, List


# =====================================================================
# 1. MT19937 Pure Python Reference Implementation (Educational)
# =====================================================================

class MT19937Pure:
    """
    Standard 32-bit Mersenne Twister (MT19937) algorithm reference.
    Parameters:
        w = 32 (word size)
        n = 624 (degree of recurrence)
        m = 397 (middle word)
        r = 31 (separation point / lower mask bit count)
        a = 0x9908B0DF (rational normal form twist matrix)
        u = 11, d = 0xFFFFFFFF (additional tempering shift/mask)
        s = 7,  b = 0x9D2C5680 (tempering bit shift/mask)
        t = 15, c = 0xEFC60000 (tempering bit shift/mask)
        l = 18 (tempering bit shift)
        f = 1812433253 (initialization multiplier)
    """
    W = 32
    N = 624
    M = 397
    R = 31
    A = 0x9908B0DF
    F = 1812433253
    U = 11
    D = 0xFFFFFFFF
    S = 7
    B = 0x9D2C5680
    T = 15
    C = 0xEFC60000
    L = 18
    LOWER_MASK = (1 << R) - 1        # 0x7FFFFFFF (31 lower bits)
    UPPER_MASK = (~LOWER_MASK) & 0xFFFFFFFF  # 0x80000000 (1 highest bit)

    def __init__(self, seed: int = 5489):
        self.mt: List[int] = [0] * self.N
        self.index: int = self.N
        self.seed(seed)

    def seed(self, seed: int) -> None:
        """Initialize generator from a 32-bit integer seed."""
        self.mt[0] = seed & 0xFFFFFFFF
        for i in range(1, self.N):
            self.mt[i] = (self.F * (self.mt[i - 1] ^ (self.mt[i - 1] >> (self.W - 2))) + i) & 0xFFFFFFFF
        self.index = self.N

    def twist(self) -> None:
        """Generate the next N values from the series."""
        for i in range(self.N):
            x = (self.mt[i] & self.UPPER_MASK) + (self.mt[(i + 1) % self.N] & self.LOWER_MASK)
            xA = x >> 1
            if x % 2 != 0:
                xA ^= self.A
            self.mt[i] = self.mt[(i + self.M) % self.N] ^ xA
        self.index = 0

    def extract_number(self) -> int:
        """Extract a tempered 32-bit integer."""
        if self.index >= self.N:
            self.twist()

        y = self.mt[self.index]
        self.index += 1

        # Tempering operations
        y ^= (y >> self.U) & self.D
        y ^= (y << self.S) & self.B
        y ^= (y << self.T) & self.C
        y ^= (y >> self.L)

        return y & 0xFFFFFFFF

    def extract_byte(self) -> int:
        """Extract one 8-bit value from generator."""
        # Extract lowest 8 bits of next random number
        return self.extract_number() & 0xFF


# =====================================================================
# 2. Built-in MT19937 Keystream & Stream Cipher Engine
# =====================================================================

def generate_keystream(seed: int, length: int) -> bytes:
    """
    Generate an 8-bit keystream of specified length using Python's built-in
    MT19937 PRNG (`random.Random`).
    
    Args:
        seed: Integer seed value.
        length: Number of keystream bytes to generate.
        
    Returns:
        bytes: Keystream of length `length`.
    """
    rng = random.Random(seed)
    return bytes(rng.getrandbits(8) for _ in range(length))


def mt19937_xor_cipher(data: bytes, seed: int) -> bytes:
    """
    Symmetric XOR stream cipher using MT19937 keystream.
    Since XOR is an involution (A ^ K ^ K = A), the exact same function
    performs both encryption and decryption.
    
    Args:
        data: Input bytes (plaintext for encryption, ciphertext for decryption).
        seed: PRNG seed value.
        
    Returns:
        bytes: Output bytes (ciphertext or recovered plaintext).
    """
    keystream = generate_keystream(seed, len(data))
    return bytes(b ^ k for b, k in zip(data, keystream))


def verify_cipher_roundtrip(test_message: bytes, seed: int) -> bool:
    """
    Verify that decrypt(encrypt(M)) == M using the same symmetric function.
    
    Args:
        test_message: Arbitrary byte message.
        seed: Seed integer.
        
    Returns:
        bool: True if decryption perfectly recovers original plaintext.
    """
    ciphertext = mt19937_xor_cipher(test_message, seed)
    decrypted = mt19937_xor_cipher(ciphertext, seed)
    return decrypted == test_message


# =====================================================================
# 3. Known-Plaintext Data Generation (5-20 prefix + 14 'A's)
# =====================================================================

def generate_target_plaintext(prefix_length: Optional[int] = None) -> Tuple[bytes, bytes, bytes]:
    """
    Generate plaintext with a random prefix of 5-20 printable characters
    followed by exactly 14 consecutive 'A' characters.
    
    Args:
        prefix_length: Optional fixed prefix length (5-20). If None, chosen randomly.
        
    Returns:
        Tuple of (full_plaintext, prefix, suffix_known)
    """
    if prefix_length is None:
        prefix_length = random.randint(5, 20)
    else:
        prefix_length = max(5, min(20, prefix_length))

    # Use printable ASCII characters for prefix
    charset = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    prefix = "".join(random.choice(charset) for _ in range(prefix_length)).encode("utf-8")
    suffix = b"A" * 14
    full_plaintext = prefix + suffix
    return full_plaintext, prefix, suffix


# =====================================================================
# 4. 16-Bit Seed Brute-Force Recovery Attack
# =====================================================================

def brute_force_16bit_seed(
    ciphertext: bytes,
    known_pattern: bytes = b"AAAAAAAAAAAAAA",
    max_seed: int = 0xFFFF
) -> Tuple[Optional[int], Optional[bytes], int, float]:
    """
    Exhaustively searches all 16-bit seeds (0 to 65535) to recover the seed
    used to generate ciphertext containing known_pattern.
    
    Args:
        ciphertext: Ciphertext bytes to attack.
        known_pattern: Known plaintext sequence (default: 14 'A' characters).
        max_seed: Maximum seed boundary (default: 65535 for 16-bit space).
        
    Returns:
        Tuple of:
            - recovered_seed (int or None)
            - recovered_plaintext (bytes or None)
            - total_seeds_tested (int)
            - elapsed_time_seconds (float)
    """
    total_seeds = max_seed + 1
    start_time = time.perf_counter()
    target_len = len(ciphertext)

    for candidate_seed in range(total_seeds):
        # Generate candidate keystream
        rng = random.Random(candidate_seed)
        candidate_keystream = bytes(rng.getrandbits(8) for _ in range(target_len))
        
        # Candidate decryption via XOR
        candidate_pt = bytes(c ^ k for c, k in zip(ciphertext, candidate_keystream))
        
        # Check if known sequence is present
        if known_pattern in candidate_pt:
            elapsed = time.perf_counter() - start_time
            return candidate_seed, candidate_pt, candidate_seed + 1, elapsed

    elapsed = time.perf_counter() - start_time
    return None, None, total_seeds, elapsed


# =====================================================================
# 5. Full Part A Demonstration Routine
# =====================================================================

def run_part_a_demonstration(verbose: bool = True) -> dict:
    """
    Execute complete Part A demonstration:
    1. Verifies encryption/decryption with sample message.
    2. Generates test plaintext with 5-20 random prefix + 14 'A's.
    3. Encrypts with random 16-bit seed.
    4. Brute-forces seed from ciphertext alone and verifies recovery.
    """
    logs = []
    def log(msg: str = ""):
        logs.append(msg)
        if verbose:
            print(msg)

    log("=" * 72)
    log("PART A: MT19937 STREAM CIPHER & WEAK 16-BIT SEED RECOVERY ATTACK")
    log("=" * 72)

    # Step 1 & 2: Verify Encryption and Decryption
    log("\n[Step 1 & 2] Verifying Symmetric Encryption / Decryption...")
    test_msg = b"CryptoLabX Group 07: Cryptographic Stream Cipher Verification Message 2026!"
    test_seed = 0xC001
    encrypted_msg = mt19937_xor_cipher(test_msg, test_seed)
    decrypted_msg = mt19937_xor_cipher(encrypted_msg, test_seed)
    
    assert decrypted_msg == test_msg, "Decryption failed to recover test message!"
    log(f"  Test Message       : {test_msg.decode('utf-8')}")
    log(f"  Test Seed          : 0x{test_seed:04X} ({test_seed})")
    log(f"  Ciphertext (Hex)   : {encrypted_msg.hex()[:64]}... ({len(encrypted_msg)} bytes)")
    log(f"  Decrypted Message  : {decrypted_msg.decode('utf-8')}")
    log("  [+] Status: Encryption and Decryption verified successfully!\n")

    # Step 3: Generate Plaintext with Random Prefix + 14 'A's and 16-bit Seed
    log("[Step 3] Generating Plaintext with Random Prefix (5-20 chars) + 14 'A's...")
    plaintext, prefix, suffix = generate_target_plaintext()
    actual_seed = random.randint(0, 0xFFFF)
    ciphertext = mt19937_xor_cipher(plaintext, actual_seed)

    log(f"  Random Prefix      : {prefix} (length = {len(prefix)})")
    log(f"  Known Suffix       : {suffix} (length = {len(suffix)})")
    log(f"  Full Plaintext     : {plaintext} (total length = {len(plaintext)})")
    log(f"  Plaintext (Hex)    : {plaintext.hex()}")
    log(f"  Chosen 16-bit Seed : 0x{actual_seed:04X} ({actual_seed})")
    log(f"  Ciphertext (Hex)   : {ciphertext.hex()}\n")

    # Step 4: Brute-Force 16-Bit Seed Recovery
    log("[Step 4] Launching 16-Bit Seed Brute-Force Attack...")
    log(f"  Search Space Size  : 2^16 = 65,536 candidate seeds (0x0000 - 0xFFFF)")
    log(f"  Target Signature   : 14 consecutive 'A' bytes (b'{suffix.decode('ascii')}')")
    
    recovered_seed, recovered_pt, tested_count, duration = brute_force_16bit_seed(
        ciphertext, known_pattern=suffix
    )

    log(f"  Seeds Tested       : {tested_count:,} / 65,536")
    log(f"  Time Elapsed       : {duration:.4f} seconds")
    if duration > 0:
        log(f"  Search Rate        : {tested_count / duration:,.0f} seeds/second")

    # Step 5: Verification of Recovered Seed and Plaintext
    log("\n[Step 5] Verifying Recovered Seed and Decrypted Plaintext...")
    if recovered_seed is not None and recovered_pt is not None:
        log(f"  [+] Recovered Seed : 0x{recovered_seed:04X} ({recovered_seed})")
        log(f"  [+] Expected Seed  : 0x{actual_seed:04X} ({actual_seed})")
        log(f"  [+] Recovered Text : {recovered_pt}")
        
        # Formal checks
        seed_match = (recovered_seed == actual_seed)
        text_match = (recovered_pt == plaintext)
        pattern_check = (suffix in recovered_pt)
        
        log(f"  - Seed Match Check          : {'PASSED' if seed_match else 'FAILED'}")
        log(f"  - Plaintext Match Check     : {'PASSED' if text_match else 'FAILED'}")
        log(f"  - Known Sequence Presence   : {'PASSED' if pattern_check else 'FAILED'}")
        
        success = seed_match and text_match and pattern_check
    else:
        log("  [-] ERROR: Failed to recover seed within 16-bit search space!")
        success = False

    log("=" * 72)
    log(f"PART A RESULT: {'SUCCESS' if success else 'FAILURE'}")
    log("=" * 72 + "\n")

    return {
        "success": success,
        "actual_seed": actual_seed,
        "recovered_seed": recovered_seed,
        "prefix": prefix,
        "plaintext": plaintext,
        "ciphertext": ciphertext,
        "duration": duration,
        "seeds_tested": tested_count,
        "log": "\n".join(logs)
    }


if __name__ == "__main__":
    result = run_part_a_demonstration(verbose=True)
    if not result["success"]:
        sys.exit(1)
