import sys
sys.path.append('/workspace')

from Config.ConfigReader import ConfigReader
from SchemGenerator.SchemGenerator import SchemGenerator, Branch
from Solver.Solver import Solver


def main():
    """Основная функция демонстрации работы схемы"""
    
    # Чтение конфигурации из JSON файла
    config_reader = ConfigReader('/workspace/Config/config.json')
    elements = config_reader.read()
    
    print("=" * 60)
    print("Чтение конфигурации схемы из JSON")
    print("=" * 60)
    print(f"Количество ветвей: {config_reader.get_branch_count()}")
    print(f"Количество узлов: {config_reader.get_nodes_count()}")
    print(f"Элементы схемы: {len(elements)}")
    
    for elem in elements:
        print(f"  - {elem.__class__.__name__}: узлы {elem.node_begin}-{elem.node_end}")
    
    # Создание генератора схемы с шагом интегрирования dt
    dt = 0.001  # 1 мс
    schem_generator = SchemGenerator(elements, dt)
    
    print("\n" + "=" * 60)
    print("Преобразование по методу Доммеля")
    print("=" * 60)
    
    # Преобразование элементов по методу Доммеля
    dommel_branches = schem_generator.transform_to_dommel()
    
    print(f"Ветвей после преобразования: {len(dommel_branches)}")
    for branch in dommel_branches:
        print(f"  Ветвь {branch.node_begin}-{branch.node_end}: "
              f"R={branch.resistance:.4f} Ом, "
              f"E={branch.voltage_source:.4f} В, "
              f"J={branch.current_source:.4f} А")
    
    # Конвертация для метода узловых потенциалов
    print("\n" + "=" * 60)
    print("Конвертация для метода узловых потенциалов")
    print("=" * 60)
    
    nodal_branches, nodes_count = schem_generator.convert_to_nodal_analysis()
    
    print(f"Количество узлов: {nodes_count}")
    print(f"Ветвей для МУП: {len(nodal_branches)}")
    for branch in nodal_branches:
        print(f"  Ветвь {branch.node_begin}-{branch.node_end}: "
              f"R={branch.resistance:.4f} Ом, "
              f"J={branch.current_source:.4f} А")
    
    # Формирование матрицы проводимостей и вектора токов
    G = schem_generator.get_conductance_matrix(nodal_branches, nodes_count)
    I = schem_generator.get_current_vector(nodal_branches, nodes_count)
    
    print("\n" + "=" * 60)
    print("Матрица проводимостей G:")
    print("=" * 60)
    for row in G:
        print("  " + " ".join(f"{g:10.6f}" for g in row))
    
    print("\n" + "=" * 60)
    print("Вектор токовых источников I:")
    print("=" * 60)
    print("  " + " ".join(f"{i:10.6f}" for i in I))
    
    # Решение системы уравнений
    print("\n" + "=" * 60)
    print("Решение системы уравнений методом узловых потенциалов")
    print("=" * 60)
    
    solver = Solver()
    node_potentials = solver.solve_nodal_analysis(G, I)
    
    print(f"Потенциалы узлов (относительно базисного узла 0):")
    for i, potential in enumerate(node_potentials, start=1):
        print(f"  Узел {i}: {potential:.6f} В")
    
    # Расчет токов и напряжений в ветвях
    print("\n" + "=" * 60)
    print("Токи в ветвях:")
    print("=" * 60)
    currents = solver.calculate_branch_currents(nodal_branches, node_potentials)
    for key, current in currents.items():
        print(f"  Ветвь {key[0]}-{key[1]}: {current:.6f} А")
    
    print("\n" + "=" * 60)
    print("Напряжения на ветвях:")
    print("=" * 60)
    voltages = solver.calculate_branch_voltages(nodal_branches, node_potentials)
    for key, voltage in voltages.items():
        print(f"  Ветвь {key[0]}-{key[1]}: {voltage:.6f} В")


if __name__ == "__main__":
    main()
