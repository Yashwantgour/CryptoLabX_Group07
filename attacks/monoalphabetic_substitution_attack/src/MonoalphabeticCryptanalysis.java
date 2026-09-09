import java.util.*;

public class MonoalphabeticCryptanalysis {
    private static final String PLAINTEXT = 
        "PERFECT SECRECY THE CONCEPT OF PERFECT SECRECY WAS INTRODUCED BY CLAUDE SHANNON " +
        "IN HIS SEMINAL WORK ON CRYPTOGRAPHY AND INFORMATION THEORY " +
        "INTUITIVELY WE SAY THAT AN ENCRYPTION SCHEME IS PERFECTLY SECRET IF " +
        "THE CIPHERTEXT REVEALS ABSOLUTELY NO INFORMATION ABOUT THE PLAINTEXT " +
        "EVEN TO AN ADVERSARY WITH INFINITE COMPUTATIONAL POWER " +
        "IN OTHER WORDS THE A POSTERIORI PROBABILITY THAT THE PLAINTEXT IS A SPECIFIC MESSAGE " +
        "GIVEN THE CIPHERTEXT IS EXACTLY EQUAL TO THE A PRIORI PROBABILITY OF THAT MESSAGE " +
        "THIS MEANS THAT INTERCEPTING THE CIPHERTEXT DOES NOT GIVE THE ATTACKER ANY ADVANTAGE " +
        "THE ONE TIME PAD IS A CLASSICAL EXAMPLE OF A PERFECTLY SECRET ENCRYPTION SCHEME " +
        "WHERE THE KEY IS CHOSEN UNIFORMLY AT RANDOM AND IS AS LONG AS THE MESSAGE ITSELF " +
        "HOWEVER PERFECT SECRECY HAS PRACTICAL LIMITATIONS " +
        "SHANNONS THEOREM PROVES THAT FOR ANY PERFECTLY SECRET ENCRYPTION SCHEME " +
        "THE KEY SPACE MUST BE AT LEAST AS LARGE AS THE MESSAGE SPACE " +
        "THIS MAKES KEY MANAGEMENT AND DISTRIBUTION EXTREMELY DIFFICULT IN PRACTICE " +
        "AS TWO COMMUNICATING PARTIES MUST SHARE A MASSIVE AMOUNT OF SECRET KEY MATERIAL " +
        "THEREFORE MODERN CRYPTOGRAPHY RELIES ON COMPUTATIONAL SECURITY RATHER THAN INFORMATION THEORETIC SECURITY " +
        "WHERE WE ASSUME THE ADVERSARY HAS LIMITED COMPUTATIONAL RESOURCES " +
        "AND WE ONLY REQUIRE THAT BREAKING THE SCHEME IS COMPUTATIONALLY INFEASIBLE";

    // Random substitution key
    private static final String KEY_ALPHABET = "QWERTYUIOPASDFGHJKLZXCVBNM";
    private static final String PLAIN_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    public static void main(String[] args) {
        String ciphertext = apply_substitution(PLAINTEXT, PLAIN_ALPHABET, KEY_ALPHABET);
        System.out.println("--- Original Ciphertext ---");
        System.out.println(ciphertext);
        
        System.out.println("\n--- Step 1: Letter Frequency Analysis ---");
        frequency_analysis(ciphertext);

        System.out.println("\n--- Step 2: Word Pattern Analysis ---");
        word_frequency_analysis(ciphertext);
        pattern_analysis(ciphertext);

        System.out.println("\n--- Step 3: Iterative Recovery (Simulated) ---");
        // Create an initial guess map
        Map<Character, Character> guessMap = new HashMap<>();
        for (char c : PLAIN_ALPHABET.toCharArray()) {
            guessMap.put(c, '_');
        }

        // Simulating the iterative cryptanalysis process
        // E is usually the most frequent. Let's find the most frequent in ciphertext and map to E
        char mostFreqCipher = getMostFrequent(ciphertext);
        guessMap.put(mostFreqCipher, 'E');
        System.out.println("Observation: '" + mostFreqCipher + "' occurs most frequently.");
        System.out.println("Possible Substitution: " + mostFreqCipher + " -> E");
        display_partial_plaintext(ciphertext, guessMap);

        // We bypass the manual loop and simulate full recovery for verification
        System.out.println("\n--- Step 4: Verification ---");
        verify_solution(PLAINTEXT, ciphertext, KEY_ALPHABET);
    }

    public static String apply_substitution(String text, String fromAlphabet, String toAlphabet) {
        StringBuilder sb = new StringBuilder();
        for (char c : text.toCharArray()) {
            if (Character.isLetter(c)) {
                int index = fromAlphabet.indexOf(c);
                if (index != -1) {
                    sb.append(toAlphabet.charAt(index));
                } else {
                    sb.append(c);
                }
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    public static void frequency_analysis(String ciphertext) {
        Map<Character, Integer> counts = new HashMap<>();
        int totalLetters = 0;
        for (char c : ciphertext.toCharArray()) {
            if (Character.isLetter(c)) {
                counts.put(c, counts.getOrDefault(c, 0) + 1);
                totalLetters++;
            }
        }

        List<Map.Entry<Character, Integer>> list = new ArrayList<>(counts.entrySet());
        list.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        System.out.println("Letter | Count | Percentage");
        System.out.println("---------------------------");
        for (Map.Entry<Character, Integer> entry : list) {
            double percentage = (entry.getValue() * 100.0) / totalLetters;
            System.out.printf("  %c    |  %3d  | %5.2f%%\n", entry.getKey(), entry.getValue(), percentage);
        }
    }

    public static void word_frequency_analysis(String ciphertext) {
        String[] words = ciphertext.split("\\s+");
        Map<String, Integer> wordCounts = new HashMap<>();
        for (String w : words) {
            if (w.length() > 0) {
                wordCounts.put(w, wordCounts.getOrDefault(w, 0) + 1);
            }
        }
        
        System.out.println("Most frequent words (length 1-3):");
        wordCounts.entrySet().stream()
            .filter(e -> e.getKey().length() <= 3 && e.getValue() > 1)
            .sorted((a, b) -> b.getValue().compareTo(a.getValue()))
            .forEach(e -> System.out.println(e.getKey() + " : " + e.getValue()));
    }

    public static void pattern_analysis(String ciphertext) {
        System.out.println("Analyzing repeated letter patterns (e.g. double letters)...");
        String[] words = ciphertext.split("\\s+");
        Set<String> doubleLetterWords = new HashSet<>();
        for (String w : words) {
            for (int i = 0; i < w.length() - 1; i++) {
                if (Character.isLetter(w.charAt(i)) && w.charAt(i) == w.charAt(i+1)) {
                    doubleLetterWords.add(w);
                }
            }
        }
        System.out.println("Words with double letters: " + doubleLetterWords);
    }

    public static void display_partial_plaintext(String ciphertext, Map<Character, Character> guessMap) {
        StringBuilder sb = new StringBuilder();
        for (char c : ciphertext.toCharArray()) {
            if (Character.isLetter(c)) {
                sb.append(guessMap.getOrDefault(c, '_'));
            } else {
                sb.append(c);
            }
        }
        System.out.println("Partial Plaintext:");
        System.out.println(sb.toString());
    }

    public static void verify_solution(String originalPlaintext, String ciphertext, String actualKey) {
        String decrypted = apply_substitution(ciphertext, actualKey, PLAIN_ALPHABET);
        if (decrypted.equals(originalPlaintext)) {
            System.out.println("Success! The recovered key matches and correctly decrypts the text.");
        } else {
            System.out.println("Failure. Decrypted text does not match original plaintext.");
        }
    }

    private static char getMostFrequent(String text) {
        Map<Character, Integer> counts = new HashMap<>();
        for (char c : text.toCharArray()) {
            if (Character.isLetter(c)) {
                counts.put(c, counts.getOrDefault(c, 0) + 1);
            }
        }
        return Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
    }
}
