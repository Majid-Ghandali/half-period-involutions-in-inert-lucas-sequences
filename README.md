# Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Preprint and reproducibility materials for **“Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences.”**

This repository accompanies a focused structural note on Lucas recurrences modulo inert primes. It records a half-period matrix involution and organizes two exact mechanisms that force cancellation in full-period character sums.

**Majid Ghandali** · Independent Researcher · Tehran, Iran · 2026  
[ORCID: 0009-0001-1097-1770](https://orcid.org/0009-0001-1097-1770)

**Release status:** preparation branch for the first tagged archival release.  
**Repository DOI:** pending Zenodo archival release.

---

## Why This Repository?

The accompanying manuscript studies the Lucas recurrence

```text
U_0 = 0
U_1 = 1
U_(n+2) = P U_(n+1) - Q U_n
```

and its companion sequence

```text
V_0 = 2
V_1 = P
V_(n+2) = P V_(n+1) - Q V_n
```

at an odd prime `p` for which the discriminant

```text
D = P^2 - 4Q
```

is a quadratic nonresidue modulo `p`.

The manuscript itself contains the mathematical proofs. This repository provides the manuscript source, compiled preprint, and exact-arithmetic verification of the diagnostic examples.

> [!IMPORTANT]
> The computations in this repository verify explicitly stated finite examples. They do not replace the proofs in the accompanying manuscript.

---

## Main Structural Setting

Let

```text
A = [[P, -Q],
     [1,  0]]
```

be the companion matrix modulo `p`, and let

```text
T = ord_GL2(F_p)(A)
```

be its matrix period.

In the inert setting, the manuscript records the half-period criterion

```text
A^m = -I  (mod p)

if and only if

T is even and m = T/2  (mod T).
```

Thus, when `T` is even,

```text
U_(n + T/2) = -U_n  (mod p)
V_(n + T/2) = -V_n  (mod p).
```

---

## Two Exact Cancellation Mechanisms

The manuscript distinguishes two structural mechanisms.

### 1. Half-period translation

If the matrix period `T` is even, translation by `T/2` negates the recurrence values:

```text
U_(n + T/2) = -U_n  (mod p)
V_(n + T/2) = -V_n  (mod p).
```

Therefore, every function satisfying

```text
f(-x) = -f(x)
```

cancels over a complete matrix period.

For the quadratic character, this mechanism applies when

```text
chi_p(-1) = -1,
```

equivalently when

```text
p = 3  (mod 4).
```

### 2. Rank-block scalar propagation

Let `alpha` be the rank of apparition and define the rank multiplier

```text
Lambda = U_(alpha + 1)  (mod p).
```

The classical rank--period--multiplier framework gives

```text
A^alpha = Lambda I  (mod p).
```

Hence, for successive rank blocks,

```text
U_(r + t alpha) = Lambda^t U_r  (mod p)
V_(r + t alpha) = Lambda^t V_r  (mod p).
```

For every multiplicative character `psi`, extended by `psi(0) = 0`, the full-period sums factor as

```text
sum_(n=1)^T psi(U_n)
=
(sum_(t=0)^(omega-1) psi(Lambda)^t)
(sum_(r=1)^alpha psi(U_r)),
```

and similarly for `V_n`, where

```text
T = alpha omega.
```

Thus,

```text
psi(Lambda) != 1
```

forces exact full-period cancellation.

> [!NOTE]
> The rank--period--multiplier framework is classical and is explicitly attributed in the manuscript. This repository does not claim a new classification of rank multipliers or matrix periods.

---

## Diagnostic Examples

The included verifier checks two examples from the manuscript.

| Example | Parameters | Structural role |
|:--|:--|:--|
| Fibonacci modulo 7 | `P = 1`, `Q = -1`, `p = 7` | Half-period quadratic cancellation |
| Scalar example modulo 5 | `P = 1`, `Q = 2`, `p = 5` | Scalar cancellation with `chi_p(-1) = 1` |

The second example shows that scalar rank-block cancellation can occur even when quadratic-character oddness under negation is unavailable.

For

```text
(P, Q, p) = (1, 2, 5),
```

one has

```text
alpha = 6
Lambda = U_7 = 2  (mod 5)
chi_5(Lambda) = -1
chi_5(-1) = 1.
```

Thus the full-period quadratic character sums vanish through scalar rank-block propagation rather than through half-period odd-function pairing.

---

## Quick Start

From the repository root, run:

```bash
python code/verify_examples.py
```

A successful run creates:

```text
results/example_verification.json
```

The verifier uses exact modular arithmetic only and checks the two diagnostic examples described above.

---

## Build the Preprint

The manuscript source is in `manuscript/`.

```bash
cd manuscript

pdflatex Main_P4_Preprint.tex
bibtex Main_P4_Preprint
pdflatex Main_P4_Preprint.tex
pdflatex Main_P4_Preprint.tex
```

The compiled preprint PDF is also included in the repository.

> [!NOTE]
> This is a preprint and reproducibility release. It is not a publisher-formatted version. Journal-facing formatting may change during editorial processing.

---

## Repository Structure

```text
half-period-involutions-in-inert-lucas-sequences/
├── README.md
├── LICENSE
├── CITATION.cff
├── zenodo.json
├── manuscript/
│   ├── Main_P4_Preprint.tex
│   ├── references_P4_Preprint.bib
│   ├── Main_P4_Preprint.bbl
│   └── Main_P4_Preprint.pdf
├── code/
│   └── verify_examples.py
├── results/
│   └── example_verification.json
└── metadata/
    ├── RELEASE_MANIFEST.json
    └── SHA256SUMS.txt
```

---

## Reproducibility Scope

The repository verifies the numerical examples included in the manuscript.

It does not:

- replace the mathematical proofs;
- claim a new theory of Lucas rank, period, or multiplier;
- provide a density theorem, Chebotarev theorem, or Artin-type result;
- include internal recovery records, failed scripts, local paths, or private research governance files.

The accompanying manuscript remains the authoritative source for theorem statements, hypotheses, proofs, and literature positioning.

---

## References and Context

The manuscript places the results within the classical and modern literature on Lucas recurrences, rank, period, multiplier, and character sums, including work by Lucas, Lehmer, Renault, Somer, Fiebig--Mbirika--Spilker, Blackburn--Shparlinski, and Carlo Sanna.

The repository itself should be cited through `CITATION.cff` after the first tagged archival release.

---

## Zenodo Archival Release

A Zenodo DOI will be added after:

1. this branch is merged into `main`;
2. a versioned GitHub Release is created;
3. Zenodo archives the tagged release.

The intended first archival tag is:

```text
v1.0.0-preprint
```

Until then, any DOI placeholder is intentionally absent.

---

## License

All contents of this repository are released under the [MIT License](LICENSE).

---

## Author

**Majid Ghandali**  
Independent Researcher, Tehran, Iran

Email: [majid.ghandali@gmail.com](mailto:majid.ghandali@gmail.com)  
ORCID: [0009-0001-1097-1770](https://orcid.org/0009-0001-1097-1770)
