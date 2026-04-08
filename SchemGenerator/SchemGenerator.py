"""
amplitude
phase
"""

class Branch:
    def __init__(self, num: int, node_begin: int, node_end: int, type : str, G: float = 0.0, J: float = 0.0):
        self.num = num
        self.node_begin = node_begin
        self.node_end = node_end
        self.R_eq = R_eq
        self.E_eq = E_eq




    
class Circuit:
    def __init__(self, circuit_data):
        self.branches = SchemGenerator.scheme_gerate(circuit_data)
    
    def add_branch(self, branch: Branch):
        """Добавить ветвь в схему"""
        self.branches.append(branch)
    
    def get_branch_count(self) -> int:
        """Получить количество ветвей в схеме"""
        return len(self.branches)



class SchemGenerator:
    @staticmethod
    def scheme_gerate(circuit_data : dict):
        circuit_data = circuit_data.get('circuit', {})
        branch_count = circuit_data.get('branch_count', {})
        branches_data = circuit_data.get('branches', [])
        for branch in branches_data:
            #здесь создание объекта класса Branch и преобразование к JG-ветви
