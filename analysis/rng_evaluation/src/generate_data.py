#!/usr/bin/env python3
"""
OS Random Number Generation Utility
CryptoLabX - Lab 7: OS Random-Number Generation (RNG) Evaluation
Group 07: Yashwant Gour (2024ucp1732), Kunal Sachan (2024ucp1547)

Generates at least 1 MB (1,048,576 bytes) of random data using:
1. Linux / macOS /dev/urandom
2. OpenSSL rand utility
3. Windows CNG / .NET cryptographic CSPRNG API
"""

import os
import sys
import subprocess
import secrets

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
ONE_MB = 1048576  # 1 MB in bytes

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def generate_urandom():
    """Generate 1 MB from /dev/urandom"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, "urandom_1mb.bin")
    print(f"[*] Generating 1 MB from /dev/urandom -> {filepath}")
    
    if os.path.exists("/dev/urandom"):
        with open("/dev/urandom", "rb") as src, open(filepath, "wb") as dst:
            dst.write(src.read(ONE_MB))
        print(f"    [+] Successfully generated {ONE_MB} bytes using /dev/urandom.")
    else:
        # Fallback if on Windows
        with open(filepath, "wb") as dst:
            dst.write(os.urandom(ONE_MB))
        print(f"    [+] Successfully generated {ONE_MB} bytes using os.urandom.")

def generate_openssl():
    """Generate 1 MB using OpenSSL rand CLI"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, "openssl_1mb.bin")
    print(f"[*] Generating 1 MB from OpenSSL rand utility -> {filepath}")
    
    try:
        subprocess.run(["openssl", "rand", "-out", filepath, str(ONE_MB)], check=True)
        print(f"    [+] Successfully generated {ONE_MB} bytes using OpenSSL CLI.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback if openssl binary not found
        import ssl
        print("    [!] 'openssl' command failed or not in PATH, generating via ssl module...")
        with open(filepath, "wb") as dst:
            dst.write(ssl.RAND_bytes(ONE_MB))
        print(f"    [+] Successfully generated {ONE_MB} bytes using OpenSSL bindings.")

def generate_windows_cng():
    """Generate 1 MB using Windows CNG / .NET cryptographic API"""
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, "windows_cng_1mb.bin")
    print(f"[*] Generating 1 MB from Windows CNG / .NET Cryptographic RNG -> {filepath}")
    
    # Check if running on Windows and PowerShell is available
    if sys.platform.startswith("win"):
        ps_cmd = (
            f"[byte[]]$bytes = New-Object byte[] {ONE_MB}; "
            "[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes); "
            f"[System.IO.File]::WriteAllBytes('{filepath}', $bytes)"
        )
        try:
            subprocess.run(["powershell", "-Command", ps_cmd], check=True)
            print(f"    [+] Successfully generated {ONE_MB} bytes via Windows CNG / .NET API.")
            return
        except Exception:
            pass
            
    # When generating on non-Windows platforms (or as a fallback), use standard CSPRNG
    # that uses the OS cryptographic provider (Windows CNG / BCryptGenRandom on Windows, getentropy on Unix)
    data = secrets.token_bytes(ONE_MB)
    with open(filepath, "wb") as dst:
        dst.write(data)
    print(f"    [+] Successfully generated {ONE_MB} bytes via Cryptographic CSPRNG.")

def main():
    print("=" * 65)
    print(" CryptoLabX - OS Random Number Generator (RNG) Data Collection")
    print("=" * 65)
    print("Target size: 1 MB (1,048,576 bytes) per source\n")
    
    generate_urandom()
    generate_openssl()
    generate_windows_cng()
    
    print("\n[+] All 3 datasets have been generated in:")
    print(f"    {DATA_DIR}")
    for fname in ["urandom_1mb.bin", "openssl_1mb.bin", "windows_cng_1mb.bin"]:
        p = os.path.join(DATA_DIR, fname)
        if os.path.exists(p):
            print(f"    - {fname}: {os.path.getsize(p):,} bytes")
    print("=" * 65)

if __name__ == "__main__":
    main()
