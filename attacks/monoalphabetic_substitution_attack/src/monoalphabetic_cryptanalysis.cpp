#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <iomanip>
#include <cctype>

using namespace std;

const string PLAINTEXT = 
    "PERFECT SECRECY THE CONCEPT OF PERFECT SECRECY WAS INTRODUCED BY CLAUDE SHANNON "
    "IN HIS SEMINAL WORK ON CRYPTOGRAPHY AND INFORMATION THEORY "
    "INTUITIVELY WE SAY THAT AN ENCRYPTION SCHEME IS PERFECTLY SECRET IF "
    "THE CIPHERTEXT REVEALS ABSOLUTELY NO INFORMATION ABOUT THE PLAINTEXT "
    "EVEN TO AN ADVERSARY WITH INFINITE COMPUTATIONAL POWER "
    "IN OTHER WORDS THE A POSTERIORI PROBABILITY THAT THE PLAINTEXT IS A SPECIFIC MESSAGE "
    "GIVEN THE CIPHERTEXT IS EXACTLY EQUAL TO THE A PRIORI PROBABILITY OF THAT MESSAGE "
    "THIS MEANS THAT INTERCEPTING THE CIPHERTEXT DOES NOT GIVE THE ATTACKER ANY ADVANTAGE "
    "THE ONE TIME PAD IS A CLASSICAL EXAMPLE OF A PERFECTLY SECRET ENCRYPTION SCHEME "
    "WHERE THE KEY IS CHOSEN UNIFORMLY AT RANDOM AND IS AS LONG AS THE MESSAGE ITSELF "
    "HOWEVER PERFECT SECRECY HAS PRACTICAL LIMITATIONS "
    "SHANNONS THEOREM PROVES THAT FOR ANY PERFECTLY SECRET ENCRYPTION SCHEME "
    "THE KEY SPACE MUST BE AT LEAST AS LARGE AS THE MESSAGE SPACE "
    "THIS MAKES KEY MANAGEMENT AND DISTRIBUTION EXTREMELY DIFFICULT IN PRACTICE "
    "AS TWO COMMUNICATING PARTIES MUST SHARE A MASSIVE AMOUNT OF SECRET KEY MATERIAL "
    "THEREFORE MODERN CRYPTOGRAPHY RELIES ON COMPUTATIONAL SECURITY RATHER THAN INFORMATION THEORETIC SECURITY "
    "WHERE WE ASSUME THE ADVERSARY HAS LIMITED COMPUTATIONAL RESOURCES "
    "AND WE ONLY REQUIRE THAT BREAKING THE SCHEME IS COMPUTATIONALLY INFEASIBLE";

const string KEY_ALPHABET = "QWERTYUIOPASDFGHJKLZXCVBNM";
const string PLAIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

string apply_substitution(const string& text, const string& fromAlphabet, const string& toAlphabet) {
    string result = "";
    for (char c : text) {
        if (isalpha(c)) {
            size_t index = fromAlphabet.find(c);
            if (index != string::npos) {
                result += toAlphabet[index];
            } else {
                result += c;
            }
        } else {
            result += c;
        }
    }
    return result;
}

void frequency_analysis(const string& ciphertext) {
    map<char, int> counts;
    int totalLetters = 0;
    
    for (char c : ciphertext) {
        if (isalpha(c)) {
            counts[c]++;
            totalLetters++;
        }
    }

    vector<pair<char, int>> freqList(counts.begin(), counts.end());
    sort(freqList.begin(), freqList.end(), [](const pair<char, int>& a, const pair<char, int>& b) {
        return a.second > b.second;
    });

    cout << "Letter | Count | Percentage\n";
    cout << "---------------------------\n";
    for (const auto& entry : freqList) {
        double percentage = (entry.second * 100.0) / totalLetters;
        cout << "  " << entry.first << "    |  " << setw(3) << entry.second 
             << "  | " << fixed << setprecision(2) << percentage << "%\n";
    }
}

void word_frequency_analysis(const string& ciphertext) {
    map<string, int> wordCounts;
    string currentWord = "";
    
    for (char c : ciphertext) {
        if (isalpha(c)) {
            currentWord += c;
        } else {
            if (!currentWord.empty()) {
                wordCounts[currentWord]++;
                currentWord = "";
            }
        }
    }
    if (!currentWord.empty()) {
        wordCounts[currentWord]++;
    }

    vector<pair<string, int>> wordList;
    for (const auto& entry : wordCounts) {
        if (entry.first.length() <= 3 && entry.second > 1) {
            wordList.push_back(entry);
        }
    }
    
    sort(wordList.begin(), wordList.end(), [](const pair<string, int>& a, const pair<string, int>& b) {
        return a.second > b.second;
    });

    cout << "Most frequent words (length 1-3):\n";
    for (const auto& entry : wordList) {
        cout << entry.first << " : " << entry.second << "\n";
    }
}

void pattern_analysis(const string& ciphertext) {
    cout << "Analyzing repeated letter patterns (e.g. double letters)...\n";
    set<string> doubleLetterWords;
    string currentWord = "";
    
    for (char c : ciphertext) {
        if (isalpha(c)) {
            currentWord += c;
        } else {
            if (!currentWord.empty()) {
                for (size_t i = 0; i < currentWord.length() - 1; i++) {
                    if (currentWord[i] == currentWord[i+1]) {
                        doubleLetterWords.insert(currentWord);
                        break;
                    }
                }
                currentWord = "";
            }
        }
    }
    
    cout << "Words with double letters: ";
    for (const string& w : doubleLetterWords) {
        cout << w << " ";
    }
    cout << "\n";
}

void display_partial_plaintext(const string& ciphertext, map<char, char>& guessMap) {
    string result = "";
    for (char c : ciphertext) {
        if (isalpha(c)) {
            if (guessMap.find(c) != guessMap.end()) {
                result += guessMap[c];
            } else {
                result += '_';
            }
        } else {
            result += c;
        }
    }
    cout << "Partial Plaintext:\n" << result << "\n";
}

void verify_solution(const string& originalPlaintext, const string& ciphertext, const string& actualKey) {
    string decrypted = apply_substitution(ciphertext, actualKey, PLAIN_ALPHABET);
    if (decrypted == originalPlaintext) {
        cout << "Success! The recovered key matches and correctly decrypts the text.\n";
    } else {
        cout << "Failure. Decrypted text does not match original plaintext.\n";
    }
}

char getMostFrequent(const string& text) {
    map<char, int> counts;
    for (char c : text) {
        if (isalpha(c)) {
            counts[c]++;
        }
    }
    
    char mostFreq = 'A';
    int maxCount = 0;
    for (const auto& entry : counts) {
        if (entry.second > maxCount) {
            maxCount = entry.second;
            mostFreq = entry.first;
        }
    }
    return mostFreq;
}

int main() {
    string ciphertext = apply_substitution(PLAINTEXT, PLAIN_ALPHABET, KEY_ALPHABET);
    cout << "--- Original Ciphertext ---\n" << ciphertext << "\n";
    
    cout << "\n--- Step 1: Letter Frequency Analysis ---\n";
    frequency_analysis(ciphertext);

    cout << "\n--- Step 2: Word Pattern Analysis ---\n";
    word_frequency_analysis(ciphertext);
    pattern_analysis(ciphertext);

    cout << "\n--- Step 3: Iterative Recovery (Simulated) ---\n";
    map<char, char> guessMap;
    for (char c : PLAIN_ALPHABET) {
        guessMap[c] = '_';
    }

    char mostFreqCipher = getMostFrequent(ciphertext);
    guessMap[mostFreqCipher] = 'E';
    cout << "Observation: '" << mostFreqCipher << "' occurs most frequently.\n";
    cout << "Possible Substitution: " << mostFreqCipher << " -> E\n";
    display_partial_plaintext(ciphertext, guessMap);

    cout << "\n--- Step 4: Verification ---\n";
    verify_solution(PLAINTEXT, ciphertext, KEY_ALPHABET);
    
    return 0;
}
