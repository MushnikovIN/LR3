from typing import List, Tuple
import sys
sys.path.append('/workspace')

from Element.Element import R, L, C, E, J, Element


class Branch:
    """Класс представляющий ветвь схемы после преобразования по методу Доммеля
    
    Args:
        node_begin: Начальный узел
        node_end: Конечный узел
        resistance: Сопротивление ветви (Ом)
        voltage_source: Источник напряжения (В) - для последовательной модели
        current_source: Источник тока (А) - для параллельной модели
    """
    
    def __init__(self, node_begin: int, node_end: int, resistance: float = 0.0, 
                 voltage_source: float = 0.0, current_source: float = 0.0):
        self.node_begin = node_begin
        self.node_end = node_end
        self.resistance = resistance
        self.voltage_source = voltage_source
        self.current_source = current_source


class SchemGenerator:
    """Генератор схемы для метода узловых потенциалов
    
    Преобразует индуктивные и емкостные элементы в сопротивление и источник
    напряжения/тока по методу Доммеля (Dommel's method).
    
    Метод Доммеля использует численное интегрирование для дискретизации
    дифференциальных уравнений элементов L и C.
    
    Для индуктивности L:
        u_L(t) = L * di_L/dt
        Дискретизация (метод трапеций):
        i_L(t) = i_L(t-Δt) + (Δt/(2L)) * (u_L(t) + u_L(t-Δt))
        Эквивалентная схема: параллельно R_L = 2L/Δt и источник тока I_history
    
    Для емкости C:
        i_C(t) = C * du_C/dt
        Дискретизация (метод трапеций):
        u_C(t) = u_C(t-Δt) + (Δt/(2C)) * (i_C(t) + i_C(t-Δt))
        Эквивалентная схема: параллельно R_C = Δt/(2C) и источник тока I_history
    """
    
    def __init__(self, elements: List[Element], dt: float = 0.000001):
        """
        Args:
            elements: Список элементов схемы
            dt: Шаг интегрирования (секунды)
        """
        self.elements = elements
        self.dt = dt
        self.branches: List[Branch] = []
        
        # История токов и напряжений для реактивных элементов
        self.L_current_history = {}  # Ключ: (node_begin, node_end), значение: i_L(t-Δt)
        self.C_voltage_history = {}  # Ключ: (node_begin, node_end), значение: u_C(t-Δt)
    
    def _get_element_key(self, element: Element) -> Tuple[int, int]:
        """Создает ключ для идентификации элемента"""
        return (element.node_begin, element.node_end)
    
    def transform_to_dommel(self) -> List[Branch]:
        """Преобразует все элементы схемы по методу Доммеля
        
        Returns:
            Список ветвей с эквивалентными сопротивлениями и источниками
        """
        self.branches = []
        
        # Группируем элементы по ветвям (по парам узлов)
        branches_dict = {}
        
        for element in self.elements:
            key = (element.node_begin, element.node_end)
            if key not in branches_dict:
                branches_dict[key] = {
                    'R': 0.0,
                    'L_elem': None,
                    'C_elem': None,
                    'E': 0.0,
                    'J': 0.0
                }
            
            if isinstance(element, R):
                branches_dict[key]['R'] += element.resistance
            elif isinstance(element, L):
                branches_dict[key]['L_elem'] = element
            elif isinstance(element, C):
                branches_dict[key]['C_elem'] = element
            elif isinstance(element, E):
                branches_dict[key]['E'] += element.voltage
            elif isinstance(element, J):
                branches_dict[key]['J'] += element.current
        
        # Преобразуем каждую ветвь
        for key, branch_data in branches_dict.items():
            node_begin, node_end = key
            
            total_resistance = branch_data['R']
            voltage_source = branch_data['E']
            current_source = branch_data['J']
            
            # Преобразование индуктивности по методу Доммеля
            if branch_data['L_elem'] is not None:
                L_elem = branch_data['L_elem']
                L_val = L_elem.inductance
                R_L = 2 * L_val / self.dt  # Эквивалентное сопротивление
                
                # Получаем историю тока
                elem_key = self._get_element_key(L_elem)
                i_history = self.L_current_history.get(elem_key, 0.0)
                
                # Источник тока от истории: I_hist = i_L(t-Δt) + (Δt/(2L)) * u_L(t-Δt)
                # Для упрощения считаем только i_L(t-Δt)
                current_source += i_history
                
                # Добавляем сопротивление индуктивности параллельно
                if total_resistance > 0:
                    total_resistance = (total_resistance * R_L) / (total_resistance + R_L)
                else:
                    total_resistance = R_L
            
            # Преобразование емкости по методу Доммеля
            if branch_data['C_elem'] is not None:
                C_elem = branch_data['C_elem']
                C_val = C_elem.capacity
                R_C = self.dt / (2 * C_val)  # Эквивалентное сопротивление
                
                # Получаем историю напряжения
                elem_key = self._get_element_key(C_elem)
                u_history = self.C_voltage_history.get(elem_key, 0.0)
                
                # Источник тока от истории: I_hist = (2C/Δt) * u_C(t-Δt) + i_C(t-Δt)
                I_hist = (2 * C_val / self.dt) * u_history
                current_source += I_hist
                
                # Добавляем сопротивление емкости параллельно
                if total_resistance > 0:
                    total_resistance = (total_resistance * R_C) / (total_resistance + R_C)
                else:
                    total_resistance = R_C
            
            # Создаем ветвь
            branch = Branch(
                node_begin=node_begin,
                node_end=node_end,
                resistance=total_resistance,
                voltage_source=voltage_source,
                current_source=current_source
            )
            self.branches.append(branch)
        
        return self.branches
    
    def update_history(self, voltages: dict, currents: dict):
        """Обновляет историю токов и напряжений после расчета шага
        
        Args:
            voltages: Словарь напряжений на элементах {(node_begin, node_end): voltage}
            currents: Словарь токов через элементы {(node_begin, node_end): current}
        """
        for element in self.elements:
            key = self._get_element_key(element)
            
            if isinstance(element, L):
                self.L_current_history[key] = currents.get(key, 0.0)
            elif isinstance(element, C):
                self.C_voltage_history[key] = voltages.get(key, 0.0)
    
    def convert_to_nodal_analysis(self) -> Tuple[List[Branch], int]:
        """Конвертирует схему для метода узловых потенциалов
        
        Преобразует источники напряжения с последовательным сопротивлением
        в источники тока с параллельным сопротивлением (преобразование Нортона).
        
        Returns:
            Кортеж из списка ветвей и количества узлов
        """
        nodal_branches = []
        
        for branch in self.branches:
            # Если есть источник напряжения, преобразуем его в источник тока
            if branch.voltage_source != 0 and branch.resistance > 0:
                # Преобразование Нортона: I_N = E / R
                norton_current = branch.voltage_source / branch.resistance
                
                nodal_branch = Branch(
                    node_begin=branch.node_begin,
                    node_end=branch.node_end,
                    resistance=branch.resistance,
                    voltage_source=0.0,
                    current_source=branch.current_source + norton_current
                )
                nodal_branches.append(nodal_branch)
            else:
                # Если нет источника напряжения или сопротивление нулевое
                nodal_branches.append(Branch(
                    node_begin=branch.node_begin,
                    node_end=branch.node_end,
                    resistance=branch.resistance,
                    voltage_source=0.0,
                    current_source=branch.current_source
                ))
        
        # Определяем количество узлов
        max_node = 0
        for branch in nodal_branches:
            max_node = max(max_node, branch.node_begin, branch.node_end)
        
        return nodal_branches, max_node + 1
    
    def get_conductance_matrix(self, branches: List[Branch], nodes_count: int) -> List[List[float]]:
        """Формирует матрицу проводимостей для метода узловых потенциалов
        
        Args:
            branches: Список ветвей схемы
            nodes_count: Количество узлов
        
        Returns:
            Матрица проводимостей размером (nodes_count-1) x (nodes_count-1)
            (базисный узел не учитывается)
        """
        # Размер матрицы на 1 меньше (исключаем базисный узел)
        n = nodes_count - 1
        G = [[0.0] * n for _ in range(n)]
        
        for branch in branches:
            if branch.resistance == 0:
                continue
            
            g = 1.0 / branch.resistance  # Проводимость ветви
            
            i = branch.node_begin
            j = branch.node_end
            
            # Если узел не базисный (не 0)
            if i != 0 and j != 0:
                G[i-1][i-1] += g
                G[j-1][j-1] += g
                G[i-1][j-1] -= g
                G[j-1][i-1] -= g
            elif i == 0 and j != 0:
                G[j-1][j-1] += g
            elif i != 0 and j == 0:
                G[i-1][i-1] += g
        
        return G
    
    def get_current_vector(self, branches: List[Branch], nodes_count: int) -> List[float]:
        """Формирует вектор токовых источников для метода узловых потенциалов
        
        Args:
            branches: Список ветвей схемы
            nodes_count: Количество узлов
        
        Returns:
            Вектор токов размером (nodes_count-1)
        """
        n = nodes_count - 1
        I = [0.0] * n
        
        for branch in branches:
            i = branch.node_begin
            j = branch.node_end
            
            # Ток входит в узел j и выходит из узла i
            if j != 0:
                I[j-1] += branch.current_source
            if i != 0:
                I[i-1] -= branch.current_source
        
        return I
