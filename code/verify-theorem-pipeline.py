# verify-theorem-pipeline.py
"""
Pure-Python companion artifact for:

    Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences
    Majid Ghandali, 2026

Purpose
-------
This verifier implements a layered, exact-arithmetic realization of the
half-period involution path in the specialized branch

    Q ≡ -1  (mod p).

The construction follows the explicit algebraic route:

    inertness
      → irreducible quadratic over F_p
      → explicit realization of F_{p²}
      → norm identity  N(λ) = Q
      → norm-fibre identity  λ^{p+1} = -1   (available when Q ≡ -1)
      → unique order-2 element in the cyclic group ⟨λ⟩
      → λ^{T/2} = -1
      → A^{T/2} = -I  and  A^T = I
      → anti-periodicity of state vectors and of the sequences U_n, V_n
      → quadratic character-sum cancellation when χ_p(-1) = -1.

Relation to the manuscript
--------------------------
- This pipeline strengthens the computational companion for Mechanism 1
  (half-period translation / matrix involution) in the important family
  Q ≡ -1 (mod p), which includes the Fibonacci and Pell sequences.
- The general half-period criterion of the manuscript (Proposition on the
  half-period criterion) does not require Q ≡ -1; the present code
  deliberately specializes in order to obtain a fully constructive
  verification path that begins from the norm-fibre identity.
- Mechanism 2 of the manuscript (rank-block scalar propagation /
  geometric character factorization) is not treated here; it is covered
  by the diagnostic examples verifier.

Outputs
-------
    results/theorem-pipeline-verification.csv
    results/theorem-pipeline-verification.json

Dependencies: Python standard library only.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ============================================================================
# Configuration
# ============================================================================

VERIFY_CHARACTER_SUMS = True
EXPORT_JSON = True
SCAN_BOUND = 200
VERBOSE = True

PROOF_MAP = {
    "Step1": "Inertness of discriminant over F_p",
    "Step2": "Irreducible quadratic and explicit construction of F_{p²}",
    "Step3": "Norm identity N(λ)=Q and derived norm-fibre specialization",
    "Step4": "Unique involution in the cyclic subgroup ⟨λ⟩",
    "Step5": "Transfer to the companion matrix A",
    "Step6": "Anti-periodicity on state vectors and sequence projections",
    "Step7": "Quadratic character-sum cancellation",
}


# ============================================================================
# Basic arithmetic
# ============================================================================

def is_odd_prime(n: int) -> bool:
    if n <= 2 or n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def primes_between(start: int, stop_exclusive: int):
    for n in range(max(2, start), stop_exclusive):
        if is_prime(n):
            yield n


def quadratic_character_mod_p(a: int, p: int) -> int:
    """Extended Legendre symbol: χ(0) = 0."""
    a_mod = a % p
    if a_mod == 0:
        return 0
    value = pow(a_mod, (p - 1) // 2, p)
    if value == 1:
        return 1
    if value == p - 1:
        return -1
    raise AssertionError(
        f"Euler criterion produced unexpected value {value} for a={a}, p={p}."
    )


# ============================================================================
# Lucas sequences
# ============================================================================

def lucas_sequences_mod_p(
    P: int, Q: int, p: int, N: int
) -> tuple[list[int], list[int]]:
    if N < 1:
        raise ValueError("N must be at least 1.")
    Pp = P % p
    Qp = Q % p
    U = [0, 1]
    V = [2 % p, Pp]
    for n in range(2, N + 1):
        U.append((Pp * U[n - 1] - Qp * U[n - 2]) % p)
        V.append((Pp * V[n - 1] - Qp * V[n - 2]) % p)
    return U, V


def state_vectors_from_sequences(
    U: list[int], V: list[int]
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """
    State vectors associated with the companion-matrix action:

        X_n = (U_{n+1}, U_n),
        Y_n = (V_{n+1}, V_n).
    """
    X = [(U[n + 1], U[n]) for n in range(len(U) - 1)]
    Y = [(V[n + 1], V[n]) for n in range(len(V) - 1)]
    return X, Y


# ============================================================================
# 2×2 matrices over F_p
# ============================================================================

Matrix2 = tuple[tuple[int, int], tuple[int, int]]


def mat_identity() -> Matrix2:
    return ((1, 0), (0, 1))


def mat_mul(a: Matrix2, b: Matrix2, p: int) -> Matrix2:
    return (
        (
            (a[0][0] * b[0][0] + a[0][1] * b[1][0]) % p,
            (a[0][0] * b[0][1] + a[0][1] * b[1][1]) % p,
        ),
        (
            (a[1][0] * b[0][0] + a[1][1] * b[1][0]) % p,
            (a[1][0] * b[0][1] + a[1][1] * b[1][1]) % p,
        ),
    )


def mat_pow(a: Matrix2, exponent: int, p: int) -> Matrix2:
    result = mat_identity()
    base = a
    n = exponent
    while n > 0:
        if n & 1:
            result = mat_mul(result, base, p)
        base = mat_mul(base, base, p)
        n >>= 1
    return result


# ============================================================================
# F_{p²} = F_p[x] / (x² - P x + Q)
# ============================================================================

@dataclass(frozen=True)
class Fp2:
    a: int
    b: int
    p: int
    P: int
    Q: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "a", self.a % self.p)
        object.__setattr__(self, "b", self.b % self.p)
        object.__setattr__(self, "P", self.P % self.p)
        object.__setattr__(self, "Q", self.Q % self.p)

    def __add__(self, other: "Fp2") -> "Fp2":
        self._check(other)
        return Fp2(self.a + other.a, self.b + other.b, self.p, self.P, self.Q)

    def __sub__(self, other: "Fp2") -> "Fp2":
        self._check(other)
        return Fp2(self.a - other.a, self.b - other.b, self.p, self.P, self.Q)

    def __neg__(self) -> "Fp2":
        return Fp2(-self.a, -self.b, self.p, self.P, self.Q)

    def __mul__(self, other: "Fp2") -> "Fp2":
        self._check(other)
        a, b = self.a, self.b
        c, d = other.a, other.b
        # (a + b λ)(c + d λ) with λ² = P λ - Q
        constant = a * c - b * d * self.Q
        linear = a * d + b * c + b * d * self.P
        return Fp2(constant, linear, self.p, self.P, self.Q)

    def __pow__(self, exponent: int) -> "Fp2":
        if exponent < 0:
            return self.inverse() ** (-exponent)
        result = Fp2.one(self.p, self.P, self.Q)
        base = self
        n = exponent
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n >>= 1
        return result

    def inverse(self) -> "Fp2":
        nrm = self.norm()
        if nrm == 0:
            raise ZeroDivisionError("Non-invertible element of Fp2.")
        norm_inv = pow(nrm, -1, self.p)
        conjugate = self.conjugate()
        return Fp2(
            conjugate.a * norm_inv,
            conjugate.b * norm_inv,
            self.p,
            self.P,
            self.Q,
        )

    def norm(self) -> int:
        return (
            self.a * self.a
            + self.a * self.b * self.P
            + self.b * self.b * self.Q
        ) % self.p

    def conjugate(self) -> "Fp2":
        # Frobenius: a + b λ  ↦  a + b λ^p = a + b (P - λ) = (a + b P) - b λ
        return Fp2(self.a + self.b * self.P, -self.b, self.p, self.P, self.Q)

    def _check(self, other: "Fp2") -> None:
        if not isinstance(other, Fp2):
            raise TypeError("Fp2 arithmetic requires another Fp2 element.")
        if self.p != other.p or self.P != other.P or self.Q != other.Q:
            raise ValueError("Fp2 elements belong to different fields.")

    @classmethod
    def zero(cls, p: int, P: int, Q: int) -> "Fp2":
        return cls(0, 0, p, P, Q)

    @classmethod
    def one(cls, p: int, P: int, Q: int) -> "Fp2":
        return cls(1, 0, p, P, Q)

    @classmethod
    def lam(cls, p: int, P: int, Q: int) -> "Fp2":
        """The generator λ satisfying λ² = P λ - Q."""
        return cls(0, 1, p, P, Q)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fp2):
            return NotImplemented
        return (
            self.a == other.a
            and self.b == other.b
            and self.p == other.p
            and self.P == other.P
            and self.Q == other.Q
        )

    def __str__(self) -> str:
        return f"({self.a} + {self.b}*λ mod {self.p})"


# ============================================================================
# Polynomial irreducibility
# ============================================================================

def quadratic_is_irreducible(P: int, Q: int, p: int) -> bool:
    D = (P * P - 4 * Q) % p
    if D == 0:
        return False
    return quadratic_character_mod_p(D, p) == -1


# ============================================================================
# Stringification
# ============================================================================

def stringify_value(value: Any) -> Any:
    if isinstance(value, (int, str, bool)) or value is None:
        return value
    return str(value)


# ============================================================================
# Core verification (layered pipeline)
# ============================================================================

def verify_case(
    name: str,
    P: int,
    Q: int,
    p: int,
    verify_character_sums: bool = True,
) -> dict[str, Any]:
    if not is_odd_prime(p):
        raise ValueError(f"p must be an odd prime, got p={p}")

    D = (P * P - 4 * Q) % p
    chi_D = quadratic_character_mod_p(D, p)

    result: dict[str, Any] = {
        "Sequence": name,
        "P": P,
        "Q": Q,
        "p": p,
        # Hypothesis layer
        "D_mod_p": D,
        "chi_D": chi_D,
        "Inert": False,
        "Q_eq_minus1_mod_p": False,
        # Algebraic layer
        "PolyIrreducible": False,
        "NormByConjugation": "",
        "NormByFieldMap": "",
        "NormEqualsQ": False,
        "NormEqualsMinusOne": False,
        "NormFibre_DirectValidation": False,
        # Structural layer
        "T": "",
        "T_even": False,
        "T_divides_2(p+1)": False,
        "T_not_divides_(p+1)": False,
        "UniqueOrder2ElementIn<lambda>": False,
        "HalfInvolution_StructuralDerivation": False,
        "HalfInvolution_DirectCheck": False,
        # Matrix layer
        "det(A)=Q": False,
        "trace(A)=P": False,
        "Eigen_to_Matrix_Bridge": False,
        "A^(T/2)=-I": False,
        "A^T=I": False,
        # Dynamical layer
        "U_AntiPeriodic_State": False,
        "V_AntiPeriodic_State": False,
        "U_AntiPeriodic_Sequence": False,
        "V_AntiPeriodic_Sequence": False,
        # Character sums
        "CharSum_U": "",
        "CharSum_V": "",
        "CharSumsVanish": "N/A",
        # Layer summaries
        "algebraic_success": False,
        "structural_success": False,
        "matrix_success": False,
        "dynamical_success": False,
        "pipeline_success": False,
        "Status": "Initialized",
    }

    # ------------------------------------------------------------------
    # Step 1 – Inertness
    # ------------------------------------------------------------------
    result["Q_eq_minus1_mod_p"] = ((Q - (-1)) % p == 0)

    if chi_D != -1:
        result["Status"] = "Failed: discriminant not inert"
        return result
    result["Inert"] = True

    # ------------------------------------------------------------------
    # Step 2 – Irreducibility and field construction
    # ------------------------------------------------------------------
    if not quadratic_is_irreducible(P, Q, p):
        result["Status"] = "Failed: polynomial reducible"
        return result
    result["PolyIrreducible"] = True

    lambda_element = Fp2.lam(p, P, Q)
    lambda_bar = lambda_element.conjugate()
    norm_conj = lambda_element * lambda_bar
    norm_map = lambda_element.norm()

    result["NormByConjugation"] = str(norm_conj)
    result["NormByFieldMap"] = str(norm_map)

    norm_equals_q = (
        norm_conj.a == (Q % p)
        and norm_conj.b == 0
        and norm_map == (Q % p)
    )
    result["NormEqualsQ"] = norm_equals_q

    if not norm_equals_q:
        result["Status"] = "Failed: norm identity"
        return result

    # The constructive half-involution path that follows requires the
    # specialization Q ≡ -1 (mod p).  Outside this branch the algebraic
    # layer is recorded as successful and the remaining steps are skipped.
    if not result["Q_eq_minus1_mod_p"]:
        result["algebraic_success"] = True
        result["Status"] = "Skipped: outside Q ≡ -1 (mod p) branch"
        return result

    # ------------------------------------------------------------------
    # Step 3 – Norm-fibre identity (available only when Q ≡ -1)
    # ------------------------------------------------------------------
    # N(λ) = Q ≡ -1  ⇒  λ · λ^p = -1  ⇒  λ^{p+1} = -1.
    result["NormEqualsMinusOne"] = (norm_map == ((-1) % p))
    norm_fibre = lambda_element ** (p + 1)
    result["NormFibre_DirectValidation"] = (
        norm_fibre == Fp2(-1, 0, p, P, Q)
    )

    result["algebraic_success"] = all([
        result["Inert"],
        result["PolyIrreducible"],
        result["NormEqualsQ"],
        result["NormEqualsMinusOne"],
        result["NormFibre_DirectValidation"],
    ])
    if not result["algebraic_success"]:
        result["Status"] = "Failed: algebraic layer"
        return result

    # ------------------------------------------------------------------
    # Step 4 – Unique involution in ⟨λ⟩
    # ------------------------------------------------------------------
    # λ^{p+1} = -1 shows that -1 lies in the cyclic group ⟨λ⟩.
    # The unique element of order 2 in a cyclic group of even order T is
    # λ^{T/2}.  The divisibility conditions
    #     T | 2(p+1)   and   T ∤ (p+1)
    # guarantee that the order of λ^{p+1} is exactly 2, so the involution
    # is realized precisely at the half-period.
    T = 1
    power = lambda_element
    one = Fp2.one(p, P, Q)
    while power != one:
        power = power * lambda_element
        T += 1
        if T > (p * p - 1):
            result["Status"] = "Failed: multiplicative order search"
            return result

    result["T"] = T
    result["T_even"] = (T % 2 == 0)
    result["T_divides_2(p+1)"] = ((2 * (p + 1)) % T == 0)
    result["T_not_divides_(p+1)"] = (((p + 1) % T) != 0)
    result["UniqueOrder2ElementIn<lambda>"] = result["T_even"]

    result["HalfInvolution_StructuralDerivation"] = all([
        result["T_even"],
        result["T_divides_2(p+1)"],
        result["T_not_divides_(p+1)"],
        result["UniqueOrder2ElementIn<lambda>"],
    ])

    if result["T_even"]:
        half_power = lambda_element ** (T // 2)
        result["HalfInvolution_DirectCheck"] = (
            half_power == Fp2(-1, 0, p, P, Q)
        )
    else:
        result["HalfInvolution_DirectCheck"] = False

    result["structural_success"] = all([
        result["HalfInvolution_StructuralDerivation"],
        result["HalfInvolution_DirectCheck"],
    ])
    if not result["structural_success"]:
        result["Status"] = "Failed: structural layer"
        return result

    # ------------------------------------------------------------------
    # Step 5 – Transfer to the companion matrix
    # ------------------------------------------------------------------
    A: Matrix2 = ((P % p, (-Q) % p), (1, 0))
    neg_I: Matrix2 = (((-1) % p, 0), (0, (-1) % p))
    A_half = mat_pow(A, T // 2, p)
    A_T = mat_pow(A, T, p)

    determinant = (A[0][0] * A[1][1] - A[0][1] * A[1][0]) % p
    trace = (A[0][0] + A[1][1]) % p

    result["det(A)=Q"] = determinant == (Q % p)
    result["trace(A)=P"] = trace == (P % p)
    result["Eigen_to_Matrix_Bridge"] = (
        lambda_element ** (T // 2) == Fp2(-1, 0, p, P, Q)
        and lambda_bar ** (T // 2) == Fp2(-1, 0, p, P, Q)
    )
    result["A^(T/2)=-I"] = (A_half == neg_I)
    result["A^T=I"] = (A_T == mat_identity())

    result["matrix_success"] = all([
        result["det(A)=Q"],
        result["trace(A)=P"],
        result["Eigen_to_Matrix_Bridge"],
        result["A^(T/2)=-I"],
        result["A^T=I"],
    ])
    if not result["matrix_success"]:
        result["Status"] = "Failed: matrix layer"
        return result

    # ------------------------------------------------------------------
    # Step 6 – Dynamical layer (state vectors + sequences)
    # ------------------------------------------------------------------
    U, V = lucas_sequences_mod_p(P, Q, p, T + 1)
    X, Y = state_vectors_from_sequences(U, V)
    half_T = T // 2

    # Anti-periodicity of state vectors:
    #   X_{n + T/2} = - X_n ,   Y_{n + T/2} = - Y_n
    # (this is the direct matrix action of A^{T/2} = -I).
    result["U_AntiPeriodic_State"] = all(
        (X[n + half_T][0] == (-X[n][0]) % p
         and X[n + half_T][1] == (-X[n][1]) % p)
        for n in range(0, len(X) - half_T)
    )
    result["V_AntiPeriodic_State"] = all(
        (Y[n + half_T][0] == (-Y[n][0]) % p
         and Y[n + half_T][1] == (-Y[n][1]) % p)
        for n in range(0, len(Y) - half_T)
    )

    # Anti-periodicity of the sequences themselves
    result["U_AntiPeriodic_Sequence"] = all(
        U[n + half_T] == (-U[n]) % p
        for n in range(1, T - half_T + 1)
    )
    result["V_AntiPeriodic_Sequence"] = all(
        V[n + half_T] == (-V[n]) % p
        for n in range(1, T - half_T + 1)
    )

    result["dynamical_success"] = all([
        result["U_AntiPeriodic_State"],
        result["V_AntiPeriodic_State"],
        result["U_AntiPeriodic_Sequence"],
        result["V_AntiPeriodic_Sequence"],
    ])
    if not result["dynamical_success"]:
        result["Status"] = "Failed: dynamical layer"
        return result

    # ------------------------------------------------------------------
    # Step 7 – Quadratic character sums
    # ------------------------------------------------------------------
    if verify_character_sums:
        if quadratic_character_mod_p(-1, p) == -1:
            S_U = sum(
                quadratic_character_mod_p(U[n], p) for n in range(1, T + 1)
            )
            S_V = sum(
                quadratic_character_mod_p(V[n], p) for n in range(1, T + 1)
            )
            result["CharSum_U"] = S_U
            result["CharSum_V"] = S_V
            result["CharSumsVanish"] = (S_U == 0 and S_V == 0)
        else:
            result["CharSum_U"] = "N/A"
            result["CharSum_V"] = "N/A"
            result["CharSumsVanish"] = "N/A"

    # ------------------------------------------------------------------
    # Closure
    # ------------------------------------------------------------------
    result["pipeline_success"] = all([
        result["algebraic_success"],
        result["structural_success"],
        result["matrix_success"],
        result["dynamical_success"],
    ])
    if verify_character_sums and result["CharSumsVanish"] is False:
        result["pipeline_success"] = False

    result["Status"] = (
        "Success" if result["pipeline_success"] else "Failed: closure"
    )
    return result


# ============================================================================
# Printing
# ============================================================================

def print_detailed_case(res: dict[str, Any]) -> None:
    print("\n" + "─" * 90)
    print(f"CASE: {res['Sequence']}   |   P={res['P']}, Q={res['Q']}, p={res['p']}")
    print("─" * 90)

    print(f"[Step1] {PROOF_MAP['Step1']}")
    print(f"        D ≡ {res['D_mod_p']} (mod p)")
    print(f"        χ(D) = {res['chi_D']}")
    print(f"        Inert (χ(D) = -1) ........... {res['Inert']}")
    print(f"        Q ≡ -1 (mod p) .............. {res['Q_eq_minus1_mod_p']}")

    print(f"\n[Step2] {PROOF_MAP['Step2']}")
    print(f"        Polynomial irreducible ...... {res['PolyIrreducible']}")
    print(f"        Norm by conjugation ......... {res['NormByConjugation']}")
    print(f"        Norm by field map ........... {res['NormByFieldMap']}")
    print(f"        NormEqualsQ ................. {res['NormEqualsQ']}")

    print(f"\n[Step3] {PROOF_MAP['Step3']}")
    print(f"        N(λ) ≡ -1 (mod p) ........... {res['NormEqualsMinusOne']}")
    print(f"        λ^{{p+1}} = -1 (direct) ....... {res['NormFibre_DirectValidation']}")
    print(f"        algebraic_success ........... {res['algebraic_success']}")

    print(f"\n[Step4] {PROOF_MAP['Step4']}")
    print(f"        Multiplicative order T ...... {res['T']}")
    print(f"        T even ...................... {res['T_even']}")
    print(f"        T | 2(p+1) .................. {res['T_divides_2(p+1)']}")
    print(f"        T does not divide (p+1) ..... {res['T_not_divides_(p+1)']}")
    print(f"        Unique order-2 element ...... {res['UniqueOrder2ElementIn<lambda>']}")
    print(f"        HalfInvolution (structural) . {res['HalfInvolution_StructuralDerivation']}")
    print(f"        HalfInvolution (direct) ..... {res['HalfInvolution_DirectCheck']}")
    print(f"        structural_success .......... {res['structural_success']}")

    print(f"\n[Step5] {PROOF_MAP['Step5']}")
    print(f"        det(A) = Q .................. {res['det(A)=Q']}")
    print(f"        trace(A) = P ................ {res['trace(A)=P']}")
    print(f"        Eigen → Matrix bridge ....... {res['Eigen_to_Matrix_Bridge']}")
    print(f"        A^(T/2) = -I ................ {res['A^(T/2)=-I']}")
    print(f"        A^T = I ..................... {res['A^T=I']}")
    print(f"        matrix_success .............. {res['matrix_success']}")

    print(f"\n[Step6] {PROOF_MAP['Step6']}")
    print(f"        U anti-periodic (state) ..... {res['U_AntiPeriodic_State']}")
    print(f"        V anti-periodic (state) ..... {res['V_AntiPeriodic_State']}")
    print(f"        U anti-periodic (sequence) .. {res['U_AntiPeriodic_Sequence']}")
    print(f"        V anti-periodic (sequence) .. {res['V_AntiPeriodic_Sequence']}")
    print(f"        dynamical_success ........... {res['dynamical_success']}")

    print(f"\n[Step7] {PROOF_MAP['Step7']}")
    print(f"        CharSum_U ................... {res['CharSum_U']}")
    print(f"        CharSum_V ................... {res['CharSum_V']}")
    print(f"        CharSumsVanish .............. {res['CharSumsVanish']}")

    print(f"\n>>> PIPELINE SUCCESS: {res['pipeline_success']}   |   Status: {res['Status']}")
    print("─" * 90)


def print_case_summary(res: dict[str, Any]) -> None:
    status = "PASS" if res["pipeline_success"] else "FAIL"
    T_str = str(res["T"]) if res["T"] != "" else "NA"
    print(
        f"{status:4} | "
        f"{res['Sequence']:22} | "
        f"p={res['p']:>3} | "
        f"T={T_str:>3} | "
        f"alg={str(res['algebraic_success']):5} | "
        f"struct={str(res['structural_success']):5} | "
        f"mat={str(res['matrix_success']):5} | "
        f"dyn={str(res['dynamical_success']):5} | "
        f"{res['Status']}"
    )


# ============================================================================
# Export
# ============================================================================

def export_csv(rows: list[dict], filename: str) -> None:
    if not rows:
        return
    flat_rows = [
        {key: stringify_value(value) for key, value in row.items()}
        for row in rows
    ]
    headers = list(flat_rows[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flat_rows)


def export_json(rows: list[dict], filename: str) -> None:
    payload = {
        "metadata": {
            "artifact": "Theorem pipeline verification",
            "implementation": "pure Python",
            "paper_title": (
                "Half-Period Involutions and Exact Cancellation "
                "in Inert Lucas Sequences"
            ),
            "scope": "Specialized constructive pipeline for the branch Q ≡ -1 (mod p)",
            "proof_map": PROOF_MAP,
            "verify_character_sums": VERIFY_CHARACTER_SUMS,
            "scan_bound": SCAN_BOUND,
        },
        "results": [
            {key: stringify_value(value) for key, value in row.items()}
            for row in rows
        ],
    }
    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_filename = results_dir / "theorem-pipeline-verification.csv"
    json_filename = results_dir / "theorem-pipeline-verification.json"

    # Hard fail-fast: refuse to overwrite existing evidence
    for filename in (csv_filename, json_filename):
        if Path(filename).exists():
            raise FileExistsError(
                f"Refusing to overwrite existing evidence file: {filename}"
            )

    rows: list[dict] = []

    print("=" * 100)
    print("THEOREM PIPELINE VERIFICATION")
    print("Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences")
    print("Pure Python / standard library only")
    print("Scope: specialized constructive path for the branch Q ≡ -1 (mod p)")
    print("=" * 100)

    print("\nProof map:")
    for key, value in PROOF_MAP.items():
        print(f"  {key}: {value}")

    print("\n--- Representative inert cases with Q ≡ -1 (mod p) ---")
    representative_cases = [
        ("Fibonacci", 1, -1, 3),
        ("Fibonacci", 1, -1, 7),
        ("Pell", 2, -1, 3),
        ("Pell", 2, -1, 5),
        ("U(3,-1)", 3, -1, 5),
    ]

    for case in representative_cases:
        result = verify_case(*case, verify_character_sums=VERIFY_CHARACTER_SUMS)
        rows.append(result)
        if VERBOSE:
            print_detailed_case(result)
        else:
            print_case_summary(result)

    print(f"\n--- Doubly inert Fibonacci scan for primes p ≤ {SCAN_BOUND} ---")
    success_count = 0
    total_count = 0

    for p in primes_between(7, SCAN_BOUND + 1):
        if (
            quadratic_character_mod_p(5, p) == -1
            and quadratic_character_mod_p(-1, p) == -1
        ):
            total_count += 1
            result = verify_case(
                "Fibonacci_Scan", 1, -1, p,
                verify_character_sums=VERIFY_CHARACTER_SUMS,
            )
            rows.append(result)
            if result["pipeline_success"]:
                success_count += 1
            print_case_summary(result)

    print(f"\nSuccessful cases in scan: {success_count}/{total_count}")

    export_csv(rows, csv_filename)
    if EXPORT_JSON:
        export_json(rows, json_filename)

    print("\n" + "=" * 100)
    print(f"CSV exported to : {csv_filename}")
    if EXPORT_JSON:
        print(f"JSON exported to: {json_filename}")
    print("=" * 100)


if __name__ == "__main__":
    main()
