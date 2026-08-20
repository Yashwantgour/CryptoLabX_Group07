from shift_cipher import decrypt

def load_dictionary(filepath):
    with open(filepath, 'r') as f:
        words = set(line.strip().lower() for line in f)
    return words

def score_plaintext(text, dictionary):
    words = text.split()
    score = 0
    for word in words:
        clean_word = ''.join(c.lower() for c in word if c.isalpha())
        if clean_word in dictionary:
            score += 1
    return score

def brute_force_attack(ciphertext, dictionary_path):
    dictionary = load_dictionary(dictionary_path)
    best_key = 0
    best_score = -1
    best_plaintext = ""
    
    for key in range(26):
        plaintext = decrypt(ciphertext, key)
        score = score_plaintext(plaintext, dictionary)
        if score > best_score:
            best_score = score
            best_key = key
            best_plaintext = plaintext
            
    return best_key, best_plaintext
