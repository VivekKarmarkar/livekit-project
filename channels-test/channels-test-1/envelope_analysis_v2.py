import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ═══════════════════════════════════════════════════════════════
# CASE 1: Rational frequencies → periodic, no convergence
# ═══════════════════════════════════════════════════════════════
omega1_rat = 2
omega2_rat = 5
omega_env_rat = (omega2_rat - omega1_rat) / 2   # 3/2
omega_car_rat = (omega2_rat + omega1_rat) / 2   # 7/2

# ═══════════════════════════════════════════════════════════════
# CASE 2: Irrational frequencies → equidistribution, convergence
# ═══════════════════════════════════════════════════════════════
omega1_irr = 2
omega2_irr = 2 + np.sqrt(2)   # ≈ 3.4142
omega_env_irr = (omega2_irr - omega1_irr) / 2   # √2/2
omega_car_irr = (omega2_irr + omega1_irr) / 2   # 2 + √2/2


def find_peaks_near_envelope_maxima(omega_env, omega_car, N_max=80):
    """For each envelope peak (cos=1), find the best combined peak nearby."""
    delta_t_window = np.pi / omega_car  # half-period of carrier
    peak_data = []

    for n in range(1, N_max + 1):
        tp = 2 * n * np.pi / omega_env  # envelope peak time
        t_local = np.linspace(tp - delta_t_window, tp + delta_t_window, 50000)
        combined_local = 2 * np.cos(omega_env * t_local) * np.sin(omega_car * t_local)
        idx_max = np.argmax(combined_local)
        max_val = combined_local[idx_max]
        dt_star = abs(t_local[idx_max] - tp)
        peak_data.append({
            'n': n,
            't_env': tp,
            't_peak': t_local[idx_max],
            'peak_val': max_val,
            'dt_star': dt_star,
            'gap': 2 - max_val,
        })
    return peak_data


peaks_rat = find_peaks_near_envelope_maxima(omega_env_rat, omega_car_rat, N_max=80)
peaks_irr = find_peaks_near_envelope_maxima(omega_env_irr, omega_car_irr, N_max=80)

# Running best (supremum approach)
running_best_rat = np.maximum.accumulate([p['peak_val'] for p in peaks_rat])
running_best_irr = np.maximum.accumulate([p['peak_val'] for p in peaks_irr])

# ═══════════════════════════════════════════════════════════════
# FIGURE 1: Side-by-side envelope + carrier for both cases
# ═══════════════════════════════════════════════════════════════
fig1 = plt.figure(figsize=(16, 10))
gs = GridSpec(2, 2, figure=fig1, hspace=0.35, wspace=0.25)

for col, (om_env, om_car, om1, om2, label) in enumerate([
    (omega_env_rat, omega_car_rat, omega1_rat, omega2_rat, "Rational"),
    (omega_env_irr, omega_car_irr, omega1_irr, omega2_irr, "Irrational"),
]):
    t = np.linspace(0, 16 * np.pi, 100000)
    envelope = 2 * np.cos(om_env * t)
    combined = 2 * np.cos(om_env * t) * np.sin(om_car * t)

    # Top: full view
    ax_top = fig1.add_subplot(gs[0, col])
    ax_top.plot(t, combined, color="mediumseagreen", alpha=0.6, linewidth=0.5)
    ax_top.plot(t, envelope, color="steelblue", linewidth=2, label="Envelope")
    ax_top.plot(t, -envelope, color="steelblue", linewidth=2, alpha=0.4)
    ax_top.axhline(y=2, color="red", linestyle="--", alpha=0.5)

    # Mark envelope peaks
    delta_t_w = np.pi / om_car
    for n in range(1, 7):
        tp = 2 * n * np.pi / om_env
        if tp < t[-1]:
            ax_top.axvspan(tp - delta_t_w, tp + delta_t_w, alpha=0.08, color="coral")
            # Find peak in window
            mask = np.abs(t - tp) < delta_t_w
            if np.any(mask):
                t_w = t[mask]
                c_w = combined[mask]
                idx = np.argmax(c_w)
                ax_top.plot(t_w[idx], c_w[idx], "ro", markersize=5, zorder=5)

    ax_top.set_title(
        f"{label}: $\\omega_1={om1:.4g},\\;\\omega_2={om2:.4g}$\n"
        f"$\\omega_e={om_env:.4g},\\;\\omega_c={om_car:.4g}$",
        fontsize=12
    )
    ax_top.set_ylabel("Amplitude")
    ax_top.set_xlim(0, 16 * np.pi)

    # Bottom: zoom into one peak
    zoom_n = 3
    zoom_tp = 2 * zoom_n * np.pi / om_env
    zoom_w = 3 * delta_t_w
    mask_z = np.abs(t - zoom_tp) < zoom_w
    ax_bot = fig1.add_subplot(gs[1, col])
    ax_bot.plot(t[mask_z], combined[mask_z], color="mediumseagreen", linewidth=1.5)
    ax_bot.plot(t[mask_z], envelope[mask_z], color="steelblue", linewidth=2)
    ax_bot.axvspan(zoom_tp - delta_t_w, zoom_tp + delta_t_w, alpha=0.12, color="coral")
    ax_bot.axhline(y=2, color="red", linestyle="--", alpha=0.5)

    # Find and mark peak
    mask_inner = np.abs(t - zoom_tp) < delta_t_w
    t_in = t[mask_inner]
    c_in = combined[mask_inner]
    idx = np.argmax(c_in)
    ax_bot.plot(t_in[idx], c_in[idx], "ro", markersize=10, zorder=5)
    ax_bot.annotate(f"peak = {c_in[idx]:.4f}", (t_in[idx], c_in[idx]),
                    textcoords="offset points", xytext=(15, -15),
                    fontsize=11, color="red", fontweight="bold")

    ax_bot.set_xlabel("Time $t$")
    ax_bot.set_ylabel("Amplitude")
    ax_bot.set_title(f"Zoom: envelope peak $n={zoom_n}$", fontsize=11)

fig1.suptitle("Envelope–Carrier Structure: Rational vs Irrational Frequency Ratios", fontsize=14, y=1.01)
plt.savefig("/home/vivekkarmarkar/Python Files/livekit-project/envelope_v2_fig1.png", dpi=150, bbox_inches="tight")


# ═══════════════════════════════════════════════════════════════
# FIGURE 2: Convergence comparison
# ═══════════════════════════════════════════════════════════════
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ns = [p['n'] for p in peaks_rat]

# Left: individual peak values
ax1.plot(ns, [p['peak_val'] for p in peaks_rat], "o", color="steelblue",
         markersize=4, alpha=0.6, label=f"Rational ($\\omega_e/\\omega_c = 3/7$)")
ax1.plot(ns, [p['peak_val'] for p in peaks_irr], "o", color="coral",
         markersize=4, alpha=0.6, label=f"Irrational ($\\omega_e/\\omega_c = \\sqrt{{2}}/(4+\\sqrt{{2}})$)")
ax1.axhline(y=2, color="red", linestyle="--", linewidth=1.5, label="Supremum = 2")
ax1.set_xlabel("Envelope peak index $n$", fontsize=12)
ax1.set_ylabel("Peak amplitude", fontsize=12)
ax1.set_title("Peak Values at Each Envelope Maximum", fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Right: running best (approach to supremum)
ax2.plot(ns, 2 - running_best_rat, "o-", color="steelblue", markersize=3,
         label="Rational: gap cycles (never converges)")
ax2.plot(ns, 2 - running_best_irr, "o-", color="coral", markersize=3,
         label="Irrational: gap shrinks → 0")
ax2.set_xlabel("Envelope peak index $n$", fontsize=12)
ax2.set_ylabel("Gap from supremum: $2 - \\mathrm{peak}$", fontsize=12)
ax2.set_title("Convergence to Supremum", fontsize=13)
ax2.set_yscale("log")
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, which="both")

plt.tight_layout()
plt.savefig("/home/vivekkarmarkar/Python Files/livekit-project/envelope_v2_fig2.png", dpi=150, bbox_inches="tight")

plt.show()

# Print summary
print("═" * 60)
print("RATIONAL CASE: ω₁=2, ω₂=5 → ω_e=3/2, ω_c=7/2")
print("═" * 60)
unique_peaks = sorted(set(round(p['peak_val'], 6) for p in peaks_rat), reverse=True)
print(f"Distinct peak values: {unique_peaks}")
print(f"Best achievable: {max(p['peak_val'] for p in peaks_rat):.6f}")
print(f"Gap from 2: {2 - max(p['peak_val'] for p in peaks_rat):.6f}")
print()
print("═" * 60)
print(f"IRRATIONAL CASE: ω₁=2, ω₂=2+√2 → ω_e=√2/2≈{omega_env_irr:.4f}, ω_c=2+√2/2≈{omega_car_irr:.4f}")
print("═" * 60)
print(f"Best peak (n≤80): {max(p['peak_val'] for p in peaks_irr):.6f}")
print(f"Gap from 2: {2 - max(p['peak_val'] for p in peaks_irr):.6f}")
print(f"\nTop 5 peaks (irrational):")
sorted_irr = sorted(peaks_irr, key=lambda p: p['peak_val'], reverse=True)
for p in sorted_irr[:5]:
    print(f"  n={p['n']:3d}: peak={p['peak_val']:.6f}, Δt*={p['dt_star']:.6f}, gap={p['gap']:.6f}")
