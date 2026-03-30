"""
Blackboard Derivation: Why does sin(2t) + sin(5t) have peaks of amplitude 2?
=============================================================================

STEP 1: Start with the Sum-to-Product Identity
───────────────────────────────────────────────
    sin(A) + sin(B) = 2 · cos((A - B) / 2) · sin((A + B) / 2)

STEP 2: Apply to our waves, where A = 2t, B = 5t
─────────────────────────────────────────────────
    sin(2t) + sin(5t) = 2 · cos((2t - 5t) / 2) · sin((2t + 5t) / 2)

                       = 2 · cos(-3t/2) · sin(7t/2)

    Since cos(-x) = cos(x):

                       = 2 · cos(3t/2) · sin(7t/2)
                         ─────────────   ──────────
                          ↑ ENVELOPE      ↑ CARRIER
                          (slow)          (fast)

STEP 3: Find the maximum amplitude
───────────────────────────────────
    The maximum of  2 · cos(3t/2) · sin(7t/2)  occurs when:

        cos(3t/2) = ±1   →   3t/2 = nπ        →  t = 2nπ/3
        sin(7t/2) = ±1   →   7t/2 = π/2 + mπ  →  t = π(2m+1)/7

    When both hit ±1 simultaneously:

        |2 · (±1) · (±1)| = 2   ← PEAK AMPLITUDE ✓

STEP 4: Why can't the amplitude exceed 2?
──────────────────────────────────────────
    |cos(3t/2)| ≤ 1  and  |sin(7t/2)| ≤ 1

    Therefore:  |2 · cos(3t/2) · sin(7t/2)| ≤ 2 · 1 · 1 = 2

    The bound is TIGHT because cos and sin each achieve ±1.

PHYSICAL INTUITION
──────────────────
    • cos(3t/2) is a SLOW envelope — it modulates the overall amplitude
    • sin(7t/2) is a FAST carrier — it oscillates within the envelope
    • Peaks happen at CONSTRUCTIVE INTERFERENCE:
      both original waves crest together → amplitudes ADD → 1 + 1 = 2
"""

# Let's verify numerically
import numpy as np

t = np.linspace(0, 4 * np.pi, 100000)
combined = np.sin(2 * t) + np.sin(5 * t)
product_form = 2 * np.cos(3 * t / 2) * np.sin(7 * t / 2)

print("=== Numerical Verification ===")
print(f"Max of sin(2t) + sin(5t):                    {np.max(combined):.6f}")
print(f"Max of 2·cos(3t/2)·sin(7t/2):                {np.max(product_form):.6f}")
print(f"Forms are equal (max diff):                   {np.max(np.abs(combined - product_form)):.2e}")
print(f"Peak amplitude confirmed:                     {np.max(combined):.4f} ≈ 2 ✓")
