# SageMath & Python Toolkit: Lattice Reduction (LLL) for Bitcoin ECDSA (Hidden Number Problem)

## 📌 Context & Overview
This repository provides high-performance tools and mathematical solvers to attack Bitcoin ECDSA private keys using **Lattice Basis Reduction (LLL)** via the **Hidden Number Problem (HNP)** framework.

When ECDSA signatures exhibit partial nonce leakage (e.g. MSB/LSB bits being zero, small nonces, or PRNG bias), brute-force searching is completely bypassed. **SageMath / LLL reduces the geometric basis and recovers the 256-bit private key in milliseconds.**

---

## 🧬 Theoretical Framework: Hidden Number Problem (HNP)

### 1. ECDSA Signature Equation
For the secp256k1 elliptic curve with order $N$:
$$s_i \equiv k_i^{-1} (z_i + r_i \cdot d) \pmod N$$

Rearranging for the secret per-signature nonce $k_i$:
$$k_i \equiv s_i^{-1} z_i + s_i^{-1} r_i \cdot d \pmod N$$

Let $t_i \equiv s_i^{-1} r_i \pmod N$ and $u_i \equiv s_i^{-1} z_i \pmod N$. We obtain the classic **Hidden Number Problem (HNP)**:
$$k_i \equiv t_i \cdot d + u_i \pmod N$$

### 2. Theoretical Bound Requirement
To recover the private key $d$, the total leaked information across $m$ signatures must satisfy:
$$m \cdot b > 256 \quad \text{bits}$$
where:
- $b$ = number of leaked bits per signature nonce $k_i$ ($k_i < N / 2^b$)
- $m$ = total number of collected signatures

| Leaked Bits per Nonce ($b$) | Minimum Signatures Required ($m$) | LLL Execution Time |
| :--- | :--- | :--- |
| **64 bits** (Top 64 bits zero) | **5 signatures** | ~5 ms |
| **32 bits** (Top 32 bits zero) | **9 signatures** | ~50 ms |
| **16 bits** (Top 16 bits zero) | **17 signatures** | ~300 ms |
| **8 bits** (Top 8 bits zero) | **33 signatures** | ~1.5 s |
| **256 bits** (Nonce Reuse: $k_1 = k_2$) | **2 signatures** | Instant (< 1 ms) |

---

## 📐 Kannan's Embedding Matrix Structure

We build a $(m+2) \times (m+2)$ matrix $M$ over $\mathbb{Z}$:

$$M = \begin{pmatrix}
N \cdot 2^b & 0 & \dots & 0 & 0 & 0 \\
0 & N \cdot 2^b & \dots & 0 & 0 & 0 \\
\vdots & \vdots & \ddots & \vdots & \vdots & \vdots \\
0 & 0 & \dots & N \cdot 2^b & 0 & 0 \\
t_1 \cdot 2^b & t_2 \cdot 2^b & \dots & t_m \cdot 2^b & 1 & 0 \\
u_1 \cdot 2^b & u_2 \cdot 2^b & \dots & u_m \cdot 2^b & 0 & X \cdot 2^b
\end{pmatrix}$$

Multiplying by vector $v = (y_1, y_2, \dots, y_m, d, 1)$ produces the target short vector:
$$v M = (k_1 \cdot 2^b, k_2 \cdot 2^b, \dots, k_m \cdot 2^b, d, X \cdot 2^b)$$

Because $k_i < X = N / 2^b$, this vector has norm $\ll \det(M)^{1/(m+2)}$.
**LLL Basis Reduction rearranges the lattice basis and extracts $d$ directly from column $m$ of the reduced matrix!**

---

## 🛠️ Provided Files & Tools

1. **`sage_hnp_solver.sage`**
   - SageMath script for CLI execution (`sage sage_hnp_solver.sage`) or copy-pasting directly into [SageMathCell](https://sagecell.sagemath.org).
2. **`lll_hnp_solver.py`**
   - Pure Python 3 solver using exact rational Gram-Schmidt arithmetic. Runs natively without external binary dependencies.
3. **`test_exact_lll.py`**
   - Benchmark script testing different leakage profiles (64-bit, 32-bit, 16-bit leakage).

---

## 🚀 How to Run

### In Python:
```bash
python lll_hnp_solver.py
```

### In SageMath:
```bash
sage sage_hnp_solver.sage
```

### Online (Web):
1. Open [SageMathCell](https://sagecell.sagemath.org)
2. Copy the content of `sage_hnp_solver.sage` into the box and click **Evaluate**.
