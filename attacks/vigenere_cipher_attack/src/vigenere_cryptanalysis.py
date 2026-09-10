#!/usr/bin/env python3

import re
from collections import Counter

# Ciphertext 1 (Odd Group No.)
CIPHERTEXT = """
DAZFI SFSPA VQLSN PXYSZ WXALC DAFGQ UISMT PHZGA 
MKTTF TCCFX 
KFCRG GLPFE TZMMM ZOZDE ADWVZ WMWKV GQSOH QSVHP 
WFKLS LEASE 
PWHMJ EGKPU RVSXJ XVBWV POSDE TEQTX OBZIK WCXLW 
NUOVJ MJCLL 
OEOFA ZENVM JILOW ZEKAZ EJAQD ILSWW ESGUG KTZGQ 
ZVRMN WTQSE 
OTKTK PBSTA MQVER MJEGL JQRTL GFJYG SPTZP GTACM 
OECBX SESCI 
YGUFP KVILL TWDKS ZODFW FWEAA PQTFS TQIRG MPMEL 
RYELH QSVWB 
AWMOS DELHM UZGPG YEKZU KWTAM ZJMLS EVJQT GLAWV 
OVVXH KWQIL 
IEUYS ZWXAH HUSZO GMUZQ CIMVZ UVWIF JJHPW VXFSE 
TZEDF 
"""

ENGLISH_FREQ = [
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015,
    0.06094, 0.06966, 0.00153, 0.00772, 0.04025, 0.02406, 0.06749,
    0.07507, 0.01929, 0.00095, 0.05987, 0.06327, 0.09056, 0.02758,
    0.00978, 0.02360, 0.00150, 0.01974, 0.00074
]

def clean_ciphertext(text):
    return re.sub(r'[^A-Z]', '', text.upper())

def find_repeated_patterns(text, length=3):
    patterns = {}
    for i in range(len(text) - length + 1):
        pattern = text[i:i+length]
        if pattern not in patterns:
            patterns[pattern] = []
        patterns[pattern].append(i)
    
    repeated = {k: v for k, v in patterns.items() if len(v) > 1}
    return repeated

def calculate_distances(patterns):
    distances = {}
    for pattern, indices in patterns.items():
        dist = []
        for i in range(1, len(indices)):
            dist.append(indices[i] - indices[i-1])
        distances[pattern] = dist
    return distances

def find_factors(distances):
    factors = []
    for pattern, dist_list in distances.items():
        for d in dist_list:
            for i in range(2, min(d + 1, 21)):
                if d % i == 0:
                    factors.append(i)
    return factors

def kasiski_analysis(text):
    patterns = find_repeated_patterns(text, 3)
    distances = calculate_distances(patterns)
    factors = find_factors(distances)
    
    if not factors:
        return 1
        
    counts = Counter(factors)
    # We will pick the most common factor > 2, as 2 is too generic.
    # Often, kasiski returns 2 or 3 heavily, but the real key length could be a multiple.
    for factor, count in counts.most_common():
        if factor > 3:
            return factor
    return counts.most_common(1)[0][0]

def calculate_ic(text):
    n = len(text)
    if n <= 1:
        return 0
    counts = Counter(text)
    ic = 0.0
    for char, count in counts.items():
        ic += (count * (count - 1))
    return ic / (n * (n - 1))

def split_into_groups(text, key_length):
    groups = ['' for _ in range(key_length)]
    for i, char in enumerate(text):
        groups[i % key_length] += char
    return groups

def frequency_analysis(group):
    counts = Counter(group)
    freq = {chr(i + 65): counts.get(chr(i + 65), 0) / len(group) for i in range(26)}
    return freq

def find_shift(group):
    freq = frequency_analysis(group)
    min_chi = float('inf')
    best_shift = 0
    
    for shift in range(26):
        chi = 0
        for i in range(26):
            expected = ENGLISH_FREQ[i]
            observed = freq[chr((i + shift) % 26 + 65)]
            if expected > 0:
                chi += ((observed - expected) ** 2) / expected
        
        if chi < min_chi:
            min_chi = chi
            best_shift = shift
            
    return best_shift

def find_key(text, key_length):
    groups = split_into_groups(text, key_length)
    key = ""
    for group in groups:
        shift = find_shift(group)
        key += chr(shift + 65)
    return key

def vigenere_decrypt(text, key):
    decrypted = ""
    for i, char in enumerate(text):
        shift = ord(key[i % len(key)]) - 65
        decrypted_char = chr(((ord(char) - 65 - shift) % 26) + 65)
        decrypted += decrypted_char
    return decrypted

def vigenere_encrypt(text, key):
    encrypted = ""
    for i, char in enumerate(text):
        shift = ord(key[i % len(key)]) - 65
        encrypted_char = chr(((ord(char) - 65 + shift) % 26) + 65)
        encrypted += encrypted_char
    return encrypted

def verify(original, decrypted, key):
    re_encrypted = vigenere_encrypt(decrypted, key)
    return original == re_encrypted

def main():
    clean_text = clean_ciphertext(CIPHERTEXT)
    
    print("=== Cryptanalysis of Vigenere Cipher ===")
    
    # 2. Estimate the key Length using Kasiski's test
    key_length = kasiski_analysis(clean_text)
    
    # Validate with IC just in case Kasiski returns 2 but the real key is 6.
    # The assignment says estimate using Kasiski, but let's make sure it's accurate.
    # We can check IC for multiples of the Kasiski guess.
    best_len = key_length
    best_ic = sum(calculate_ic(g) for g in split_into_groups(clean_text, key_length)) / key_length
    
    for mult in range(2, 6):
        test_len = key_length * mult
        avg_ic = sum(calculate_ic(g) for g in split_into_groups(clean_text, test_len)) / test_len
        if avg_ic > 0.06: # closer to english IC
            if avg_ic > best_ic:
                best_len = test_len
                best_ic = avg_ic
                
    # Use the best refined length based on Kasiski base factor
    final_key_length = best_len
    
    print(f"Estimated Key Length: {final_key_length}")
    
    # 3. Divide the ciphertext into groups according to the estimated key length.
    groups = split_into_groups(clean_text, final_key_length)
    
    # 4. Perform frequency analysis on each group.
    for i, group in enumerate(groups):
        freq = frequency_analysis(group)
        print(f"\nFrequency table for group {i+1}:")
        for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if freq[char] > 0:
                print(f"  {char}: {freq[char]:.4f}")
                
    # 5. Determine the probable key.
    probable_key = find_key(clean_text, final_key_length)
    print(f"\nRecovered Key: {probable_key}")
    
    # 6. Decrypt the ciphertext using the recovered key.
    decrypted_text = vigenere_decrypt(clean_text, probable_key)
    print(f"\nRecovered Plaintext:\n{decrypted_text}")
    
    # 8. Verify the result by re-encrypting the recovered plaintext
    is_valid = verify(clean_text, decrypted_text, probable_key)
    if is_valid:
        print("\nVerification: SUCCESS (Re-encryption matches original ciphertext)")
    else:
        print("\nVerification: FAILED")

if __name__ == "__main__":
    main()
