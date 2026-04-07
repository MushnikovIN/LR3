from typing import List, Tuple
import sys
sys.path.append('/workspace')

from SchemGenerator.SchemGenerator import Branch


class Solver:
    """Решатель системы уравнений метода узловых потенциалов
    
    Решает систему линейных уравнений G * U = I, где:
    - G - матрица проводимостей
    - U - вектор узловых потенциалов
    - I - вектор токовых источников
    """
    
    @staticmethod
    def solve_nodal_analysis(G: List[List[float]], I: List[float]) -> List[float]:
        """Решает систему уравнений методом узловых потенциалов
        
        Args:
            G: Матрица проводимостей (n x n)
            I: Вектор токовых источников (n)
        
        Returns:
            Вектор узловых потенциалов (n)
        """
        n = len(I)
        
        # Создаем расширенную матрицу [G | I]
        augmented = [row[:] + [I[i]] for i, row in enumerate(G)]
        
        # Прямой ход метода Гаусса
        for i in range(n):
            # Поиск ведущего элемента
            max_row = i
            for k in range(i + 1, n):
                if abs(augmented[k][i]) > abs(augmented[max_row][i]):
                    max_row = k
            
            # Обмен строк
            augmented[i], augmented[max_row] = augmented[max_row], augmented[i]
            
            # Проверка на вырожденность
            if abs(augmented[i][i]) < 1e-10:
                continue
            
            # Исключение переменной
            for k in range(i + 1, n):
                factor = augmented[k][i] / augmented[i][i]
                for j in range(i, n + 1):
                    augmented[k][j] -= factor * augmented[i][j]
        
        # Обратный ход
        X = [0.0] * n
        for i in range(n - 1, -1, -1):
            if abs(augmented[i][i]) < 1e-10:
                X[i] = 0.0
            else:
                X[i] = augmented[i][n]
                for j in range(i + 1, n):
                    X[i] -= augmented[i][j] * X[j]
                X[i] /= augmented[i][i]
        
        return X
    
    @staticmethod
    def calculate_branch_currents(branches: List[Branch], node_potentials: List[float]) -> dict:
        """Вычисляет токи в ветвях схемы
        
        Args:
            branches: Список ветвей схемы
            node_potentials: Вектор узловых потенциалов (без базисного узла)
        
        Returns:
            Словарь токов {(node_begin, node_end): current}
        """
        currents = {}
        
        # Добавляем базисный узел с потенциалом 0
        potentials = [0.0] + node_potentials
        
        for branch in branches:
            key = (branch.node_begin, branch.node_end)
            
            u_begin = potentials[branch.node_begin]
            u_end = potentials[branch.node_end]
            
            # Ток через ветвь: I = (U_begin - U_end + E) / R + J
            # где E - источник напряжения (уже преобразован в ток), J - источник тока
            
            if branch.resistance > 0:
                # Ток от разности потенциалов
                branch_current = (u_begin - u_end) / branch.resistance
                # Добавляем источник тока
                branch_current += branch.current_source
            else:
                branch_current = branch.current_source
            
            currents[key] = branch_current
        
        return currents
    
    @staticmethod
    def calculate_branch_voltages(branches: List[Branch], node_potentials: List[float]) -> dict:
        """Вычисляет напряжения на ветвях схемы
        
        Args:
            branches: Список ветвей схемы
            node_potentials: Вектор узловых потенциалов (без базисного узла)
        
        Returns:
            Словарь напряжений {(node_begin, node_end): voltage}
        """
        voltages = {}
        
        # Добавляем базисный узел с потенциалом 0
        potentials = [0.0] + node_potentials
        
        for branch in branches:
            key = (branch.node_begin, branch.node_end)
            
            u_begin = potentials[branch.node_begin]
            u_end = potentials[branch.node_end]
            
            # Напряжение на ветви
            branch_voltage = u_begin - u_end
            
            voltages[key] = branch_voltage
        
        return voltages
