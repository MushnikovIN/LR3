import json
from typing import Optional
from SchemGenerator.SchemGenerator import Circuit, Branch



def read_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        print(config_data)
    return config_data



def _calculate_dommel_R(self, R: float, L: float, C: float) -> float:
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
    # Создаем читатель конфигурации
    reader = ConfigReader('config.json', dt=0.001)
    
    # Читаем конфигурацию и создаем схему
    circuit = reader.create_circuit()
    
    print(f"Создана схема с {circuit.get_branch_count()} ветвями:")
    for branch in circuit.branches:
        print(f"  {branch}")


if __name__ == '__main__':
    main()
