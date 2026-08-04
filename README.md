# Half-Period Involutions in Inert Lucas Sequences

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Companion repository for the paper **"Half-Period Involutions in Inert Lucas Sequences"** by Majid Ghandali.

---

## Abstract

This repository accompanies the paper *Half-Period Involutions in Inert Lucas Sequences* and provides a fully reproducible computational verification of the main theorem.

For an odd prime $p$, consider a Lucas sequence $U_n(P,Q)$ with discriminant:
$$D=P^2-4Q$$

When:
$$\chi_p(D)=-1, \qquad Q\equiv -1 \pmod p$$

the associated companion matrix:
A= $\begin{pmatrix} P & -Q \\ 1 & 0 \end{pmatrix}$

satisfies the structural identity:
$$A^{T/2}=-I$$

where $T$ denotes the spectral period of the inert eigenvalue. This involution induces exact half-period sign reversal:
$$U_{n+T/2}\equiv -U_n \pmod p$$

and consequently yields exact cancellation of all odd observables over a full orbit. The repository contains verification scripts, numerical examples, exported datasets, and reproducible computational artifacts corresponding to every step of the proof pipeline.

---

## Main Theorem

Let $D=P^2-4Q$, and let $p$ be an odd prime satisfying:

$$\chi_p(D)=-1, \qquad Q\equiv -1 \pmod p$$

If $\lambda$ is a root of $x^2-Px+Q$ in $$\mathbb{F}_{p^2}$$ and T = $\{ord}$ $\lambda$, then:

$$A^{T/2}=-I$$

Consequently:

$$U_{n+T/2}\equiv -U_n \pmod p$$

$$V_{n+T/2}\equiv -V_n \pmod p$$

and every odd observable cancels exactly over a complete orbit.

---

## Proof Pipeline

The computational artifact mirrors the logical structure of the paper:

```text
[Inertness]
    ↓
[Norm identity: λ^(p+1) = -1]
    ↓
[-1 ∈ <λ>]
    ↓
[Unique involution]
    ↓
[λ^(T/2) = -1]
    ↓
[A^(T/2) = -I]
    ↓
[Anti-periodicity]
    ↓
[Exact cancellation]
[Step 1: Inertness] ---> [Step 2: F_{p^2} Realization] ---> [Step 3: Norm-Fibre Identity]
|
[Step 6: Anti-Periodicity] <--- [Step 5: Matrix Bridge] <--- [Step 4: Unique Involution]
|
v
[Step 7: Character Cancellation]
```

## Proof Mapping & Structural Pipeline

The verification engine maps directly to the paper's theoretical framework via the following layers:
* **Step 1:** Strict canonical validation of the quadratic non-residuosity ($\chi_p(D) = -1$) and specialization to $Q \equiv -1 \pmod{p}$.
* **Step 2:** Explicit degree-2 finite field extension $\mathbb{F}_{p^2} = \mathbb{F}_p[x] / (x^2 - Px + Q)$ using irreducible characteristic polynomials.
* **Step 3:** Structural derivation of the norm-fibre condition ($\lambda^{p+1} = -1$).
* **Step 4:** Representation of the unique order-2 involution ($\lambda^{T/2} = -1$) in the cyclic subgroup $\langle\lambda\rangle$.
* **Step 5:** Matrix representation projection confirming the central matrix involution $A^{T/2} = -I$.
* **Step 6:** Dynamical state-space vector and sequence projection orbit anti-periodicity ($U_{n+T/2} \equiv -U_n$ and $V_{n+T/2} \equiv -V_n$).
* **Step 7:** Exact character-sum cancellation over a full orbit period whenever $\chi_p(-1) = -1$.

## Prerequisites & Installation

To run this computational proof structure, you need to have **SageMath** (v9.0 or later) installed on your system.

```bash
# Clone the repository
git clone [https://github.com/Majid-Ghandali/lucas-half-period-involutions.git](https://github.com/Majid-Ghandali/lucas-half-period-involutions.git)
cd lucas-half-period-involutions
```
## Usage
​Execute the main verification pipeline directly via SageMath:

```bash
sage verify_theorem_pipeline.sage
```
## Outputs
​The execution automatically benchmarks representative sequences (Fibonacci, Pell, etc.) and performs a systematic scan over doubly-inert Fibonacci primes up to p \le 200, exporting full verifiable matrices to:
​Theorem_pipeline_verification.csv (For tabular integration)
​Theorem_pipeline_verification.json (For exact reproducibility payload).

## Citation 

If you utilize this artifact or the theoretical results in your academic work, please cite the main manuscript and this software package:
@article{ghandali2026half,
  author  = {Ghandali, Majid},
  title   = {Half-Period Involutions in Inert Lucas Sequences},
  journal = {Journal of Number Theory (Preprint)},
  year    = {2026}
}

@software{ghandali_artifact_2026,
  author       = {Ghandali, Majid},
  title        = {Computational Companion for "Half-Period Involutions in Inert Lucas Sequences"},
  month        = jun,
  year         = 2026,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.XXXXXXX},
  url          = {[https://doi.org/10.5281/zenodo.XXXXXXX](https://doi.org/10.5281/zenodo.XXXXXXX)}
}

