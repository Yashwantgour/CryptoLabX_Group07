#!/usr/bin/env python3
"""
Assignment 10 - Part B: Predictable Password Reset Tokens & Timestamp Attack
CryptoLabX - Group 07
Primary Contributor (Part B): Yashwant Gour (2024ucp1732)
Collaborator: Kunal Sachan (2024ucp1547)

Description:
    This module simulates an insecure password reset token service that uses MT19937
    seeded with the current Unix timestamp (in integer seconds).
    It demonstrates:
    1. Token generation: Recording Unix timestamp T, generating 16 consecutive 8-bit
       outputs via MT19937, and outputting the 16-byte token in hex.
    2. Token prediction attack: An attacker who intercepts/observes the token searches
       the plausible timestamp window [T - 300, T + 300] (or custom interval).
    3. Regeneration verification: Regenerating the token using the recovered timestamp
       to prove identical output.
    4. Entropy and search space analysis for timestamp-based PRNG seeds.
"""

import os
import sys
import time
import random
from typing import Tuple, Optional, List, Dict


def generate_reset_token(timestamp: Optional[int] = None) -> Tuple[int, bytes, str]:
    """
    Simulated Application Token Generator:
    Generates a 16-byte password reset token using MT19937 seeded with the
    current Unix timestamp (integer seconds).
    
    Args:
        timestamp: Optional explicit Unix timestamp. If None, records int(time.time()).
        
    Returns:
        Tuple of (timestamp, token_bytes, token_hex)
    """
    if timestamp is None:
        timestamp = int(time.time())

    # Seed MT19937 with the integer timestamp
    rng = random.Random(timestamp)
    
    # Generate 16 consecutive 8-bit outputs
    token_bytes = bytes(rng.getrandbits(8) for _ in range(16))
    token_hex = token_bytes.hex()
    
    return timestamp, token_bytes, token_hex


def predict_token_from_interval(
    observed_token: bytes,
    approximate_time: int,
    window_seconds: int = 300
) -> Tuple[Optional[int], int, float, List[Dict]]:
    """
    Simulated Attacker Token Predictor:
    Given an observed 16-byte reset token and an approximate time of generation,
    tests every timestamp candidate in [approximate_time - window_seconds, approximate_time + window_seconds].
    
    Args:
        observed_token: Intercepted 16-byte token.
        approximate_time: Attacker's estimate of generation timestamp.
        window_seconds: Search radius in seconds (default +/- 300s = 5 minutes).
        
    Returns:
        Tuple of:
            - recovered_timestamp (int or None)
            - total_candidates_tested (int)
            - elapsed_time_seconds (float)
            - sample_candidates (list of sample evaluations)
    """
    start_ts = approximate_time - window_seconds
    end_ts = approximate_time + window_seconds
    total_candidates = end_ts - start_ts + 1

    sample_candidates = []
    start_bench = time.perf_counter()
    recovered_timestamp = None
    tested_count = 0

    for cand_ts in range(start_ts, end_ts + 1):
        tested_count += 1
        rng = random.Random(cand_ts)
        candidate_token = bytes(rng.getrandbits(8) for _ in range(16))

        # Store first 3 and last 3 candidate evaluations as sample telemetry
        if tested_count <= 3 or tested_count >= total_candidates - 2:
            sample_candidates.append({
                "candidate_timestamp": cand_ts,
                "token_hex": candidate_token.hex(),
                "match": (candidate_token == observed_token)
            })

        if candidate_token == observed_token:
            recovered_timestamp = cand_ts
            break

    elapsed = time.perf_counter() - start_bench
    return recovered_timestamp, tested_count, elapsed, sample_candidates


def verify_recovered_token(recovered_timestamp: int, original_token: bytes) -> bool:
    """
    Regenerates the token with the recovered timestamp to verify full byte match.
    
    Args:
        recovered_timestamp: The recovered seed timestamp.
        original_token: The original intercepted token.
        
    Returns:
        bool: True if regenerated token strictly equals the original token.
    """
    _, regenerated_token, _ = generate_reset_token(recovered_timestamp)
    return regenerated_token == original_token


def run_part_b_demonstration(
    custom_offset_seconds: int = 42,
    window_seconds: int = 300,
    verbose: bool = True
) -> dict:
    """
    Execute full Part B demonstration according to assignment requirements 6 to 11.
    
    Args:
        custom_offset_seconds: Simulated delay between token generation and attack start.
        window_seconds: Search radius (+/- seconds).
        verbose: Print human-readable logs to stdout.
    """
    logs = []
    def log(msg: str = ""):
        logs.append(msg)
        if verbose:
            print(msg)

    log("=" * 72)
    log("PART B: PREDICTABLE PASSWORD RESET TOKENS & TIMESTAMP ATTACK")
    log("=" * 72)

    # Step 6, 7 & 8: Token Generation
    log("\n[Step 6-8] Simulated Application Token Generation...")
    # Simulate a realistic current Unix timestamp
    current_time = int(time.time())
    # Allow token to have been generated slightly in the past
    actual_t = current_time - custom_offset_seconds
    _, token_bytes, token_hex = generate_reset_token(actual_t)

    log(f"  Recorded Timestamp (T) : {actual_t} (Unix Epoch Seconds)")
    log(f"  Formatted Date / Time  : {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(actual_t))}")
    log(f"  PRNG Seed Used         : {actual_t}")
    log(f"  Generated Token (Hex)  : {token_hex}")
    log(f"  Token Byte Length      : {len(token_bytes)} bytes (128 bits)")

    # Step 9 & 10: Token Prediction Attack
    log("\n[Step 9 & 10] Attacker Intercepts Token and Initiates Interval Attack...")
    # Attacker knows token was generated approximately around 'current_time'
    search_center = current_time
    interval_start = search_center - window_seconds
    interval_end = search_center + window_seconds
    total_interval_span = interval_end - interval_start + 1

    log(f"  Intercepted Token      : {token_hex}")
    log(f"  Attacker Time Reference: {search_center}")
    log(f"  Search Interval Bounds : [{interval_start}, {interval_end}]")
    log(f"  Search Interval Radius : +/- {window_seconds} seconds")
    log(f"  Total Candidates in Win: {total_interval_span} candidate seeds")

    recovered_t, candidates_tested, duration, samples = predict_token_from_interval(
        token_bytes, approximate_time=search_center, window_seconds=window_seconds
    )

    # Step 11: Report Results and Verify Match
    log("\n[Step 11] Attack Results & Regeneration Verification...")
    log(f"  Candidates Tested      : {candidates_tested} / {total_interval_span}")
    log(f"  Elapsed Search Time    : {duration * 1000:.3f} ms ({duration:.6f} seconds)")
    if duration > 0:
        log(f"  Cracking Throughput    : {candidates_tested / duration:,.0f} candidate tokens/second")

    if recovered_t is not None:
        log(f"  [+] Recovered Timestamp: {recovered_t}")
        log(f"  [+] Actual Timestamp   : {actual_t}")
        
        # Verify regeneration
        is_verified = verify_recovered_token(recovered_t, token_bytes)
        _, regen_token, regen_hex = generate_reset_token(recovered_t)
        
        log(f"  Regenerated Token (Hex): {regen_hex}")
        log(f"  Exact Byte-for-Byte    : {'VERIFIED MATCH' if is_verified else 'MISMATCH'}")
        success = (recovered_t == actual_t) and is_verified
    else:
        log("  [-] ERROR: No matching timestamp found within interval!")
        success = False

    log("\n" + "=" * 72)
    log(f"PART B RESULT: {'SUCCESS' if success else 'FAILURE'}")
    log("=" * 72 + "\n")

    return {
        "success": success,
        "actual_timestamp": actual_t,
        "recovered_timestamp": recovered_t,
        "token_hex": token_hex,
        "candidates_tested": candidates_tested,
        "total_interval_span": total_interval_span,
        "duration": duration,
        "samples": samples,
        "log": "\n".join(logs)
    }


if __name__ == "__main__":
    result = run_part_b_demonstration(verbose=True)
    if not result["success"]:
        sys.exit(1)
