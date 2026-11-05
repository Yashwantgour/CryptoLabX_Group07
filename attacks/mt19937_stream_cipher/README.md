# Lab Assignment 10: MT19937 Stream Cipher and Predictable Token Attack

**CryptoLabX - Cryptography Laboratory (22CPP307)**  
**Group Number:** Group 07  
**Team Members:**  
- **Kunal Sachan** (Roll No: `2024ucp1547`, Email: `2024ucp1547@mnit.ac.in`) — *Primary Contributor: Part A (Stream Cipher & Seed Cracker)*
- **Yashwant Gour** (Roll No: `2024ucp1732`, Email: `2024ucp1732@mnit.ac.in`) — *Primary Contributor: Part B (Predictable Token Generator & Interval Attack, Notebook Report)*

---

## 1. Objective

To understand why statistical pseudo-random number generators (PRNGs), specifically **Mersenne Twister (MT19937)**, are fundamentally unsuitable for cryptographic applications. This is demonstrated by:
1. Constructing a toy symmetric stream cipher using MT19937 and breaking it via a **known-plaintext brute-force attack** against a weak 16-bit seed ($2^{16} = 65,536$ search space).
2. Simulating an insecure password reset token generation mechanism seeded by Unix timestamps and recovering the exact seed and token within an arbitrary observation window ($[T - 300, T + 300]$ seconds).
3. Analyzing the mathematical weaknesses of MT19937, state reconstruction via untempering, keystream extraction through XOR properties, and low-entropy timestamp seeding.

---

## 2. Directory Structure

```
attacks/mt19937_stream_cipher/
├── README.md                              # Comprehensive laboratory notebook & report
├── assignment10_notebook.ipynb            # Interactive Jupyter Notebook demonstration
├── outputs/
│   ├── part_a_stream_cipher_results.txt   # Verified logs for Part A (Cipher & Seed Recovery)
│   ├── part_b_token_prediction_results.txt# Verified logs for Part B (Token Prediction & Timing)
│   └── full_demonstration_output.txt      # Full end-to-end execution transcript
└── src/
    ├── mt19937_cipher.py                  # Part A implementation (Stream cipher & 16-bit cracker)
    ├── password_reset_token.py            # Part B implementation (Token generator & Interval attack)
    └── run_assignment10.py                # Unified CLI runner and benchmark engine
```

---

## 3. How to Execute

### Option 1: Unified Assignment Suite (Parts A & B)
Run the automated unified runner from the repository root:
```bash
python3 attacks/mt19937_stream_cipher/src/run_assignment10.py
```

### Option 2: Execute Part A Only (Stream Cipher & Seed Recovery)
```bash
python3 attacks/mt19937_stream_cipher/src/mt19937_cipher.py
```

### Option 3: Execute Part B Only (Predictable Token Attack)
```bash
python3 attacks/mt19937_stream_cipher/src/password_reset_token.py
```

### Option 4: Via Interactive Main Toolkit
```bash
python3 main.py
# Select Option 3 (Attack) -> MT19937 PRNG Cryptanalysis Suite
```

---

## 4. Notebook Work (Theoretical & Mathematical Analysis)

### Question 12: MT19937 Algorithm and Why It Is Not Cryptographically Secure

#### 1. Mathematical Architecture of MT19937
The Mersenne Twister (MT19937) is a generalized feedback shift register (GFSR) algorithm developed by Makoto Matsumoto and Takuji Nishimura (1997). It provides an astronomical period of $2^{19937} - 1$ (a Mersenne prime, hence the name) and 623-dimensional equidistribution up to 32-bit accuracy.

* **Internal State Size:** The internal state consists of an array of $n = 624$ 32-bit unsigned integers:
  $$\text{State Size} = 624 \times 32\text{ bits} = 19,968\text{ bits}$$
  With 31 bits omitted by the linear recurrence constraint, the working state entropy is exactly $19,937$ bits.
* **State Transition (Twist Function):**
  The recurrence relation transitions the state array cyclically using matrix linear operations over the Galois Field $\mathrm{GF}(2)$:
  $$x_{k+n} = x_{k+m} \oplus ((x_k^u \mid x_{k+1}^l) \mathbf{A})$$
  where:
  - $x_k^u$ denotes the most significant bit (bit 31) of $x_k$.
  - $x_{k+1}^l$ denotes the lower 31 bits (bits 0 to 30) of $x_{k+1}$.
  - $\mid$ denotes bitwise concatenation.
  - $m = 397$ is the middle offset.
  - $\mathbf{A}$ is the companion matrix in rational normal form:
    $$\mathbf{x} \mathbf{A} = \begin{cases} \mathbf{x} \gg 1 & \text{if least significant bit of } \mathbf{x} = 0 \\ (\mathbf{x} \gg 1) \oplus \mathbf{a} & \text{if least significant bit of } \mathbf{x} = 1 \end{cases}$$
    with twist vector $\mathbf{a} = \mathtt{0x9908B0DF}$.

* **Tempering Transformation (Output Generation):**
  To improve linear complexity and spectral properties, each raw state word $x$ undergoes four successive invertible bitwise transformations (tempering) before outputting 32-bit integer $y$:
  $$\begin{aligned}
  y_1 &= x \oplus ((x \gg u) \ \& \ d) \\
  y_2 &= y_1 \oplus ((y_1 \ll s) \ \& \ b) \\
  y_3 &= y_2 \oplus ((y_2 \ll t) \ \& \ c) \\
  y &= y_3 \oplus (y_3 \gg l)
  \end{aligned}$$
  where standard parameters are:
  - $u = 11$, $d = \mathtt{0xFFFFFFFF}$
  - $s = 7$,  $b = \mathtt{0x9D2C5680}$
  - $t = 15$, $c = \mathtt{0xEFC60000}$
  - $l = 18$

#### 2. Why MT19937 is Completely Broken Cryptographically
1. **Linearity over $\mathrm{GF}(2)$:**
   Every operation in MT19937—state recurrence, twist transformation, and tempering—consists solely of bitwise shifts, bitwise AND masks, and bitwise XOR additions. These are entirely **linear** operations over $\mathbb{F}_2$. There are zero non-linear components (no non-linear S-boxes, modular multiplications, or non-linear Boolean functions).
2. **State Recovery via Untempering (Full State Compromise):**
   Each of the four tempering steps is an invertible bijective mapping $\mathbb{F}_2^{32} \to \mathbb{F}_2^{32}$. Because every bit of $x$ can be recovered from the corresponding output bits of $y$ by applying inverse right/left shifts and masks, an observer who intercepts **624 consecutive 32-bit outputs** (only 2,496 bytes of keystream) can invert the tempering operations, recover the complete internal state array $\mathbf{x}$, and deterministically predict:
   - Every single future output without error.
   - Every single past output by rolling the LFSR backwards.
3. **Failure of the Next-Bit Test:**
   According to cryptographic standards (Yao's Next-Bit Test, 1982), a Cryptographically Secure PRNG (CSPRNG) must ensure that no polynomial-time adversary given the first $k$ output bits can predict the $(k+1)$-th bit with probability better than $1/2 + \epsilon$. MT19937 fails this test completely: given 624 words, the $(625)$-th word can be predicted with probability $1.0$ (100% certainty).

---

### Question 13: Keystream Extraction from Known Plaintext & 16-Bit Seed Search Space

#### 1. Known-Plaintext Attack (KPA) Keystream Extraction
A symmetric stream cipher produces ciphertext $C$ by bitwise XORing plaintext $P$ with keystream $K$:
$$C_i = P_i \oplus K_i$$
Due to the involutory property of XOR ($\forall a, b: (a \oplus b) \oplus b = a$ and $a \oplus a = 0$), the attacker can express the keystream directly in terms of known plaintext and ciphertext:
$$K_i = C_i \oplus P_i$$

* When an attacker knows a target plaintext fragment $P_{\text{known}}$ (e.g., 14 consecutive `'A'` characters, ASCII `0x41`), the corresponding candidate keystream fragment is directly computable:
  $$K_{\text{cand}}[j \dots j+13] = C[j \dots j+13] \oplus (\mathtt{0x41} \times 14)$$
* Even if the exact offset of the known pattern is randomized by a variable prefix (5–20 characters in Part A), an attacker can decrypt candidate plaintexts across candidate seeds:
  $$P_{\text{candidate}} = C \oplus \text{Keystream}(\text{seed})$$
  and simply inspect whether the substring `b"AAAAAAAAAAAAAA"` occurs anywhere within $P_{\text{candidate}}$.

#### 2. Search Space of a 16-Bit Seed
A 16-bit seed limits the possible internal initialization states to:
$$|\mathcal{S}| = 2^{16} = 65,536\text{ possible seeds}$$

* **Entropy:**
  $$H(\text{Seed}) = \log_2(65536) = 16\text{ bits}$$
* **Computational Work Factor:**
  Testing each seed requires generating $|C| \le 34$ bytes of keystream and performing 34 XOR operations followed by a substring check.
  - Operations per seed: $\approx 10^2$ CPU instructions.
  - Total computational cost: $\approx 65,536 \times 100 \approx 6.55 \times 10^6$ CPU cycles.
  - On a standard modern processor running at 3.0 GHz, $6.55 \times 10^6$ cycles execute in **less than 0.5 seconds** (measured experimentally at $\approx 0.25 - 0.42$ seconds).
* **Comparison with Cryptographic Security:**
  NIST SP 800-131A requires a minimum security strength of **128 bits** ($2^{128} \approx 3.40 \times 10^{38}$ operations). A 16-bit seed provides a deficiency of 112 bits of entropy, making exhaustive search trivial.

---

### Question 14: Vulnerability of Timestamp-Based PRNG Seeding

When developers use Unix timestamps (e.g., `time(NULL)` or `int(time.time())`) to seed PRNGs for security-sensitive tokens (such as password reset tokens, session IDs, or activation links), the effective search space collapses drastically:

1. **Known Time Window:**
   An adversary requesting or observing a password reset token knows the approximate wall-clock time $T_{\text{obs}}$ when the server processed the request (e.g., via HTTP `Date` response headers, network packet timestamps, or local clock synchronization).
2. **Entropy Collapse:**
   If the attacker bounds the token generation event to within a standard $\pm 5$ minute window ($\pm 300$ seconds) around $T_{\text{obs}}$:
   $$\text{Candidate Seeds} = 2 \times 300 + 1 = 601\text{ candidates}$$
   The effective entropy is:
   $$H(\text{Seed}) = \log_2(601) \approx 9.23\text{ bits}$$
3. **Full System Compromise:**
   Testing 601 seeds takes less than **4 milliseconds** on any standard workstation. Even if the attacker only knows the date of generation (a 24-hour window), there are only $86,400$ candidate seeds ($< 16.4$ bits of entropy, cracked in $< 1$ second).
   Once the matching seed $T$ is identified, the attacker regenerates the reset token and submits it to reset the victim's account password, resulting in complete account takeover.

---

### Question 15: Pseudocode for Seed Recovery and Token Prediction

#### Algorithm 1: MT19937 Stream Cipher (Encryption & Decryption)
```text
Algorithm: MT19937_XOR_Cipher(Data, Seed)
Input: Byte array Data of length L, 32-bit integer Seed
Output: Byte array Result of length L

1: Instantiate PRNG = MT19937(Seed)
2: Keystream = Array of size L
3: for i = 0 to L - 1 do
4:     Keystream[i] = PRNG.ExtractByte()   // Extract 8 bits
5: end for
6: Result = Array of size L
7: for i = 0 to L - 1 do
8:     Result[i] = Data[i] XOR Keystream[i]
9: end for
10: return Result
```

#### Algorithm 2: Known-Plaintext 16-Bit Seed Recovery (Part A)
```text
Algorithm: Recover16BitSeed(Ciphertext, KnownPattern)
Input: Ciphertext bytes C, Target sequence P_known = "AAAAAAAAAAAAAA"
Output: Recovered Seed S, Decrypted Plaintext P

1: L = Length(C)
2: for CandidateSeed = 0 to 65535 do
3:     PRNG = MT19937(CandidateSeed)
4:     Keystream = Array of size L
5:     for i = 0 to L - 1 do
6:         Keystream[i] = PRNG.ExtractByte()
7:     end for
8:     CandidatePlaintext = Array of size L
9:     for i = 0 to L - 1 do
10:        CandidatePlaintext[i] = C[i] XOR Keystream[i]
11:    end for
12:    if KnownPattern is a substring of CandidatePlaintext then
13:        return (CandidateSeed, CandidatePlaintext)
14:    end if
15: end for
16: return (FAILURE, NULL)
```

#### Algorithm 3: Predictable Reset Token Generation (Part B)
```text
Algorithm: GenerateResetToken(Timestamp T)
Input: Integer Unix timestamp T (seconds)
Output: 16-byte Reset Token TokenBytes

1: PRNG = MT19937(T)
2: TokenBytes = Array of size 16
3: for i = 0 to 15 do
4:     TokenBytes[i] = PRNG.ExtractByte()  // 8-bit output
5: end for
6: return TokenBytes
```

#### Algorithm 4: Windowed Timestamp Token Prediction Attack (Part B)
```text
Algorithm: PredictTokenFromTimestampWindow(ObservedToken, ApproxTime T_approx, Radius Delta)
Input: 16-byte ObservedToken, Approximate timestamp T_approx, Window radius Delta (300s)
Output: Recovered timestamp T_seed, Verification status

1: StartTime = T_approx - Delta
2: EndTime   = T_approx + Delta
3: CandidatesTested = 0
4: for CandidateT = StartTime to EndTime do
5:     CandidatesTested = CandidatesTested + 1
6:     CandToken = GenerateResetToken(CandidateT)
7:     if CandToken == ObservedToken then
8:         // Verification step
9:         VerifyToken = GenerateResetToken(CandidateT)
10:        Assert(VerifyToken == ObservedToken)
11:        return (CandidateT, CandidatesTested, SUCCESS)
12:    end if
13: end for
14: return (NULL, CandidatesTested, FAILURE)
```

---

## 5. Lab Demonstration & Submission Evidence

### Requirement 16: Source Code, Encryption/Decryption, Plaintext and Ciphertext
The core encryption/decryption module is implemented in [`attacks/mt19937_stream_cipher/src/mt19937_cipher.py`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/src/mt19937_cipher.py).

#### Encryption and Decryption Roundtrip Verification:
- **Test Message:** `CryptoLabX Group 07: Cryptographic Stream Cipher Verification Message 2026!`
- **Test Seed:** `0xC001` (`49153`)
- **Ciphertext (Hex):** `f8b68e06a2d8ab94b76f2bd080a0b094405c7d22e9cc96427f10ece313c127b0...`
- **Decrypted Message:** `CryptoLabX Group 07: Cryptographic Stream Cipher Verification Message 2026!`
- **Result:** Exact identity confirmed ($D(E(M)) = M$).

#### Self-Generated Target Plaintext with Random Prefix + 14 'A's:
- **Random Prefix (5–20 chars):** `b'B^THS7'` (length 6)
- **Known Plaintext Suffix:** `b'AAAAAAAAAAAAAA'` (length 14)
- **Full Plaintext:** `b'B^THS7AAAAAAAAAAAAAA'` (length 20)
- **Plaintext (Hex):** `425e544853374141414141414141414141414141`
- **Random 16-bit Seed Chosen:** `0x52C8` (`21192`)
- **Ciphertext (Hex):** `de366a3cdf06f638335cfe8df2eda1da62ff3447`

---

### Requirement 17: Demonstrated Recovered Seed and Verified Full Plaintext
- **Target Signature Checked:** `b'AAAAAAAAAAAAAA'`
- **Total Search Space:** $2^{16} = 65,536$ candidate seeds
- **Seeds Evaluated Before Hit:** `21,193` seeds
- **Search Execution Time:** `0.2431` seconds
- **Effective Search Rate:** `87,182` seeds/second
- **Recovered Seed:** `0x52C8` (`21192`) $\to$ **EXACT MATCH** with chosen seed
- **Decrypted Plaintext:** `b'B^THS7AAAAAAAAAAAAAA'` $\to$ **EXACT MATCH** with original plaintext
- **Verification Checks:**
  - Seed Match: `PASSED`
  - Plaintext Match: `PASSED`
  - 14-Character Known Sequence Presence: `PASSED`

---

### Requirement 18: Demonstrated Predictable Reset Token Attack
The token generation and prediction module is implemented in [`attacks/mt19937_stream_cipher/src/password_reset_token.py`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/src/password_reset_token.py).

#### Simulated Token Generation:
- **Recorded Timestamp $T$:** `1793858936` (Unix seconds)
- **UTC Date / Time:** `2026-11-05 06:08:56 UTC`
- **Generated 16-byte Token (Hex):** `9ef15af61eb63a0021fdec496e53ba3b`

#### Intercepted Token Interval Attack:
- **Attacker Reference Time:** `1793858978` (42 seconds post-generation)
- **Search Interval Bounds:** `[1793858678, 1793859278]` ($\pm 300$ seconds)
- **Search Radius:** $\pm 300$ seconds ($601$ candidate seeds)
- **Candidates Tested:** `259` candidates
- **Cracking Time:** `2.836 ms` (`0.002836` seconds)
- **Cracking Throughput:** `91,312` candidate tokens/second
- **Recovered Timestamp:** `1793858936` $\to$ **EXACT MATCH**
- **Regenerated Token (Hex):** `9ef15af61eb63a0021fdec496e53ba3b`
- **Regeneration Byte-for-Byte Check:** `VERIFIED MATCH`

---

### Requirement 19: Submission Files, Output Logs & Reproducibility

| Artifact | Location | Purpose |
| :--- | :--- | :--- |
| **Part A Source** | [`src/mt19937_cipher.py`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/src/mt19937_cipher.py) | Stream cipher XOR engine & 16-bit seed brute-force cracker |
| **Part B Source** | [`src/password_reset_token.py`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/src/password_reset_token.py) | Timestamp token generator & interval cracking attack |
| **Unified Runner** | [`src/run_assignment10.py`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/src/run_assignment10.py) | Automated test suite and demonstration generator |
| **Jupyter Notebook** | [`assignment10_notebook.ipynb`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/assignment10_notebook.ipynb) | Interactive notebook covering Questions 12–19 |
| **Part A Logs** | [`outputs/part_a_stream_cipher_results.txt`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/outputs/part_a_stream_cipher_results.txt) | Detailed verification transcript for Part A |
| **Part B Logs** | [`outputs/part_b_token_prediction_results.txt`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/outputs/part_b_token_prediction_results.txt) | Detailed interval search & candidate logs for Part B |
| **Full Output** | [`outputs/full_demonstration_output.txt`](file:///Users/kunalsachan/Desktop/crypto%20lab/CryptoLabX_Group07/attacks/mt19937_stream_cipher/outputs/full_demonstration_output.txt) | Complete execution transcript of the entire laboratory suite |

---

## 6. Secure Cryptographic Alternatives

To prevent these critical vulnerabilities in real-world applications:
1. **Never use MT19937, `rand()`, or `random` for cryptographic primitives, keys, or security tokens.**
2. **Use Cryptographically Secure PRNGs (CSPRNGs):**
   - **Python:** Use the `secrets` module (`secrets.token_bytes(16)` or `secrets.token_hex(16)`) or `os.urandom(16)`.
   - **Linux / Unix:** Read directly from `/dev/urandom` or call `getrandom(2)`.
   - **Windows:** Use the Windows Cryptography Next Generation (CNG) `BCryptGenRandom` API.
3. **Seed Entropy:** Ensure seeds and secret keys have at least **128 to 256 bits of true physical entropy** sourced from hardware interrupts, thermal noise, or OS entropy pools.
4. **Stream Ciphers:** Replace toy PRNG XOR ciphers with standardized, cryptanalytically scrutinized stream ciphers such as **ChaCha20-Poly1305** (RFC 8439) or **AES-GCM / AES-CTR** (NIST SP 800-38D).
