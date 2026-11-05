import os
import sys
import logging

os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    filename="outputs/cryptolabx.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

def analyze_file():
    filename = input("Enter file name (example: sample1.txt): ")

    path = os.path.join("datasets", filename)

    if not os.path.exists(path):
        print("File not found!")
        return

    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    # Characters
    characters = len(text)

    # Words
    words = len(text.split())

    # Lines
    lines = len(text.splitlines())

    # Unique Characters
    unique_characters = len(set(text))

    # Letter Frequency
    frequency = {}

    for ch in text.lower():
        if ch.isalpha():
            frequency[ch] = frequency.get(ch, 0) + 1

    print("\n===== File Analysis =====")
    print("Characters :", characters)
    print("Words      :", words)
    print("Lines      :", lines)
    print("Unique Characters :", unique_characters)

    print("\nLetter Frequency")

    for letter in sorted(frequency):
        print(letter, ":", frequency[letter])

def analyze_menu():
    print("\n===== Analysis Module =====")
    print("1. Text File Analysis (Datasets)")
    print("2. OS Random-Number Generation (RNG) Statistical Evaluation")
    sub_choice = input("Enter choice (1-2): ").strip()
    if sub_choice == "1":
        analyze_file()
    elif sub_choice == "2":
        import subprocess
        script_path = os.path.join("analysis", "rng_evaluation", "src", "analyze_rng.py")
        subprocess.run([sys.executable, script_path])
    else:
        print("Invalid analysis option.")

def attack_menu():
    print("\n===== Attack Module =====")
    print("1. MT19937 Stream Cipher & Predictable Token Attack (Lab 10)")
    print("2. Padding Oracle Attack (Lab 7)")
    print("3. Monoalphabetic Substitution Attack (Lab 5)")
    print("4. Shift Cipher Attack (Lab 4)")
    sub_choice = input("Enter choice (1-4): ").strip()
    if sub_choice == "1":
        import subprocess
        script_path = os.path.join("attacks", "mt19937_stream_cipher", "src", "run_assignment10.py")
        subprocess.run([sys.executable, script_path])
    elif sub_choice == "2":
        import subprocess
        script_path = os.path.join("attacks", "padding_oracle.py")
        subprocess.run([sys.executable, script_path])
    elif sub_choice == "3":
        print("Monoalphabetic Substitution Attack available in attacks/monoalphabetic_substitution_attack/")
    elif sub_choice == "4":
        print("Shift Cipher Attack available in attacks/shift_cipher_attack/")
    else:
        print("Invalid attack option.")

def main():
    while True:
        print("\n===== CryptoLabX Toolkit =====")
        print("1. Encrypt")
        print("2. Decrypt")
        print("3. Attack")
        print("4. Analyze")
        print("5. Math (Prime Generation)")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            logging.info("Selected Option: Encrypt")
            print("Encrypt Module - Coming Soon")

        elif choice == "2":
            logging.info("Selected Option: Decrypt")
            print("Decrypt Module - Coming Soon")

        elif choice == "3":
            logging.info("Selected Option: Attack")
            attack_menu()

        elif choice == "4":
            logging.info("Selected Option: Analyze")
            analyze_menu()

        elif choice == "5":
            logging.info("Selected Option: Math")
            import subprocess
            script_path = os.path.join("math", "prime_generation", "src", "miller_rabin.py")
            subprocess.run([sys.executable, script_path])

        elif choice == "6":
            logging.info("Selected Option: Exit")
            print("Thank you for using CryptoLabX.")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

