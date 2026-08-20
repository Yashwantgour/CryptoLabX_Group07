from shift_cipher import decrypt

# Standard English letter frequencies
ENGLISH_FREQS = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253,
    'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094,
    'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025,
    'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929,
    'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
    'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150,
    'y': 0.01974, 'z': 0.00074
}

def calculate_chi_square(text):
    text = ''.join(c.lower() for c in text if c.isalpha())
    n = len(text)
    if n == 0:
        return float('inf')
        
    counts = {char: text.count(char) for char in 'abcdefghijklmnopqrstuvwxyz'}
    
    chi_square = 0
    for char in 'abcdefghijklmnopqrstuvwxyz':
        expected = ENGLISH_FREQS[char] * n
        observed = counts[char]
        if expected > 0:
            chi_square += ((observed - expected) ** 2) / expected
            
    return chi_square

def chi_square_attack(ciphertext):
    best_key = 0
    min_chi_square = float('inf')
    best_plaintext = ""
    
    for key in range(26):
        plaintext = decrypt(ciphertext, key)
        chi_sq = calculate_chi_square(plaintext)
        if chi_sq < min_chi_square:
            min_chi_square = chi_sq
            best_key = key
            best_plaintext = plaintext
            
    return best_key, best_plaintext
