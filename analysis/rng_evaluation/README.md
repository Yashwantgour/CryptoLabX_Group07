# Lab Assignment: Evaluation of Operating-System Random-Number Generation (RNG) Mechanisms

**CryptoLabX - Cryptography Laboratory (22CPP307)**  
**Group Number:** Group 07  
**Team Members:**  
- Yashwant Gour (Roll No: `2024ucp1732`)  
- Kunal Sachan (Roll No: `2024ucp1547`)  

---

## 1. Objective
To evaluate operating-system cryptographically secure random-number generation (CSPRNG) mechanisms—specifically **Linux/Unix `/dev/urandom`**, **OpenSSL's `rand` utility**, and **Windows CNG / .NET cryptographic RNG API**—and investigate their statistical properties and suitability for cryptographic applications.

---

## 2. Directory Structure
```
analysis/rng_evaluation/
├── data/
│   ├── urandom_1mb.bin           # 1 MB random data from /dev/urandom
│   ├── openssl_1mb.bin           # 1 MB random data from OpenSSL rand
│   └── windows_cng_1mb.bin       # 1 MB random data from Windows CNG / .NET API
├── outputs/
│   ├── results_summary.txt       # Full generated analysis summary
│   └── byte_frequency.csv        # Detailed byte frequency table (0-255)
├── src/
│   ├── generate_data.py          # Cross-platform 1 MB generation script
│   ├── generate_windows_cng.ps1  # Windows PowerShell script using .NET RNG
│   └── analyze_rng.py            # Complete statistical analysis & test suite
└── README.md                     # Documentation & Laboratory Notebook Guide
```

---

## 3. How to Execute

### Step 1: Generate 1 MB Random Data
From the terminal:
```bash
cd analysis/rng_evaluation
python3 src/generate_data.py
```
*Alternatively, you can generate manually:*
- **Linux / macOS (`/dev/urandom`):**
  ```bash
  head -c 1048576 /dev/urandom > data/urandom_1mb.bin
  # Or: dd if=/dev/urandom of=data/urandom_1mb.bin bs=1048576 count=1
  ```
- **OpenSSL CLI:**
  ```bash
  openssl rand -out data/openssl_1mb.bin 1048576
  ```
- **Windows PowerShell (CNG / .NET):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File src/generate_windows_cng.ps1
  ```

### Step 2: Run Statistical Analysis Suite
Run interactively (menu-driven) or non-interactively:
```bash
./src/analyze_rng.py --all
```
Or directly launch interactive CLI:
```bash
python3 src/analyze_rng.py
```

---

## 4. Experimental Results (For Laboratory Notebook)

### Table 1: Comprehensive Summary Comparison
*(Copy this table directly into your physical Laboratory Notebook)*

| Metric / Statistical Test | Theoretical / Ideal | Linux `/dev/urandom` | OpenSSL `rand` | Windows CNG / .NET | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sample Size (Bytes)** | $1,048,576$ (1 MB) | $1,048,576$ | $1,048,576$ | $1,048,576$ | Complete |
| **Sample Size (Bits)** | $8,388,608$ bits | $8,388,608$ | $8,388,608$ | $8,388,608$ | Complete |
| **Shannon Entropy** | $8.000000$ bits/byte | **$7.999842$** | **$7.999813$** | **$7.999847$** | **PASS** ($>99.99\%$) |
| **Expected Byte Frequency ($E_i$)** | $4096.0$ | $4096.0$ | $4096.0$ | $4096.0$ | Exact |
| **Observed Byte Std Dev** | $\approx 63.87$ | $60.62$ | $65.89$ | $59.60$ | Normal |
| **Chi-Square Stat ($\chi^2$, df=255)** | $\le 293.25$ ($\alpha=0.05$) | **$229.71$** | **$271.38$** | **$222.00$** | **PASS** ($\chi^2 < \chi^2_{crit}$) |
| **Chi-Square P-Value** | $p \ge 0.01$ | $0.8707$ | $0.2298$ | $0.9331$ | **PASS** (Uniform) |
| **Bit 1s Proportion ($\pi$)** | $0.500000$ ($50.0\%$) | $0.499884$ ($49.988\%$) | $0.499933$ ($49.993\%$) | $0.500015$ ($50.002\%$) | Balanced |
| **NIST Monobit Stat ($S_{obs}$)** | $\le 2.5758$ ($\alpha=0.01$) | $0.6712$ | $0.3895$ | $0.0870$ | Minimal Bias |
| **NIST Monobit P-Value** | $p \ge 0.01$ | $0.5021$ | $0.6969$ | $0.9307$ | **PASS** (Random) |
| **NIST Runs Test P-Value** | $p \ge 0.01$ | $0.1814$ | $0.3452$ | $0.4287$ | **PASS** (Random) |
| **Serial Correlation ($r_1$)** | $|r_1| < 0.001953$ | **$-0.000515$** | **$+0.000228$** | **$-0.001797$** | **PASS** (Uncorrelated) |
| **2-Byte Pattern Coverage** | $65,536$ ($100\%$) | $65,522$ ($99.98\%$) | $65,518$ ($99.97\%$) | $65,515$ ($99.97\%$) | Complete |
| **4-Byte Block Collisions** | $\approx 8.00$ (Birthday Bound)| $9$ | $6$ | $9$ | Normal Collision Rate |

---

## 5. Statistical Tests & Interpretations (Task 3)

### 1. Byte-Frequency Distribution & Chi-Square Goodness-of-Fit Test
- **Formula:** 
  $$\chi^2 = \sum_{i=0}^{255} \frac{(O_i - E_i)^2}{E_i}$$
  where $O_i$ is the count of byte $i$, $N = 1,048,576$, and $E_i = \frac{N}{256} = 4096.0$.
- **Degrees of Freedom:** $df = 256 - 1 = 255$.
- **Critical Value:** At significance level $\alpha = 0.05$, $\chi^2_{crit} = 293.25$.
- **Interpretation:** For all three sources, the calculated $\chi^2$ values ($229.71$, $271.38$, and $222.00$) fall well below the critical value $293.25$, and $p$-values are $> 0.01$. This confirms that byte values from $0$ to $255$ are uniformly distributed with no statistical skew.

### 2. Shannon Entropy
- **Formula:**
  $$H = -\sum_{i=0}^{255} p_i \log_2(p_i) \quad \text{bits/byte}$$
- **Maximum Theoretical Entropy:** $\log_2(256) = 8.000000$ bits/byte.
- **Interpretation:** All datasets achieve entropy values $\ge 7.99981$ bits/byte ($>99.997\%$ of theoretical maximum). This proves virtually zero information redundancy or predictability per byte.

### 3. NIST SP 800-22 Monobit Frequency Test
- **Formula:**
  $$S_{obs} = \frac{|c_1 - c_0|}{\sqrt{M}}, \quad P\text{-value} = \text{erfc}\left(\frac{S_{obs}}{\sqrt{2}}\right)$$
  where $M = 8,388,608$ total bits, $c_1$ = number of ones, $c_0$ = number of zeros.
- **Decision Rule:** Reject randomness if $P\text{-value} < 0.01$.
- **Interpretation:** The proportion of ones for all generators is within $\pm 0.02\%$ of $0.5$. With $P\text{-values}$ of $0.5021$, $0.6969$, and $0.9307$, the null hypothesis of bit equality cannot be rejected.

### 4. NIST SP 800-22 Runs Test
- **Formula:**
  Tests whether the total count of uninterrupted identical bit runs ($V_{obs}$) deviates from the expected value for an independent sequence:
  $$Z = \frac{|V_{obs} - 2 M \pi (1 - \pi)|}{2 \sqrt{2 M} \pi (1 - \pi)}, \quad P\text{-value} = \text{erfc}(Z)$$
- **Interpretation:** The transitions between consecutive bits fluctuate as expected for a memoryless Bernoulli process. $P\text{-values}$ ($0.1814$, $0.3452$, $0.4287$) are substantially above $0.01$, passing the runs test.

### 5. Serial Correlation (Lag-1 Autocorrelation)
- **Formula:**
  $$r_1 = \frac{\sum_{i=0}^{N-2}(X_i - \bar{X})(X_{i+1} - \bar{X})}{\sum_{i=0}^{N-1}(X_i - \bar{X})^2}$$
- **Acceptance Bound:** $|r_1| \le \frac{2}{\sqrt{N}} = \frac{2}{\sqrt{1048576}} \approx 0.001953$.
- **Interpretation:** The calculated coefficients are $-0.000515$, $+0.000228$, and $-0.001797$. Because all values satisfy $|r_1| < 0.001953$, there is no linear dependency between adjacent byte emissions.

### 6. Repeated Patterns & Collision Analysis
- **2-Byte Patterns (16-bit):** In $524,288$ non-overlapping pairs across $65,536$ states, each generator covers $>99.97\%$ of all possible 16-bit patterns with an observed maximum count of $22-23$ occurrences (expected average is $8.0$).
- **4-Byte Patterns (32-bit Words):** By the **Birthday Paradox**, among $n = 262,144$ blocks drawn from $2^{32} \approx 4.29 \times 10^9$ possibilities:
  $$\text{Expected Collisions} \approx \frac{n(n-1)}{2 \times 2^{32}} \approx \frac{(262144)^2}{2 \times 4294967296} \approx 8.00$$
  The observed collision counts ($9$, $6$, and $9$) match the theoretical Poisson expectation, proving that repeating patterns occur solely due to statistical probability rather than algorithm repetition or short cycles.

---

## 6. Architecture & Management of CSPRNGs (Task 4)

### A. Linux CSPRNG Architecture (`/dev/urandom`, `getrandom()`)
1. **Entropy Harvesting Sources:**
   - Linux collects nondeterministic environmental noise from device drivers: inter-interrupt timing, keyboard keystroke latencies, mouse movements, disk seek timings, and hardware jitter.
   - Modern kernels (Linux 5.17+) also incorporate CPU instruction entropy via `RDRAND` / `RDSEED` and cycle counters (`RDTSC`).
2. **Internal Cryptographic Primitive:**
   - Historically, Linux used SHA-1 based LFSR pools.
   - Since Linux 4.8 / 5.17+, the Linux CSPRNG uses **ChaCha20** (designed by Daniel J. Bernstein) and **BLAKE2s** for mixing and entropy extraction (implemented by Jason A. Donenfeld).
3. **Reseeding & Forward Secrecy:**
   - The kernel maintains a primary input pool and per-NUMA/per-core ChaCha20 states.
   - After emitting output, the internal ChaCha20 state is overwritten immediately (**backtracking resistance** / forward secrecy).
   - The generator is reseeded automatically every 60 seconds or whenever fresh entropy arrives.
4. **Interface Differences:**
   - `/dev/urandom`: Never blocks once seeded; safe for virtually all cryptographic operations (session keys, nonces, IVs).
   - `/dev/random`: Historically blocked when estimated entropy was low; in modern kernels, it only blocks at boot until the CRNG is initially seeded (128 bits), then behaves like `/dev/urandom`.
   - `getrandom(2)` system call: Avoids file descriptor exhaustion and security issues with chroot; can block until initialized unless `GRND_NONBLOCK` is specified.

### B. Windows CSPRNG Architecture (CNG / `BCryptGenRandom` / .NET)
1. **Entropy Harvesting Sources:**
   - Windows collects root entropy at boot and runtime through the kernel driver `cng.sys`.
   - Sources include: TPM (Trusted Platform Module) hardware seed, UEFI platform entropy, high-resolution performance counters (`QueryPerformanceCounter`), thread scheduling interrupts, and Intel/AMD hardware instructions (`RDRAND`/`RDSEED`).
2. **Internal Cryptographic Primitive:**
   - Windows Cryptography Next Generation (CNG) uses Microsoft's **SymCrypt** core cryptographic library.
   - The underlying DRBG algorithm adheres to **NIST SP 800-90A AES-256 in Counter (CTR) Mode** (AES-CTR DRBG).
3. **State Management & Per-Processor Architecture:**
   - To eliminate lock contention in multi-threaded environments, Windows assigns independent PRNG instances per logical processor.
   - Reseeding occurs continuously from the kernel entropy pool.
   - Forward and backward secrecy are enforced through regular key updates and zeroization of intermediate states.
4. **User-Space APIs:**
   - C / Native C++: `BCryptGenRandom()` with `BCRYPT_USE_SYSTEM_PREFERRED_RNG`.
   - .NET / C# / PowerShell: `System.Security.Cryptography.RandomNumberGenerator.Create()`.
   - Legacy Win32: `CryptGenRandom()` from CryptoAPI (deprecated in favor of CNG).

---

## 7. Comparison: Linux vs. Windows CSPRNG (Task 5)

| Feature | Linux (`/dev/urandom` / `getrandom`) | Windows CNG (`BCryptGenRandom` / .NET) |
| :--- | :--- | :--- |
| **Kernel Implementation** | `drivers/char/random.c` | `cng.sys` (Kernel Mode) |
| **Core Algorithm** | **ChaCha20** stream cipher + **BLAKE2s** | **NIST SP 800-90A AES-256 CTR_DRBG** (SymCrypt) |
| **Standard Compliance** | De facto cryptographic standard (RFC 8439) | FIPS 140-2 / 140-3, NIST SP 800-90A |
| **Primary Interfaces** | `/dev/urandom`, `getrandom()` | `BCryptGenRandom`, `RandomNumberGenerator` (.NET) |
| **Blocking Behavior** | Blocks only before initial 128-bit seeding at boot | Never blocks in user space (initialized during boot) |
| **State Partitioning** | Primary pool + per-NUMA/CPU CRNG instances | Per-core PRNG state instances |
| **Forward Secrecy** | Immediate key erasure after block generation | State updating per NIST SP 800-90A specifications |

---

## 8. Why Passing Statistical Tests Does NOT Guarantee Cryptographic Security (Task 5)
*(Crucial Viva and Notebook Section)*

### 1. Distinction: Empirical Randomness vs. Cryptographic Unpredictability
- **Statistical tests** (such as Chi-Square, Shannon Entropy, and NIST SP 800-22) are **black-box empirical tests**. They only verify whether the generated sequence is **statistically indistinguishable from a uniform distribution** over the tested sample size.
- **Cryptographic security** requires **unpredictability**: an adversary with unlimited previous outputs, knowledge of the algorithm, and substantial computational resources must not be able to predict the next bit ($n+1$) with probability significantly greater than $0.5$ (**Next-Bit Test** / Yao's Theorem).

### 2. Counter-Examples Proving the Distinction

#### Counter-Example A: Expansions of Mathematical Constants ($\pi, e, \sqrt{2}$)
- The decimal and binary expansions of $\pi$ pass virtually all standard statistical suites (uniform digit distribution, low serial correlation, high entropy).
- **Security:** Zero! An attacker who recognizes the sequence or knows the formula can calculate any future bit deterministically with $100\%$ accuracy.

#### Counter-Example B: AES-CTR with a Known Key
- Consider AES-256 operating in Counter mode:
  $$C_i = \text{AES}_{K}(i) \quad \text{for } i = 1, 2, 3, \dots$$
- If the key $K$ is static and publicly known (e.g., $K = 0x00\dots00$):
  - The output will pass **all** NIST SP 800-22 tests, have an entropy of $7.9999$ bits/byte, and pass every Chi-Square test because AES is a strong pseudo-random permutation.
  - Yet it provides **0 bits of cryptographic security** because any observer can compute future numbers trivially.

#### Counter-Example C: Linear Congruential Generators (LCG) & Mersenne Twister (MT19937)
- Standard programming language generators (e.g., `rand()` in C or `random` in Python) pass many basic statistical uniformity tests.
- However, after observing just 624 32-bit outputs of Mersenne Twister, the entire internal state matrix is reconstructed, and all past and future outputs are completely revealed.

#### Counter-Example D: Backdoored CSPRNGs (NIST Dual_EC_DRBG)
- The NSA-designed **Dual_EC_DRBG** generator passed all NIST statistical tests with flying colors.
- However, the algorithm contained a mathematical relationship between two elliptic curve points ($P$ and $Q$ such that $eP = Q$). Anyone possessing the secret scalar $e$ could determine the internal state from just 32 bytes of public output.

### 3. State Compromise & Secrecy Properties
Statistical tests evaluate a static file and cannot test dynamic security guarantees:
- **Forward Secrecy (Backtracking Resistance):** If an attacker compromises the current internal state at time $t$, they must not be able to deduce outputs generated prior to $t$.
- **Backward Secrecy (Prediction Resistance):** If the internal state is compromised at time $t$, future outputs must become unpredictable once fresh entropy is reseeded.
- Statistical tests cannot assess whether an implementation zeroizes memory or resists side-channel attacks (e.g., cache timing, power analysis).

---

## 9. Conclusion
1. **Linux `/dev/urandom`**, **OpenSSL `rand`**, and **Windows CNG / .NET** all demonstrate near-ideal statistical properties with maximum Shannon entropy ($\approx 7.9998$ bits/byte), balanced bit distributions, zero serial correlation, and full compliance with Chi-Square and NIST SP 800-22 tests.
2. While statistical tests are necessary to detect flaws, biases, and poor implementations, **cryptographic security relies on computational hardness, irreversible state evolution (ChaCha20 / AES-CTR), robust entropy harvesting, and forward/backward secrecy.**
