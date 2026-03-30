import numpy as np
import matplotlib.pyplot as plt

# Time axis
t = np.linspace(0, 2 * np.pi, 1000)

# Two sine waves with different frequencies
wave1 = np.sin(2 * t)      # 2 Hz
wave2 = np.sin(5 * t)      # 5 Hz

# Sum of the two waves
combined = wave1 + wave2

# Plot
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

axes[0].plot(t, wave1, color="steelblue")
axes[0].set_title("Sine Wave 1 — sin(2t)")
axes[0].set_ylabel("Amplitude")

axes[1].plot(t, wave2, color="coral")
axes[1].set_title("Sine Wave 2 — sin(5t)")
axes[1].set_ylabel("Amplitude")

axes[2].plot(t, combined, color="mediumseagreen")
axes[2].set_title("Sum — sin(2t) + sin(5t)")
axes[2].set_ylabel("Amplitude")
axes[2].set_xlabel("Time (radians)")

plt.tight_layout()
plt.savefig("/home/vivekkarmarkar/Python Files/livekit-project/sum_of_sines.png", dpi=150)
plt.show()
