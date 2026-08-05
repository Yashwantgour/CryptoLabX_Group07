import os

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
while True:
    print("\n===== CryptoLabX Toolkit =====")
    print("1. Encrypt")
    print("2. Decrypt")
    print("3. Attack")
    print("4. Analyze")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("Encrypt Module - Coming Soon")

    elif choice == "2":
        print("Decrypt Module - Coming Soon")

    elif choice == "3":
        print("Attack Module - Coming Soon")

    elif choice == "4":
        # print("Analyze Module - Coming Soon")
        analyze_file()
    elif choice == "5":
        print("Thank you for using CryptoLabX.")
        break

    else:
        print("Invalid choice. Please try again.")