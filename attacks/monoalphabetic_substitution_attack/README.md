# Monoalphabetic Substitution Cipher and Cryptanalysis

## Implementation Details
This lab implements the Monoalphabetic Substitution cipher and demonstrates cryptanalysis using Frequency and Pattern Analysis.
**Language Used:** Java (since Python was explicitly disallowed by the assignment instructions).

## Requirements Satisfied
1. `frequency_analysis()` - Performs letter-frequency analysis on the ciphertext.
2. `word_frequency_analysis()` - Analyzes the frequencies of common short words (1 to 3 letters).
3. `pattern_analysis()` - Analyzes repeated letter patterns, such as double letters.
4. `apply_substitution()` - Applies a mapping to either encrypt a plaintext or decode a ciphertext given a key.
5. `display_partial_plaintext()` - Helper function to print the current state of decryption based on a suspected mapping.
6. `verify_solution()` - Validates the recovered key against the original plaintext.

## The Plaintext
The plaintext used is an excerpt discussing "Perfect Secrecy" (representing content roughly around page 37 of Katz and Lindell's *Modern Cryptography*). 

## How to run
You must have the Java Development Kit (JDK) installed on your machine.
1. Open terminal and navigate to `attacks/monoalphabetic_substitution_attack/`.
2. Compile the file: 
   ```bash
   javac src/MonoalphabeticCryptanalysis.java
   ```
3. Run the file:
   ```bash
   java -cp src MonoalphabeticCryptanalysis
   ```

## Cryptanalysis Table (Notebook Example)
| Step | Observation | Possible Substitution | Substitution Tested | Result | Decision |
|---|---|---|---|---|---|
| 1 | 'E' occurs most frequently in ciphertext | Cipher E -> Plain E | E->E | Many substitutions useful | Good decision |
| 2 | "X" is the most common 1-letter word | Cipher X -> Plain A or I | X->A | Makes sense in context | Keep |
| 3 | "YXZ" is the most common 3-letter word | YXZ -> THE | Y->T, X->H, Z->E | Common english word | Keep |
