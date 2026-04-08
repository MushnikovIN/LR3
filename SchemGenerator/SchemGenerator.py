"""
amplitude
phase
"""


class Branch:
    def __init__(self, num: int, node_begin: int, node_end: int, type : str, G_eq: float = 0.0, J_eq: float = 0.0):
        self.num = num
        self.node_begin = node_begin
        self.node_end = node_end
        self.R_eq = R_eq
        self.E_eq = E_eq
    
class Circuit:
    def __init__(self, branches: list[Branch] = None):
        self.branches = branches if branches is not None else []
    
    def add_branch(self, branch: Branch):
        """Добавить ветвь в схему"""
        self.branches.append(branch)
    
    def get_branch_count(self) -> int:
        """Получить количество ветвей в схеме"""
        return len(self.branches)
    
    def __repr__(self):
        return f"Circuit(branches_count={len(self.branches)}, branches={self.branches})"

"""
class SchemGenerator:
    def __init__(self, circuit_data : dict):
        for i in dfdf
"""