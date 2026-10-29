#!/usr/bin/env python3
"""
Cryptographic Random Number Generator (RNG) Statistical Analysis Toolkit
CryptoLabX - Lab 7: OS Random-Number Generation (RNG) Evaluation
Group 07: Yashwant Gour (2024ucp1732), Kunal Sachan (2024ucp1547)

Tasks Implemented:
- Task 2: Byte-frequency distribution, bit distribution, repeated patterns, serial correlations.
- Task 3: Statistical tests (NIST Monobit, NIST Runs Test, Chi-Square Goodness-of-Fit, Shannon Entropy).
"""

import os
import sys
import math
import time
import csv
from collections import Counter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# --- Mathematical Helper Functions (Pure Python, No external dependencies) ---

def gammp(a, x):
    """Incomplete gamma function P(a, x) = gamma(a, x) / Gamma(a)"""
    if x < 0.0 or a <= 0.0:
        return 0.0
    if x < a + 1.0:
        # Series expansion
        ap = a
        sum_val = 1.0 / a
        del_val = sum_val
        for _ in range(1, 1000):
            ap += 1.0
            del_val *= x / ap
            sum_val += del_val
            if abs(del_val) < abs(sum_val) * 1e-15:
                break
        return sum_val * math.exp(-x + a * math.log(x) - math.lgamma(a))
    else:
        # Continued fraction representation for Q(a, x) = 1 - P(a, x)
        b = x + 1.0 - a
        c = 1.0 / 1e-30
        d = 1.0 / b
        h = d
        for i in range(1, 1000):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            del_val = d * c
            h *= del_val
            if abs(del_val - 1.0) < 1e-15:
                break
        gammq = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
        return 1.0 - gammq

def chi2_survival(x, df):
    """Chi-square survival function (p-value): Q(df/2, x/2)"""
    if x <= 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - gammp(df / 2.0, x / 2.0)))

# --- Core Analysis Engine ---

class RNGAnalysisResult:
    def __init__(self, filename, filepath, data):
        self.filename = filename
        self.filepath = filepath
        self.total_bytes = len(data)
        self.total_bits = self.total_bytes * 8
        
        # 1. Byte-Frequency Distribution
        self.byte_counts = [0] * 256
        for b in data:
            self.byte_counts[b] += 1
            
        self.expected_byte_freq = self.total_bytes / 256.0
        self.min_byte_freq = min(self.byte_counts)
        self.max_byte_freq = max(self.byte_counts)
        self.mean_byte_freq = sum(self.byte_counts) / 256.0
        self.variance_byte_freq = sum((c - self.mean_byte_freq) ** 2 for c in self.byte_counts) / 256.0
        self.std_dev_byte_freq = math.sqrt(self.variance_byte_freq)
        self.theoretical_std_dev = math.sqrt(self.total_bytes * (1.0 / 256.0) * (255.0 / 256.0))
        
        # 2. Chi-Square Goodness-of-Fit Test (Byte Distribution)
        self.chi_square = sum(((c - self.expected_byte_freq) ** 2) / self.expected_byte_freq for c in self.byte_counts)
        self.chi_df = 255
        self.chi_critical_val_05 = 293.25 # critical value for df=255 at alpha=0.05
        self.chi_p_value = chi2_survival(self.chi_square, self.chi_df)
        self.chi_verdict = "PASS (Uniform)" if self.chi_p_value >= 0.01 else "FAIL (Non-uniform)"
        
        # 3. Shannon Entropy
        entropy = 0.0
        for c in self.byte_counts:
            if c > 0:
                p = c / float(self.total_bytes)
                entropy -= p * math.log2(p)
        self.entropy = entropy
        self.entropy_ideal = 8.000000
        
        # 4. Bit Distribution & Monobit Frequency Test (NIST SP 800-22)
        bit_counts_lookup = [bin(i).count('1') for i in range(256)]
        self.ones_count = sum(bit_counts_lookup[b] for b in data)
        self.zeros_count = self.total_bits - self.ones_count
        self.prop_ones = self.ones_count / float(self.total_bits)
        
        # NIST Monobit Test Statistic
        diff = abs(self.ones_count - self.zeros_count)
        self.monobit_s_obs = diff / math.sqrt(self.total_bits)
        self.monobit_p_value = math.erfc(self.monobit_s_obs / math.sqrt(2))
        self.monobit_verdict = "PASS (Random)" if self.monobit_p_value >= 0.01 else "FAIL (Biased)"
        
        # 5. Runs Test (NIST SP 800-22)
        transitions_lookup = [sum(((i >> j) & 1) != ((i >> (j + 1)) & 1) for j in range(7)) for i in range(256)]
        v_obs = 1 + sum(transitions_lookup[b] for b in data)
        for i in range(len(data) - 1):
            if (data[i] & 1) != ((data[i+1] >> 7) & 1):
                v_obs += 1
        self.runs_count = v_obs
        
        pi = self.prop_ones
        if abs(pi - 0.5) >= (2.0 / math.sqrt(self.total_bits)):
            self.runs_p_value = 0.0
            self.runs_verdict = "FAIL (Pre-test failed)"
        else:
            numerator = abs(v_obs - 2.0 * self.total_bits * pi * (1.0 - pi))
            denominator = 2.0 * math.sqrt(2.0 * self.total_bits) * pi * (1.0 - pi)
            self.runs_z = numerator / denominator if denominator > 0 else 0.0
            self.runs_p_value = math.erfc(self.runs_z)
            self.runs_verdict = "PASS (Random)" if self.runs_p_value >= 0.01 else "FAIL (Non-random)"
            
        # 6. Serial Correlation (Lag-1 Autocorrelation of Bytes)
        mean_byte = sum(data) / float(self.total_bytes)
        var_byte = sum((b - mean_byte) ** 2 for b in data) / float(self.total_bytes)
        cov_byte = sum((data[i] - mean_byte) * (data[i+1] - mean_byte) for i in range(self.total_bytes - 1)) / float(self.total_bytes - 1)
        self.serial_corr_r1 = cov_byte / var_byte if var_byte > 0 else 0.0
        self.serial_corr_threshold = 2.0 / math.sqrt(self.total_bytes)
        self.serial_corr_verdict = "PASS (Uncorrelated)" if abs(self.serial_corr_r1) < self.serial_corr_threshold else "FAIL (Correlated)"
        
        # 7. Repeated Patterns Analysis (2-byte and 4-byte block collisions)
        blocks_2b = [data[i:i+2] for i in range(0, self.total_bytes - 1, 2)]
        counts_2b = Counter(blocks_2b)
        self.patterns_2b_total = len(blocks_2b)
        self.patterns_2b_unique = len(counts_2b)
        self.patterns_2b_max_occurrences = max(counts_2b.values())
        
        blocks_4b = [data[i:i+4] for i in range(0, self.total_bytes - 3, 4)]
        counts_4b = Counter(blocks_4b)
        self.patterns_4b_total = len(blocks_4b)
        self.patterns_4b_unique = len(counts_4b)
        self.patterns_4b_collisions = self.patterns_4b_total - self.patterns_4b_unique
        # Theoretical birthday paradox collisions for 262,144 blocks of 2^32: n*(n-1)/(2*2^32) ≈ 8.00
        self.patterns_4b_expected_collisions = (self.patterns_4b_total * (self.patterns_4b_total - 1)) / (2.0 * (2 ** 32))

def analyze_file(filepath):
    """Load binary data and run analysis"""
    if not os.path.exists(filepath):
        print(f"[-] Error: File not found: {filepath}")
        return None
    with open(filepath, "rb") as f:
        data = f.read()
    filename = os.path.basename(filepath)
    return RNGAnalysisResult(filename, filepath, data)

def print_single_report(res: RNGAnalysisResult):
    """Display comprehensive report for a single dataset"""
    print("\n" + "=" * 75)
    print(f" STATISTICAL RNG EVALUATION REPORT: {res.filename}")
    print("=" * 75)
    print(f" File Path           : {res.filepath}")
    print(f" Sample Size         : {res.total_bytes:,} bytes ({res.total_bits:,} bits)")
    print("-" * 75)
    
    print(" 1. BYTE FREQUENCY DISTRIBUTION (Task 2 & 3)")
    print(f"    Expected Frequency per Byte : {res.expected_byte_freq:.1f}")
    print(f"    Observed Min Frequency      : {res.min_byte_freq}")
    print(f"    Observed Max Frequency      : {res.max_byte_freq}")
    print(f"    Mean Frequency              : {res.mean_byte_freq:.2f}")
    print(f"    Standard Deviation (Obs)    : {res.std_dev_byte_freq:.2f} (Theoretical: ~{res.theoretical_std_dev:.2f})")
    print(f"    Chi-Square Statistic (df=255): {res.chi_square:.2f} (Critical @ alpha=0.05: {res.chi_critical_val_05:.2f})")
    print(f"    Chi-Square P-value          : {res.chi_p_value:.6f}")
    print(f"    Uniformity Test Verdict     : {res.chi_verdict}")
    print("-" * 75)
    
    print(" 2. SHANNON ENTROPY (Task 3)")
    print(f"    Calculated Entropy          : {res.entropy:.6f} bits/byte")
    print(f"    Theoretical Maximum         : {res.entropy_ideal:.6f} bits/byte")
    print(f"    Entropy Percentage          : {(res.entropy / res.entropy_ideal) * 100:.4f}%")
    print("-" * 75)
    
    print(" 3. BIT DISTRIBUTION & NIST MONOBIT TEST (Task 2 & 3)")
    print(f"    Count of 0s                 : {res.zeros_count:,} ({((res.zeros_count/res.total_bits)*100):.3f}%)")
    print(f"    Count of 1s                 : {res.ones_count:,} ({((res.ones_count/res.total_bits)*100):.3f}%)")
    print(f"    Proportion of Ones (pi)     : {res.prop_ones:.6f} (Ideal: 0.500000)")
    print(f"    Monobit Test Statistic S_obs: {res.monobit_s_obs:.4f}")
    print(f"    Monobit Test P-value        : {res.monobit_p_value:.6f}")
    print(f"    Monobit Test Verdict        : {res.monobit_verdict}")
    print("-" * 75)
    
    print(" 4. NIST RUNS TEST FOR BIT SEQUENCES (Task 3)")
    print(f"    Observed Total Runs V_obs   : {res.runs_count:,}")
    print(f"    Expected Total Runs         : {int(2 * res.total_bits * res.prop_ones * (1 - res.prop_ones)):,}")
    print(f"    Runs Test P-value           : {res.runs_p_value:.6f}")
    print(f"    Runs Test Verdict           : {res.runs_verdict}")
    print("-" * 75)
    
    print(" 5. SERIAL CORRELATION COEFFICIENT (Task 2 & 3)")
    print(f"    Lag-1 Autocorrelation (r_1) : {res.serial_corr_r1:.6f}")
    print(f"    Acceptance Threshold        : +/- {res.serial_corr_threshold:.6f} (2 / sqrt(N))")
    print(f"    Serial Correlation Verdict  : {res.serial_corr_verdict}")
    print("-" * 75)
    
    print(" 6. REPEATED PATTERNS & COLLISION ANALYSIS (Task 2)")
    print(f"    2-Byte Digram Patterns      : {res.patterns_2b_unique:,} unique / 65,536 theoretical ({((res.patterns_2b_unique/65536)*100):.2f}% coverage)")
    print(f"    Max Occurrences of 2B Word  : {res.patterns_2b_max_occurrences} (Expected mean: ~8.0)")
    print(f"    4-Byte Word Blocks Tested   : {res.patterns_4b_total:,}")
    print(f"    Observed 4-Byte Collisions  : {res.patterns_4b_collisions}")
    print(f"    Birthday Paradox Expected   : ~{res.patterns_4b_expected_collisions:.2f} collisions")
    print("=" * 75 + "\n")

def print_comparison_table(results):
    """Print comparative table across all RNG sources"""
    print("\n" + "=" * 90)
    print(" COMPARATIVE SUMMARY OF OPERATING SYSTEM RNG MECHANISMS")
    print("=" * 90)
    header = f"{'Metric / Test':<30} | " + " | ".join(f"{r.filename:<16}" for r in results)
    print(header)
    print("-" * 90)
    
    rows = [
        ("File Size (Bytes)", [f"{r.total_bytes:,}" for r in results]),
        ("Shannon Entropy (bits/byte)", [f"{r.entropy:.6f}" for r in results]),
        ("Chi-Square Stat (df=255)", [f"{r.chi_square:.2f}" for r in results]),
        ("Chi-Square P-Value", [f"{r.chi_p_value:.4f}" for r in results]),
        ("Uniformity Test", [r.chi_verdict.split()[0] for r in results]),
        ("Bit 1s Proportion (pi)", [f"{r.prop_ones:.6f}" for r in results]),
        ("NIST Monobit P-Value", [f"{r.monobit_p_value:.4f}" for r in results]),
        ("Monobit Test Verdict", [r.monobit_verdict.split()[0] for r in results]),
        ("NIST Runs P-Value", [f"{r.runs_p_value:.4f}" for r in results]),
        ("Runs Test Verdict", [r.runs_verdict.split()[0] for r in results]),
        ("Serial Correlation (r_1)", [f"{r.serial_corr_r1:.6f}" for r in results]),
        ("Serial Correlation Verdict", [r.serial_corr_verdict.split()[0] for r in results]),
        ("4-Byte Collisions (Obs/Exp)", [f"{r.patterns_4b_collisions} / ~8.0" for r in results]),
        ("2-Byte Pattern Coverage", [f"{((r.patterns_2b_unique/65536)*100):.2f}%" for r in results]),
    ]
    
    for title, values in rows:
        line = f"{title:<30} | " + " | ".join(f"{v:<16}" for v in values)
        print(line)
        
    print("=" * 90)

def export_results(results):
    """Save results summary and byte frequencies to outputs/"""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    summary_path = os.path.join(OUTPUTS_DIR, "results_summary.txt")
    csv_path = os.path.join(OUTPUTS_DIR, "byte_frequency.csv")
    
    with open(summary_path, "w") as f:
        f.write("CryptoLabX - Lab 7: OS RNG Evaluation Results Summary\n")
        f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Team: Yashwant Gour (2024ucp1732), Kunal Sachan (2024ucp1547)\n")
        f.write("=" * 80 + "\n\n")
        
        for r in results:
            f.write(f"DATASET: {r.filename}\n")
            f.write("-" * 50 + "\n")
            f.write(f"Bytes: {r.total_bytes:,} | Bits: {r.total_bits:,}\n")
            f.write(f"Shannon Entropy: {r.entropy:.6f} / 8.000000\n")
            f.write(f"Chi-Square: {r.chi_square:.2f} (df=255, p-value={r.chi_p_value:.6f}) -> {r.chi_verdict}\n")
            f.write(f"Monobit Test: 1s={r.ones_count:,}, 0s={r.zeros_count:,}, pi={r.prop_ones:.6f}, p={r.monobit_p_value:.6f} -> {r.monobit_verdict}\n")
            f.write(f"Runs Test: V_obs={r.runs_count:,}, p={r.runs_p_value:.6f} -> {r.runs_verdict}\n")
            f.write(f"Serial Correlation: r1={r.serial_corr_r1:.6f} -> {r.serial_corr_verdict}\n")
            f.write(f"2-Byte Patterns: {r.patterns_2b_unique}/65536 ({((r.patterns_2b_unique/65536)*100):.2f}%)\n")
            f.write(f"4-Byte Collisions: {r.patterns_4b_collisions} (Theoretical: ~8.00)\n\n")
            
    # Export byte frequency table as CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ByteValue", "Hex"] + [r.filename for r in results])
        for b in range(256):
            row = [b, f"0x{b:02X}"] + [r.byte_counts[b] for r in results]
            writer.writerow(row)
            
    print(f"\n[+] Results successfully exported to:")
    print(f"    - {summary_path}")
    print(f"    - {csv_path}")

def main():
    files = [
        os.path.join(DATA_DIR, "urandom_1mb.bin"),
        os.path.join(DATA_DIR, "openssl_1mb.bin"),
        os.path.join(DATA_DIR, "windows_cng_1mb.bin")
    ]
    
    # Check if files exist
    existing_files = [f for f in files if os.path.exists(f)]
    if not existing_files:
        print("[!] No data files found. Automatically generating data first...")
        import generate_data
        generate_data.main()
        existing_files = [f for f in files if os.path.exists(f)]
        
    if "--all" in sys.argv or not sys.stdin.isatty():
        # Non-interactive / batch execution
        results = [analyze_file(f) for f in existing_files]
        for r in results:
            print_single_report(r)
        if len(results) > 1:
            print_comparison_table(results)
        export_results(results)
        return

    # Interactive menu
    while True:
        print("\n" + "=" * 60)
        print(" CryptoLabX: OS RNG Statistical Analysis & Evaluation")
        print(" Group 07: Yashwant Gour, Kunal Sachan")
        print("=" * 60)
        print(" 1. Analyze Linux / macOS /dev/urandom dataset")
        print(" 2. Analyze OpenSSL rand dataset")
        print(" 3. Analyze Windows CNG / .NET dataset")
        print(" 4. Comparative Evaluation of All 3 Mechanisms")
        print(" 5. Re-generate 1 MB Data Samples")
        print(" 6. Export Results to outputs/ (Summary TXT & Frequency CSV)")
        print(" 7. Exit")
        print("=" * 60)
        
        choice = input("Enter choice (1-7): ").strip()
        
        if choice == "1":
            path = os.path.join(DATA_DIR, "urandom_1mb.bin")
            res = analyze_file(path)
            if res: print_single_report(res)
        elif choice == "2":
            path = os.path.join(DATA_DIR, "openssl_1mb.bin")
            res = analyze_file(path)
            if res: print_single_report(res)
        elif choice == "3":
            path = os.path.join(DATA_DIR, "windows_cng_1mb.bin")
            res = analyze_file(path)
            if res: print_single_report(res)
        elif choice == "4":
            results = [analyze_file(f) for f in existing_files if os.path.exists(f)]
            for r in results:
                print_single_report(r)
            print_comparison_table(results)
        elif choice == "5":
            import generate_data
            generate_data.main()
            existing_files = [f for f in files if os.path.exists(f)]
        elif choice == "6":
            results = [analyze_file(f) for f in existing_files if os.path.exists(f)]
            export_results(results)
        elif choice == "7":
            print("\nExiting OS RNG Evaluation toolkit. Goodbye!")
            break
        else:
            print("[!] Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    main()
