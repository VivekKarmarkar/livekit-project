import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 4 * np.pi, 500)
y = np.sin(x) + np.sin(2 * x)

plt.figure(figsize=(10, 5))
plt.plot(x, y, color='darkorange', linewidth=2)
plt.title('sin(x) + sin(2x)')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='gray', linewidth=0.5)
plt.tight_layout()
plt.savefig('/home/vivekkarmarkar/Python Files/livekit-project/sine_plot.png', dpi=150)
plt.show()
