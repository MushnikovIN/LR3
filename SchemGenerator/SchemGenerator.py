"""
amplitude
phase
"""
import math
import numpy as np


class Branch:
    def __init__(self, num: int, node_begin: int, node_end: int, type : str, value : float,
                 G: float = 0.0, J: float = 0.0, U : float = 0.0, i : float = 0.0, start_phase_deg : float = 0.0):
        self.num = num
        self.node_begin = node_begin
        self.node_end = node_end
        self.type = type
        self.value = value
        self.G = G #Проводимость ветви в схеме замещения
        self.J = J #Значение тока источника на некотором шаге
        self.U = U #Значение напряжения на выводах ветви на некотором шаге
        self.i = i #Значение тока ветви
        self.start_phase_deg = start_phase_deg

    def get_node_begin(self):
        return self.node_begin

    def get_node_end(self):
        return self.node_end

    def get_G(self):
        return self.G

    def get_type(self):
        return self.type

    def __repr__(self):
        return str(self.__dict__)


class Circuit:
    def __init__(self, circuit_data, dt : float):
        self.branches = SchemGenerator.scheme_gerate(circuit_data, dt)
        self.branch_count = circuit_data.get('circuit', {}).get('branch_count', {})
        self.node_count = circuit_data.get('circuit', {}).get('node_count', {})
        #print(self.node_count)
        self.A_matrix = SchemGenerator.make_A_matrix(self.branches, self.branch_count, self.node_count)
        self.G_matrix, self.Gv_matrix= SchemGenerator.make_G_matrix(self.branches, self.A_matrix)
    
    def add_branch(self, branch: Branch):
        """Добавить ветвь в схему"""
        self.branches.append(branch)
    
    def get_branch_count(self) -> int:
        """Получить количество ветвей в схеме"""
        return len(self.branches)

    def get_all_branches(self):
        return self.branches

    def get_A_matrix(self):
        return self.A_matrix

    def get_G_matrix(self):
        return self.G_matrix

    def get_Gv_matrix(self):
        return self.Gv_matrix

    def __repr__(self):
        return str(self.branches)


class SchemGenerator:
    @staticmethod
    def scheme_gerate(circuit_data : dict, dt : float):
        circuit_data = circuit_data.get('circuit', {})
        branch_count = circuit_data.get('branch_count', {})
        branches_data = circuit_data.get('branches', [])
        branches = {}
        for branch in branches_data:
            start_phase = 0
            match branch['type']:
                case 'R':
                    J = 0
                    G = 1/branch['value']
                case 'L':
                    J = 0
                    G = dt / 2 / branch['value']
                case 'C':
                    J = 0
                    G = 2*branch['value']/dt
                case 'E':
                    J = branch['value']/0.000001
                    G = 1/0.000001
                case 'J':
                    J = branch['value']
                    G = 0
                case 'Jsin':
                    J = branch['value'][0]*math.sin(branch['value'][2]*math.pi/180)
                    start_phase = branch['value'][2]
                    G = 0

            branches[branch['num']] = Branch(*branch.values(), G, J, 0, 0, start_phase)
        return branches
            #здесь создание объекта класса Branch и преобразование к JG-ветви

    @staticmethod
    def make_A_matrix(branches : dict, branch_count : int, node_count : int):
        A = np.zeros((node_count, branch_count))
        for br in branches:
            A[branches[br].get_node_begin(), br-1] = 1
            A[branches[br].get_node_end(), br-1] = -1
        A = np.delete(A, 0, axis=0) #Нулевой узел принимается за базисный всегда
        #print(A)
        return A

    @staticmethod
    def make_G_matrix(branches : dict, A : list):
        Gv = []
        for br in branches:
            Gv.append(branches[br].get_G())
        G = A @ np.diag(Gv) @ (A.T)
        return G, Gv



