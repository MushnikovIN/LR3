from Config.ConfigReader import read_config
from SchemGenerator.SchemGenerator import Circuit
from Solver.Solver import Solver
import numpy as np
import scipy.io

from graph_maker.graph_maker import graph_maker

filename = 'config1'
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


graph_maker(time_array, T, I_res, 2, U_res, 0, 2, filename)