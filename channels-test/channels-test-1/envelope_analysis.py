import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# General parameters
omega1 = 2    # frequency of first sine
omega2 = 5    # frequency of second sine

# Derived envelope/carrier frequencies
omega_env = (omega2 - omega1) / 2    # = 3/2, slow envelope
omega_car = (omega2 + omega1) / 2    # = 7/2, fast carrier

# Time axis — go far out to see convergence
t = np.linspace(0, 40 * np.pi, 200000)

# The decomposed form
envelope = 2 * np.cos(omega_env * t)
carrier = np.sin(omega_car * t)
combined = envelope * carrier

# ─── FIGURE 1: Envelope + carrier with local windows ───
fig1, axes = plt.subplots(2, 1, figsize=(14, 8))

# Top panel: show envelope and combined wave
ax = axes[0]
ax.plot(t, combined, color="mediumseagreen", alpha=0.7, linewidth=0.5, label=r"$2\cos(\omega_e t)\sin(\omega_c t)$")
ax.plot(t, envelope, color="steelblue", linewidth=2, label=r"Envelope: $2\cos(\omega_e t)$")
ax.plot(t, -envelope, color="steelblue", linewidth=2, alpha=0.5)
ax.set_ylabel("Amplitude", fontsize=12)
ax.set_title(
    rf"Envelope–Carrier Decomposition: $\omega_1={omega1},\;\omega_2={omega2}$"
    rf"$\;\Rightarrow\;\omega_e={omega_env},\;\omega_c={omega_car}$",
    fontsize=13
)
ax.legend(fontsize=11, loc="upper right")
ax.set_xlim(0, 12 * np.pi)

# Find envelope peaks (cos = 1 → omega_env * t = 2nπ)
n_peaks = 8
peak_times = [2 * n * np.pi / omega_env for n in range(1, n_peaks + 1)]

# For each envelope peak, find the nearest carrier peak (sin = 1)
delta_t_window = np.pi / omega_car  # half-period of carrier
peak_values = []

for tp in peak_times:
    # Window around envelope peak
    mask = np.abs(t - tp) < delta_t_window
    t_window = t[mask]
    c_window = combined[mask]
    if len(c_window) > 0:
        idx_max = np.argmax(c_window)
        peak_val = c_window[idx_max]
        t_peak = t_window[idx_max]
        peak_values.append((tp, t_peak, peak_val))
        # Shade the window
        ax.axvspan(tp - delta_t_window, tp + delta_t_window, alpha=0.1, color="coral")
        ax.plot(t_peak, peak_val, "ro", markersize=6, zorder=5)

ax.axhline(y=2, color="red", linestyle="--", alpha=0.5, label="Supremum = 2")
ax.legend(fontsize=11, loc="upper right")

# Bottom panel: zoom into one envelope peak to show local structure
zoom_peak = peak_times[2]  # 3rd peak
zoom_width = 3 * delta_t_window
mask_zoom = np.abs(t - zoom_peak) < zoom_width
t_zoom = t[mask_zoom]

ax2 = axes[1]
ax2.plot(t_zoom, combined[mask_zoom], color="mediumseagreen", linewidth=1.5, label="Combined wave")
ax2.plot(t_zoom, envelope[mask_zoom], color="steelblue", linewidth=2, label="Envelope")
ax2.axvspan(zoom_peak - delta_t_window, zoom_peak + delta_t_window, alpha=0.15, color="coral", label=rf"Window $\Delta t = \pi/\omega_c$")
ax2.axhline(y=2, color="red", linestyle="--", alpha=0.5)

# Mark the peak
for tp, t_pk, pv in peak_values:
    if abs(tp - zoom_peak) < 0.1:
        ax2.plot(t_pk, pv, "ro", markersize=10, zorder=5)
        ax2.annotate(f"peak = {pv:.4f}", (t_pk, pv), textcoords="offset points",
                     xytext=(15, 10), fontsize=11, color="red", fontweight="bold")

ax2.set_xlabel("Time $t$", fontsize=12)
ax2.set_ylabel("Amplitude", fontsize=12)
ax2.set_title(f"Zoomed View Near Envelope Peak at $t \\approx {zoom_peak:.2f}$", fontsize=13)
ax2.legend(fontsize=11)

plt.tight_layout()
plt.savefig("/home/vivekkarmarkar/Python Files/livekit-project/envelope_analysis_fig1.png", dpi=150)


# ─── FIGURE 2: Convergence to supremum ───
fig2, ax3 = plt.subplots(figsize=(10, 6))

# Compute actual peak near each successive envelope maximum over a long range
N_max = 50
all_peak_vals = []
all_n = []
all_theoretical = []

for n in range(1, N_max + 1):
    tp = 2 * n * np.pi / omega_env
    # Search in a window of one carrier half-period
    t_local = np.linspace(tp - delta_t_window, tp + delta_t_window, 10000)
    combined_local = 2 * np.cos(omega_env * t_local) * np.sin(omega_car * t_local)
    max_val = np.max(combined_local)
    all_peak_vals.append(max_val)
    all_n.append(n)

    # Theoretical approximation: the nearest carrier peak is at most
    # delta_t* away, where delta_t* ≤ π/(2·omega_car)
    # Peak ≈ 2·(1 - omega_env² · delta_t*² / 2)
    # Find actual delta_t*
    idx_max = np.argmax(combined_local)
    dt_star = abs(t_local[idx_max] - tp)
    approx_val = 2 * (1 - omega_env**2 * dt_star**2 / 2)
    all_theoretical.append(approx_val)

ax3.plot(all_n, all_peak_vals, "o-", color="mediumseagreen", markersize=5, label="Actual peak near $n$-th envelope max")
ax3.plot(all_n, all_theoretical, "s--", color="coral", markersize=4, alpha=0.7, label=r"Quadratic approx: $2(1 - \omega_e^2 \Delta t_*^2 / 2)$")
ax3.axhline(y=2, color="red", linestyle="--", linewidth=1.5, label="Supremum = 2")
ax3.set_xlabel("Envelope peak index $n$", fontsize=12)
ax3.set_ylabel("Peak amplitude", fontsize=12)
ax3.set_title(
    rf"Convergence to Supremum: $\omega_1={omega1},\;\omega_2={omega2}$"
    rf"$\;\;(\omega_e={omega_env},\;\omega_c={omega_car})$",
    fontsize=13
)
ax3.legend(fontsize=11)
ax3.set_ylim(1.85, 2.01)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("/home/vivekkarmarkar/Python Files/livekit-project/envelope_analysis_fig2.png", dpi=150)

plt.show()

print(f"\nFrequency parameters:")
print(f"  ω₁ = {omega1}, ω₂ = {omega2}")
print(f"  ω_env = (ω₂-ω₁)/2 = {omega_env}")
print(f"  ω_car = (ω₂+ω₁)/2 = {omega_car}")
print(f"  Carrier half-period = π/ω_car = {np.pi/omega_car:.4f}")
print(f"\nPeak values at successive envelope maxima:")
for i, v in enumerate(all_peak_vals[:10], 1):
    print(f"  n={i:2d}: peak = {v:.6f},  gap from 2 = {2-v:.6f}")
