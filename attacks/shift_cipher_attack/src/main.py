from shift_cipher import encrypt
from brute_force_dictionary import brute_force_attack
from chi_square_attack import chi_square_attack
import sys
import os

def main():
    dict_path = os.path.join(os.path.dirname(__file__), '..', 'dictionary', 'english_words.txt')
    
    plaintext = "This is a secret message used to test the shift cipher attacks using dictionary and chi square methods."
    key = 7
    ciphertext = encrypt(plaintext, key)
    
    print(f"Original Text: {plaintext}")
    print(f"Key: {key}")
    print(f"Ciphertext: {ciphertext}")
    
    print("\n--- Dictionary Brute Force Attack ---")
    dict_key, dict_pt = brute_force_attack(ciphertext, dict_path)
    print(f"Predicted Key: {dict_key}")
    print(f"Decrypted Text: {dict_pt}")
    
    print("\n--- Chi-Square Attack ---")
    chi_key, chi_pt = chi_square_attack(ciphertext)
    print(f"Predicted Key: {chi_key}")
    print(f"Decrypted Text: {chi_pt}")

if __name__ == "__main__":
    main()
