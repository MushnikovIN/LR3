import math
import numpy as np


class Solver:
    @staticmethod
    def solve_circuit(circuit : object, dt : float, T : float):
        branches = circuit.get_all_branches()
        G = circuit.get_G_matrix()
        A = circuit.get_A_matrix()
        t = 0
        U_res = np.zeros((circuit.node_count, 1))
        I_res = np.zeros((circuit.branch_count, 1))

        print(branches)

        while t < T-0.0000001:
            Jv = []
            for br in branches:
                #print(branches[br].get_type() == 'C')
                if branches[br].get_type() == 'L':
                    Jv.append(branches[br].i + branches[br].U * dt / 2 / branches[br].value)
                elif branches[br].get_type() == 'C':
                    Jv.append(0 - branches[br].i - branches[br].U / dt * 2 * branches[br].value)
                elif branches[br].get_type()  == 'Jsin':
                    Jv.append(branches[br].value[0]*math.sin(branches[br].value[1]*2*math.pi*t + branches[br].value[2]*math.pi/180))
                else:
                    Jv.append(branches[br].J)

            J = -A @ np.array(Jv)
            U = np.linalg.inv(G) @ J
            Up = np.insert(U, 0, [0], axis=0)
            Iv = np.diag(circuit.get_Gv_matrix()) @ A.T @ U + Jv

            U_res = np.column_stack((U_res, Up))
            I_res = np.column_stack((I_res, Iv))

            for br in branches:
                if (branches[br].type == 'L') or (branches[br].type  == 'C'):
                    branches[br].i = Iv[br-1]
                    branches[br].U = 0 - Up[branches[br].node_end] + Up[branches[br].node_begin]


            #PJ = U.T @ J
            #PG = U.T @ G @ U
            #
            #print(PJ, PG)
            t += dt

        U_res = np.delete(U_res, 0, axis=1)
        I_res = np.delete(I_res, 0, axis=1)


        return U_res, I_res
