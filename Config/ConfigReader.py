"""
ConfigReader - модуль для чтения конфигурации схемы из JSON файла
и создания объектов схемы с использованием метода Доммеля
"""

import json
from typing import Optional
from SchemGenerator.SchemGenerator import Circuit, Branch


class ConfigReader:
    """Читатель конфигурации для создания электрической схемы
    
    Читает данные из JSON файла и создает объекты схемы,
    применяя метод Доммеля для преобразования накопителей (L, C)
    в эквивалентные схемы замещения (сопротивление + источник напряжения).
    
    Метод Доммеля:
    - Для индуктивности: R_eq = 2L/dt, E_eq = (2L/dt)*i(t-dt) + u(t-dt)
    - Для емкости: R_eq = dt/(2C), E_eq = u(t-dt) + (dt/(2C))*i(t-dt)
    
    Args:
        config_path: Путь к файлу конфигурации JSON
        dt: Шаг интегрирования для метода Доммеля (по умолчанию 0.001)
    """
    
    def __init__(self, config_path: str, dt: float = 0.001):
        self.config_path = config_path
        self.dt = dt
        self._config_data = None
    
    def read_config(self) -> dict:
        """Прочитать конфигурацию из JSON файла
        
        Returns:
            Словарь с данными конфигурации
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config_data = json.load(f)
        return self._config_data
    
    def _calculate_dommel_R(self, R: float, L: float, C: float) -> float:
        """Вычислить эквивалентное сопротивление по методу Доммеля
        
        Для резистора: R_eq = R
        Для индуктивности: R_eq = 2L/dt
        Для емкости: R_eq = dt/(2C)
        
        Args:
            R: Активное сопротивление
            L: Индуктивность
            C: Емкость
            
        Returns:
            Эквивалентное сопротивление ветви
        """
        R_eq = R
        
        if L > 0:
            R_eq += 2 * L / self.dt
        
        if C > 0:
            # Для емкости сопротивление добавляется последовательно
            R_eq += self.dt / (2 * C)
        
        return R_eq
    
    def _calculate_dommel_E(self, R: float, L: float, C: float, 
                            E_source: float, J_source: float,
                            i_prev: float = 0.0, u_L_prev: float = 0.0, 
                            u_C_prev: float = 0.0) -> float:
        """Вычислить эквивалентную ЭДС по методу Доммеля
        
        Для индуктивности: E_eq = (2L/dt)*i(t-dt) + u(t-dt)
        Для емкости: E_eq = u(t-dt) + (dt/(2C))*i(t-dt)
        
        Args:
            R: Активное сопротивление
            L: Индуктивность
            C: Емкость
            E_source: Источник напряжения в ветви
            J_source: Источник тока в ветви
            i_prev: Ток на предыдущем шаге
            u_L_prev: Напряжение на индуктивности на предыдущем шаге
            u_C_prev: Напряжение на емкости на предыдущем шаге
            
        Returns:
            Эквивалентная ЭДС ветви
        """
        E_eq = E_source
        
        # Учитываем влияние источника тока через падение напряжения на сопротивлении
        if J_source != 0:
            R_eq_temp = self._calculate_dommel_R(R, L, C)
            E_eq -= J_source * R_eq_temp
        
        if L > 0:
            # Исторический источник для индуктивности
            E_eq += (2 * L / self.dt) * i_prev + u_L_prev
        
        if C > 0:
            # Исторический источник для емкости
            E_eq += u_C_prev + (self.dt / (2 * C)) * i_prev
        
        return E_eq
    
    def create_branch(self, branch_data: dict, 
                     i_prev: float = 0.0, u_L_prev: float = 0.0, 
                     u_C_prev: float = 0.0) -> Branch:
        """Создать ветвь схемы из данных конфигурации
        
        Применяет метод Доммеля для преобразования параметров ветви
        в эквивалентную схему замещения.
        
        Args:
            branch_data: Словарь с параметрами ветви из конфигурации
            i_prev: Ток через ветвь на предыдущем шаге
            u_L_prev: Напряжение на индуктивности на предыдущем шаге
            u_C_prev: Напряжение на емкости на предыдущем шаге
            
        Returns:
            Объект Branch с эквивалентными параметрами
        """
        num = branch_data.get('num', 0)
        node_begin = branch_data.get('node_begin', 0)
        node_end = branch_data.get('node_end', 0)
        R = branch_data.get('R', 0.0)
        L = branch_data.get('L', 0.0)
        C = branch_data.get('C', 0.0)
        E = branch_data.get('E', 0.0)
        J = branch_data.get('J', 0.0)
        
        R_eq = self._calculate_dommel_R(R, L, C)
        E_eq = self._calculate_dommel_E(R, L, C, E, J, i_prev, u_L_prev, u_C_prev)
        
        return Branch(num=num, node_begin=node_begin, node_end=node_end,
                     R_eq=R_eq, E_eq=E_eq)
    
    def create_circuit(self) -> Circuit:
        """Создать объект схемы из конфигурации
        
        Читает конфигурацию из файла и создает все ветви схемы,
        применяя метод Доммеля для накопителей.
        
        Returns:
            Объект Circuit со всеми ветвями
        """
        if self._config_data is None:
            self.read_config()
        
        circuit_data = self._config_data.get('circuit', {})
        branches_data = circuit_data.get('branches', [])
        
        circuit = Circuit()
        
        for branch_data in branches_data:
            branch = self.create_branch(branch_data)
            circuit.add_branch(branch)
        
        return circuit


def main():
    """Пример использования ConfigReader"""
    # Создаем читатель конфигурации
    reader = ConfigReader('Config/config.json', dt=0.001)
    
    # Читаем конфигурацию и создаем схему
    circuit = reader.create_circuit()
    
    print(f"Создана схема с {circuit.get_branch_count()} ветвями:")
    for branch in circuit.branches:
        print(f"  {branch}")


if __name__ == '__main__':
    main()
