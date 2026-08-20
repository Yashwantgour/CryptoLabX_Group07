# Lab Assignment 4: Cryptanalysis of Shift Cipher

## 1. Both Algorithms of Cryptanalysis
Refer to `src/brute_force_dictionary.py` and `src/chi_square_attack.py` for the implementation.

## 2. Comparison
The dictionary scoring method counts the number of valid English words for each predicted shift.
The Chi-Square method statistically compares the character frequencies of the decrypted text with the standard English letter frequencies.
Both methods predicted the correct key in our test cases, but Chi-Square is typically more robust for larger texts, while dictionary scoring is better for short texts with complete words.

## 3. Failure Analysis
- **Dictionary Scoring** may fail if the ciphertext is very short and does not contain full dictionary words, or if it contains many names/slangs not in the dictionary.
- **Chi-Square Analysis** may fail for very short ciphertexts because the letter frequencies won't have enough data to match the expected standard English distribution.
- **Improvement**: Combining both methods or using bigram/trigram frequencies can yield better accuracy.

## 4. Observations
- The Chi-Square method is computationally efficient and requires no external dictionary file.
- The dictionary attack requires a comprehensive word list to be effective.

## 5. Conclusion
We successfully implemented the shift cipher and two methods to break it: Dictionary Scoring and Chi-Square Analysis. Both are effective given sufficient ciphertext length.

## Results Table
| Test Case | Actual Key | Dictionary Key | Chi-Square Key | Dictionary Correct? | Chi-Square Correct? |
|-----------|------------|----------------|----------------|---------------------|---------------------|
| 1         | 7          | 7              | 7              | Yes                 | Yes                 |
| 2         | 15         | 15             | 15             | Yes                 | Yes                 |
