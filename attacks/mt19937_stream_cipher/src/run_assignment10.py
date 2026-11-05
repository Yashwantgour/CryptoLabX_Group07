#!/usr/bin/env python3
"""
Assignment 10: MT19937 Stream Cipher and Predictable Token Attack
CryptoLabX - Group 07
Authors:
    - Yashwant Gour (Roll No: 2024ucp1732, Email: 2024ucp1732@mnit.ac.in)
    - Kunal Sachan (Roll No: 2024ucp1547, Email: 2024ucp1547@mnit.ac.in)

Description:
    Unified runner and demonstration suite for Assignment 10.
    Executes:
        - Part A: MT19937 Stream Cipher & 16-Bit Seed Brute-Force Recovery
        - Part B: Predictable Password Reset Tokens & Interval Timestamp Attack
        - Automated Verification & Output Artifact Generation
"""

import os
import sys
import argparse
import time

# Ensure local imports work cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from mt19937_cipher import run_part_a_demonstration
from password_reset_token import run_part_b_demonstration


def main():
    parser = argparse.ArgumentParser(
        description="Assignment 10: MT19937 Stream Cipher & Predictable Token Attack Suite"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "part_a", "part_b"],
        default="all",
        help="Which section of Assignment 10 to execute (default: all)"
    )
    parser.add_argument(
        "--save-logs",
        action="store_true",
        default=True,
        help="Automatically save demonstration outputs to outputs/ folder"
    )
    args = parser.parse_args()

    output_dir = os.path.join(os.path.dirname(CURRENT_DIR), "outputs")
    os.makedirs(output_dir, exist_ok=True)

    header = []
    header.append("=" * 80)
    header.append("      CRYPTOGRAPHY LAB ASSIGNMENT 10: MT19937 PRNG CRYPTANALYSIS")
    header.append("                  Group 07 - MNIT Jaipur (22CPP307)")
    header.append("  Team: Kunal Sachan (2024ucp1547) & Yashwant Gour (2024ucp1732)")
    header.append("=" * 80)
    print("\n".join(header))

    combined_logs = list(header)
    all_success = True

    if args.mode in ["all", "part_a"]:
        res_a = run_part_a_demonstration(verbose=True)
        combined_logs.append("\n" + res_a["log"])
        if not res_a["success"]:
            all_success = False

    if args.mode in ["all", "part_b"]:
        res_b = run_part_b_demonstration(verbose=True)
        combined_logs.append("\n" + res_b["log"])
        if not res_b["success"]:
            all_success = False

    combined_text = "\n".join(combined_logs)

    if args.save_logs:
        full_log_path = os.path.join(output_dir, "full_demonstration_output.txt")
        with open(full_log_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        print(f"[+] Complete demonstration output written to: {full_log_path}")

    summary_banner = [
        "",
        "*" * 80,
        f"  ASSIGNMENT 10 OVERALL SUITE STATUS: {'ALL TESTS PASSED' if all_success else 'TESTS FAILED'}",
        "*" * 80,
        ""
    ]
    print("\n".join(summary_banner))

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
