"""
Классы для описания электрической схемы
"""


class Branch:
    """Ветвь электрической схемы по методу Доммеля
    
    Ветвь представлена эквивалентной схемой замещения:
    - Сопротивление R_eq
    - Источник напряжения E_eq
    
    Для индуктивностей и емкостей используется метод Доммеля,
    который заменяет их на комбинацию сопротивления и источника напряжения.
    
    Args:
        num: Номер ветви
        node_begin: Номер начального узла
        node_end: Номер конечного узла
        R_eq: Эквивалентное сопротивление ветви
        E_eq: Эквивалентная ЭДС ветви
    """
    
    def __init__(self, num: int, node_begin: int, node_end: int, 
                 R_eq: float = 0.0, E_eq: float = 0.0):
        self.num = num
        self.node_begin = node_begin
        self.node_end = node_end
        self.R_eq = R_eq
        self.E_eq = E_eq
    
    def __repr__(self):
        return (f"Branch(num={self.num}, nodes=[{self.node_begin}-{self.node_end}], "
                f"R_eq={self.R_eq}, E_eq={self.E_eq})")


class Circuit:
    """Электрическая схема, содержащая набор ветвей
    
    Args:
        branches: Список ветвей схемы
    """
    
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
