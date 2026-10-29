# Lab Assignment: Cryptographic Prime Generation Using Miller–Rabin

**CryptoLabX - Cryptography Laboratory (22CPP307)**  
**Group Number:** Group 07  
**Primary Author for this Lab:** Kunal Sachan (Roll No: `2024ucp1547`, Email: `2024ucp1547@mnit.ac.in`)  
**Teammate:** Yashwant Gour (Roll No: `2024ucp1732`, Email: `2024ucp1732@mnit.ac.in`)  

---

## 1. Objective
To generate a cryptographically secure probable prime integer of exactly **512-bit length** using the probabilistic **Miller–Rabin primality test**, verify its exact bit length, and validate the result through multiple bases and independent trusted cryptographic libraries.

---

## 2. Directory Structure
```
math/prime_generation/
├── outputs/
│   ├── experimental_results.txt    # Submission results table & verification logs
│   └── prime_candidate_512bit.txt  # Full decimal, hex, and binary representations
├── src/
│   └── miller_rabin.py             # Complete implementation, tests, and CLI
└── README.md                       # Comprehensive documentation & notebook report
```

---

## 3. How to Execute in Terminal
You can run the script directly from your terminal:
```bash
cd math/prime_generation
./src/miller_rabin.py
```
*Or via standard python:*
```bash
python3 src/miller_rabin.py
```

---

## 4. Mathematical Background & Algorithm

### The Miller–Rabin Primality Test
The Miller–Rabin test is an efficient probabilistic primality test based on properties of strong pseudoprimes and Fermat's Little Theorem.

#### Decomposition
Given an odd integer $n > 2$, write $n - 1$ as:
$$n - 1 = 2^s \cdot d$$
where $d$ is odd and $s \ge 1$.

#### Test Condition
For a randomly chosen base $a \in [2, n - 2]$:
1. Compute $x \equiv a^d \pmod n$.
2. If $x \equiv 1 \pmod n$ or $x \equiv n - 1 \pmod n$, then $n$ passes the test for base $a$.
3. Otherwise, square $x$ iteratively up to $s - 1$ times:
   $$x \leftarrow x^2 \pmod n$$
   If at any point $x \equiv n - 1 \pmod n$, then $n$ passes the test for base $a$.
4. If the loop terminates without encountering $n - 1$, then $n$ is **definitely composite**, and $a$ is a witness to the compositeness of $n$.

#### Error Probability & Security Guarantee
- For any odd composite $n$, the probability that a randomly chosen base $a$ fails to detect compositeness is at most $\frac{1}{4}$.
- By performing $k$ independent rounds with randomly selected bases, the probability that a composite number passes all $k$ rounds is bounded by:
  $$P(\text{False Positive}) \le \left(\frac{1}{4}\right)^k = 2^{-2k}$$
- For $k = 40$ rounds:
  $$P(\text{False Positive}) \le 4^{-40} = 2^{-80} \approx 8.27 \times 10^{-25}$$
  This strictly satisfies the primality testing requirements of **NIST FIPS 186-4 (Digital Signature Standard)**.

---

## 5. Experimental Results (What to Submit)

*(Submit this table in your Laboratory Notebook)*

| Parameter | Value |
| :--- | :--- |
| **Assigned bit length** | **512 bits** |
| **Generated prime candidate (Decimal)** | `7855342889084485970064689556357049172967106163340113850932362847137313673009891506764439218973301392637769667249499158632930629413202301520934805603001743` |
| **Generated prime candidate (Hex)** | `0x95fc1dc0d1030ccc1725c38bf1b0755d10744d0a9669b6cba837131a3b1e009d4f2cc619eb67cb80b1f0c4e8ff687eafc83b5c36224f67d2e983d4ded6eea58f` |
| **Actual bit length of the candidate** | **512 bits** |
| **Number of candidates tested** | **129 candidates** (Pre-filtered with small primes) |
| **Number of Miller–Rabin rounds** | **40 rounds** |
| **Total execution time** | **0.0272 seconds** |

---

## 6. Verification

### Verification 1: Demonstrate Exact Bit Length
To guarantee the number has an exact length of 512 bits:
1. **Bit Length Formula:**
   $$\text{bit\_length}(p) = \lfloor \log_2(p) \rfloor + 1 = 512$$
2. **Range Inequality:**
   $$2^{511} \le p < 2^{512}$$
   - **Lower Bound ($2^{511}$):**
     `6703903964971298549787012499102923063739682910296196688861780721860882015036773488400937149083451713845015929093243025426876941405973284973216824503042048`
   - **Generated Prime ($p$):**
     `7855342889084485970064689556357049172967106163340113850932362847137313673009891506764439218973301392637769667249499158632930629413202301520934805603001743`
   - **Upper Bound ($2^{512} - 1$):**
     `13407807929942597099574024998205846127479365820592393377723561443721764030073546976801874298166903427690031858186486050853753882811946569946433649006084095`
   - **Status:** **PASSED** ($2^{511} \le p < 2^{512}$).
3. **Parity Check:**
   $$p \equiv 1 \pmod 2$$
   The least significant bit is set to 1, ensuring the candidate is strictly odd.

---

### Verification 2: Show that it Passes Miller–Rabin for Specified Bases
The candidate was verified individually against the first 12 prime bases:

| Base ($a$) | Modular Result | Primality Status |
| :---: | :---: | :---: |
| **$a = 2$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 3$** | $x \equiv 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 5$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 7$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 11$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 13$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 17$** | $x \equiv 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 19$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 23$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 29$** | $x \equiv 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 31$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |
| **$a = 37$** | $x \equiv n - 1 \pmod n$ | **PASSED (Probable Prime)** |

---

### Verification 3: Independent Primality Verification
1. **OpenSSL Cryptographic Utility:**
   The generated hexadecimal value was submitted directly to OpenSSL's trusted `openssl prime` tool:
   ```bash
   openssl prime -hex 95fc1dc0d1030ccc1725c38bf1b0755d10744d0a9669b6cba837131a3b1e009d4f2cc619eb67cb80b1f0c4e8ff687eafc83b5c36224f67d2e983d4ded6eea58f
   ```
   **Output:**
   ```text
   95FC1DC0D1030CCC1725C38BF1B0755D10744D0A9669B6CBA837131A3B1E009D4F2CC619EB67CB80B1F0C4E8FF687EAFC83B5C36224F67D2E983D4DED6EEA58F is prime
   ```
   **Result:** **PASSED** (Independently confirmed prime by OpenSSL).

2. **Baillie–PSW / Strong Lucas Test:**
   - Evaluated using Lucas sequence parameters $(P = 1, Q = -1)$ with Jacobi symbol $(D/p) = -1$.
   - **Result:** **PASSED** (No composite counterexample has ever been found for Baillie-PSW).

3. **Fermat Primality Test:**
   - Evaluated $a^{p-1} \equiv 1 \pmod p$ across multiple prime bases.
   - **Result:** **PASSED**.

---

## 7. Conclusion
The 512-bit prime candidate was successfully generated in **0.0272 seconds** after testing **129 candidates**. It fulfills all cryptographic bit-length, parity, and primality criteria with an error probability bounded by $P < 2^{-80}$, confirmed independently by the OpenSSL cryptographic core.
