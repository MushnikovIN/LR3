from Config.ConfigReader import read_config
from SchemGenerator.SchemGenerator import Circuit
from Solver.Solver import Solver
import numpy as np
import matplotlib.pyplot as plt
import scipy.io

filename = 'config3'
circuit_data = read_config(f'Config/{filename}.json')

dt = 0.000001
T = 0.01

circuit1  = Circuit(circuit_data, dt)
#print(circuit1.get_all_branches())
#print(circuit1)

# circuit_data1 = circuit_data.get('circuit', {})
# branches_data = circuit_data1.get('branches', [])
#print(circuit_data1)
#print(branches_data)

U_res, I_res = Solver.solve_circuit(circuit1, dt, T)

scipy.io.savemat(f'Modeling_results/{filename}_U.mat', {'U': U_res})
scipy.io.savemat(f'Modeling_results/{filename}_I.mat', {'I': I_res})

time_array = np.arange(0, T, dt)


# Создаем фигуру с подграфиками
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

time_ticks = np.arange(0, T+0.000001, 0.001)

# График токов
ax1 = axes[0]
label = f'Ток ветви 3'
ax1.plot(time_array, I_res[1], label=label, linewidth=1.5)
ax1.set_xlabel('Время, с')
ax1.set_ylabel('Ток, А')
ax1.set_title('Зависимость токов в ветвях от времени')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(time_ticks)
ax1.legend(loc='best')

# График напряжений
ax2 = axes[1]
label = f'Напряжение узла 6'
ax2.plot(time_array, U_res[6] , label=label, linewidth=1.5)
ax2.set_xlabel('Время, с')
ax2.set_ylabel('Напряжение, В')
ax2.set_title('Зависимость напряжения узла от времени')
ax2.grid(True, alpha=0.3)
ax2.set_xticks(time_ticks)
ax2.legend(loc='best')

plt.tight_layout()
plt.savefig(f'Modeling_results/{filename}_graph.png', dpi=150, bbox_inches='tight')
print(f"\nГрафики сохранены в файл: {filename}_graph.png")
plt.show()