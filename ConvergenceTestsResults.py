import matplotlib.pyplot as plt
import numpy as np


data = np.loadtxt('CuTaN2_Test/ENCUT_test/encut_convergence.dat')
encut, energy = data[:, 0], data[:, 1]

print(encut, energy)

plt.figure(figsize=(8, 6))
plt.plot(encut, energy, marker='o', linestyle='-', color='b')
plt.title('Energy Convergence with ENCUT')
plt.xlabel('ENCUT (eV)')
plt.ylabel('Total Energy (eV)')
plt.grid()
plt.savefig('encut_convergence.png')
