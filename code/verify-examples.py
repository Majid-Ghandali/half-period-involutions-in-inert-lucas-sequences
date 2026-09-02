# verify-examples.py
"""
Exact-arithmetic verification of the two diagnostic examples appearing in:

    Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences
    Majid Ghandali, 2026

This script verifies, statement by statement, the two examples given in
Section "Examples" of the manuscript. It uses only the Python standard
library and exact modular arithmetic.

Output
------
results/example-verification.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================================
# Arithmetic helpers
# ============================================================================

def is_odd_prime(p: int) -> bool:
    if p <= 2 or p % 2 == 0:
        return False
    d = 3
    while d * d <= p:
        if p % d == 0:
            return False
        d += 2
    return True


def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    val = pow(a, (p - 1) // 2, p)
    if val == 1:
        return 1
    if val == p - 1:
        return -1
    raise AssertionError(f"Unexpected Euler criterion value {val}")


def chi(a: int, p: int) -> int:
    return legendre(a, p)


# ============================================================================
# Matrix arithmetic over F_p
# ============================================================================

Matrix = tuple[tuple[int, int], tuple[int, int]]


def mat_mul(A: Matrix, B: Matrix, p: int) -> Matrix:
    return (
        (
            (A[0][0]*B[0][0] + A[0][1]*B[1][0]) % p,
            (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % p,
        ),
        (
            (A[1][0]*B[0][0] + A[1][1]*B[1][0]) % p,
            (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % p,
        ),
    )


def mat_pow(A: Matrix, exp: int, p: int) -> Matrix:
    result: Matrix = ((1, 0), (0, 1))
    base = A
    while exp:
        if exp & 1:
            result = mat_mul(result, base, p)
        base = mat_mul(base, base, p)
        exp >>= 1
    return result


def matrix_order(A: Matrix, p: int) -> int:
    I: Matrix = ((1, 0), (0, 1))
    cur = I
    bound = (p*p - 1) * (p*p - p)
    for n in range(1, bound + 1):
        cur = mat_mul(cur, A, p)
        if cur == I:
            return n
    raise AssertionError("Order not found")


# ============================================================================
# Lucas sequences
# ============================================================================

def lucas(P: int, Q: int, p: int, N: int) -> tuple[list[int], list[int]]:
    U = [0, 1]
    V = [2 % p, P % p]
    for _ in range(2, N + 1):
        U.append((P * U[-1] - Q * U[-2]) % p)
        V.append((P * V[-1] - Q * V[-2]) % p)
    return U, V


# ============================================================================
# Example 1 – Fibonacci modulo 7
# ============================================================================

def verify_fibonacci_mod_7() -> dict[str, Any]:
    P, Q, p = 1, -1, 7
    if not is_odd_prime(p):
        raise ValueError(f"p must be an odd prime, got {p}")

    D = (P*P - 4*Q) % p
    A: Matrix = ((1, 1), (1, 0))

    U, V = lucas(P, Q, p, 16)
    T = matrix_order(A, p)
    half = T // 2

    assert D == 5
    assert chi(D, p) == -1
    assert T == 16
    assert mat_pow(A, half, p) == ((p - 1, 0), (0, p - 1))
    assert mat_pow(A, T, p) == ((1, 0), (0, 1))
    assert all(
        U[n + half] == (-U[n]) % p
        for n in range(0, half + 1)
    )
    assert all(
        V[n + half] == (-V[n]) % p
        for n in range(0, half + 1)
    )
    assert chi(-1, p) == -1

    S_U = sum(chi(U[n], p) for n in range(1, T + 1))
    S_V = sum(chi(V[n], p) for n in range(1, T + 1))
    assert S_U == 0 and S_V == 0

    return {
        "name": "Fibonacci sequence modulo 7",
        "label": "ex:fibonacci-7",
        "parameters": {"P": P, "Q": Q, "p": p, "D": D},
        "matrix_A": A,
        "T": T,
        "half_period": half,
        "A8_equals_minus_I": True,
        "A16_equals_I": True,
        "U_anti_periodicity": True,
        "V_anti_periodicity": True,
        "chi_minus_1": chi(-1, p),
        "character_sum_U": S_U,
        "character_sum_V": S_V,
        "status": "PASS",
    }


# ============================================================================
# Example 2 – Inert scalar cancellation
# ============================================================================

def verify_inert_scalar_mod_5() -> dict[str, Any]:
    P, Q, p = 1, 2, 5
    if not is_odd_prime(p):
        raise ValueError(f"p must be an odd prime, got {p}")

    D = (P*P - 4*Q) % p
    A: Matrix = ((P % p, (-Q) % p), (1, 0))

    U, V = lucas(P, Q, p, 24)

    paper_U = [0, 1, 1, 4, 2, 4, 0, 2]
    assert U[:8] == paper_U

    alpha = 6
    Lambda = U[alpha + 1]
    assert Lambda == 2

    omega = 1
    pow_L = Lambda
    while pow_L != 1:
        pow_L = (pow_L * Lambda) % p
        omega += 1
    assert omega == 4

    T_from_formula = alpha * omega
    assert T_from_formula == 24

    matrix_T = matrix_order(A, p)
    assert matrix_T == T_from_formula

    assert chi(Lambda, p) == -1
    assert chi(-1, p) == 1
    assert mat_pow(A, alpha, p) == ((Lambda, 0), (0, Lambda))

    for k in range(4):
        factor = pow(Lambda, k, p)
        for j in range(1, alpha + 1):
            assert U[k*alpha + j] == (factor * U[j]) % p
            assert V[k*alpha + j] == (factor * V[j]) % p

    sum_block0 = sum(chi(U[j], p) for j in range(1, 7))
    sum_block1 = sum(chi(U[6 + j], p) for j in range(1, 7))
    assert sum_block0 == 3
    assert sum_block1 == -3

    full_sum_U = sum(chi(U[n], p) for n in range(1, T_from_formula + 1))
    full_sum_V = sum(chi(V[n], p) for n in range(1, T_from_formula + 1))
    assert full_sum_U == 0
    assert full_sum_V == 0

    return {
        "name": "Inert scalar cancellation",
        "label": "ex:scalar-cancellation",
        "parameters": {"P": P, "Q": Q, "p": p, "D": D},
        "initial_U": U[:8],
        "alpha": alpha,
        "Lambda": Lambda,
        "omega": omega,
        "T_from_formula": T_from_formula,
        "matrix_order": matrix_T,
        "matrix_order_equals_T": True,
        "chi_Lambda": chi(Lambda, p),
        "chi_minus_1": chi(-1, p),
        "A_alpha_equals_Lambda_I": True,
        "rank_block_propagation": True,
        "block0_character_sum": sum_block0,
        "block1_character_sum": sum_block1,
        "full_character_sum_U": full_sum_U,
        "full_character_sum_V": full_sum_V,
        "full_character_sums_vanish": True,
        "status": "PASS",
    }


# ============================================================================


# ============================================================================
# Remark ? Even period alone is not enough  (P,Q,p)=(1,1,5)
# ============================================================================

def verify_even_period_not_enough_mod_5() -> dict[str, Any]:
    """Remark 6.3: T even and A^{T/2}=-I do not force quadratic cancellation."""
    P, Q, p = 1, 1, 5
    if not is_odd_prime(p):
        raise ValueError(f"p must be an odd prime, got {p}")

    D = (P * P - 4 * Q) % p
    A: Matrix = ((P % p, (-Q) % p), (1, 0))

    U, V = lucas(P, Q, p, 12)

    assert D == 2
    assert chi(D, p) == -1

    alpha = next(n for n in range(1, len(U)) if U[n] == 0)
    assert alpha == 3
    Lambda = U[alpha + 1]
    assert Lambda == (p - 1) % p

    omega = 1
    pow_L = Lambda
    while pow_L != 1:
        pow_L = (pow_L * Lambda) % p
        omega += 1
        if omega > p:
            raise RuntimeError("order computation failed")
    assert omega == 2

    T = alpha * omega
    assert T == 6
    assert matrix_order(A, p) == T

    half = T // 2
    assert mat_pow(A, half, p) == ((p - 1, 0), (0, p - 1))
    assert mat_pow(A, T, p) == ((1, 0), (0, 1))

    assert chi(-1, p) == 1
    assert chi(Lambda, p) == 1

    S_U = sum(chi(U[n], p) for n in range(1, T + 1))
    assert S_U == 4

    return {
        "name": "Even period alone is not enough",
        "label": "rem:even-period-not-enough",
        "parameters": {"P": P, "Q": Q, "p": p, "D": D},
        "alpha": alpha,
        "Lambda": Lambda,
        "omega": omega,
        "T": T,
        "A_half_equals_minus_I": True,
        "chi_minus_1": chi(-1, p),
        "chi_Lambda": chi(Lambda, p),
        "both_criteria_inactive": True,
        "character_sum_U": S_U,
        "character_sum_does_not_vanish": True,
        "status": "PASS",
    }

# Pretty-printing
# ============================================================================

def print_example(ex: dict[str, Any]) -> None:
    print("\n" + "═"*78)
    print(f"EXAMPLE: {ex['name']}  ({ex['label']})")
    print("═"*78)

    if ex["label"] == "ex:fibonacci-7":
        print(f"(P,Q,p) = ({ex['parameters']['P']}, {ex['parameters']['Q']}, {ex['parameters']['p']})")
        print(f"D = {ex['parameters']['D']}  (nonsquare mod 7)  →  X²−X−1 irreducible over F_7")
        print()
        print("Companion matrix:")
        print("    A = [[1, 1],")
        print("         [1, 0]]")
        print()
        print("Direct exponentiation:")
        print("    A^8  = −I")
        print("    A^16 =  I")
        print(f"    ⇒  T = {ex['T']}")
        print()
        print("Anti-periodicity:")
        print("    U_{n+8} ≡ −U_n  (mod 7)")
        print("    V_{n+8} ≡ −V_n  (mod 7)")
        print()
        print(f"χ_7(−1) = {ex['chi_minus_1']}")
        print("⇒  quadratic-character values cancel under the half-period translation")
        print(f"    Σ χ(U_n) = {ex['character_sum_U']},   Σ χ(V_n) = {ex['character_sum_V']}")

    elif ex["label"] == "ex:scalar-cancellation":
        print(f"(P,Q,p) = ({ex['parameters']['P']}, {ex['parameters']['Q']}, {ex['parameters']['p']})")
        print(f"D ≡ {ex['parameters']['D']} (mod 5)  (nonsquare)  →  X²−X+2 irreducible over F_5")
        print()
        print("Initial segment of U (as given in the paper):")
        print(f"    {ex['initial_U']}")
        print()
        print(f"Rank α = {ex['alpha']},   Λ = U_{{α+1}} = {ex['Lambda']}")
        print(f"χ_5(Λ) = {ex['chi_Lambda']},   ord(Λ) = {ex['omega']}")
        print(f"T from formula (α·ω) = {ex['T_from_formula']}")
        print(f"Direct matrix order   = {ex['matrix_order']}   → matches T")
        print(f"χ_5(−1) = {ex['chi_minus_1']}   ← cancellation is NOT produced by half-period negation")
        print()
        print("Scalar propagation:")
        print("    U_{6k+j} ≡ 2^k U_j,   V_{6k+j} ≡ 2^k V_j  (mod 5)")
        print()
        print("Character sums on the first two rank blocks:")
        print(f"    Σ_{{j=1..6}} χ(U_j)     = {ex['block0_character_sum']}")
        print(f"    Σ_{{j=1..6}} χ(U_{{6+j}}) = {ex['block1_character_sum']}")
        print("    sum of the two blocks = 0")
        print()
        print("Full-period character sums (n = 1 … T):")
        print(f"    Σ χ(U_n) = {ex['full_character_sum_U']}")
        print(f"    Σ χ(V_n) = {ex['full_character_sum_V']}")
        print("⇒  scalar character filtering, not a negation pairing")


    elif ex["label"] == "rem:even-period-not-enough":
        print(f"(P,Q,p) = ({ex['parameters']['P']}, {ex['parameters']['Q']}, {ex['parameters']['p']})")
        print(f"D = {ex['parameters']['D']} (mod 5)")
        print(f"alpha={ex['alpha']}, Lambda={ex['Lambda']}, omega={ex['omega']}, T={ex['T']}")
        print(f"chi(-1)={ex['chi_minus_1']}, chi(Lambda)={ex['chi_Lambda']}")
        print(f"sum chi(U)={ex['character_sum_U']} != 0")
    print()
    print(f">>> STATUS: {ex['status']}")
    print("═"*78)


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "example-verification.json"

    # Hard fail-fast: refuse to overwrite existing evidence
    if output_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing evidence file: {output_path}"
        )

    print("="*78)
    print("VERIFICATION OF THE TWO EXAMPLES FROM THE MANUSCRIPT")
    print("Half-Period Involutions and Exact Cancellation in Inert Lucas Sequences")
    print("="*78)

    examples = [
        verify_fibonacci_mod_7(),
        verify_inert_scalar_mod_5(),
        verify_even_period_not_enough_mod_5(),
    ]

    for ex in examples:
        print_example(ex)

    report = {
        "artifact": "verify-examples.py",
        "purpose": "Statement-by-statement verification of the two examples in Section Examples",
        "examples": examples,
        "overall_status": "PASS",
    }

    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("\n" + "="*78)
    print("SUMMARY")
    for ex in examples:
        print(f"  PASS  –  {ex['name']}")
    print(f"\nJSON written to: {output_path}")
    print("="*78)


if __name__ == "__main__":
    main()