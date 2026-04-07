import sys
sys.path.append('/workspace')

from Config.ConfigReader import ConfigReader
from SchemGenerator.SchemGenerator import SchemGenerator, Branch
from Solver.Solver import Solver


def main():
    """Основная функция демонстрации работы схемы"""
    
    # =========================================================================
    # ЭТАП 1: Считывание из файла config.json
    # =========================================================================
    print("=" * 70)
    print("ЭТАП 1: СЧИТЫВАНИЕ ИЗ ФАЙЛА config.json")
    print("=" * 70)
    
    config_reader = ConfigReader('Config/config.json')
    elements = config_reader.read()
    
    print(f"\nИсходная схема из config.json:")
    print(f"  Количество ветвей: {config_reader.get_branch_count()}")
    print(f"  Количество узлов: {config_reader.get_nodes_count()}")
    print(f"  Всего элементов: {len(elements)}")
    
    print("\n  Состав исходной схемы по элементам:")
    # Группируем элементы по ветвям для наглядного отображения
    branches_dict = {}
    for elem in elements:
        key = (elem.node_begin, elem.node_end)
        if key not in branches_dict:
            branches_dict[key] = []
        branches_dict[key].append(elem)
    
    for (node_begin, node_end), elems in branches_dict.items():
        print(f"\n  Ветвь {node_begin}-{node_end}:")
        for elem in elems:
            elem_type = elem.__class__.__name__
            if elem_type == 'R':
                print(f"    - R: {elem.resistance} Ом")
            elif elem_type == 'L':
                print(f"    - L: {elem.inductance} Гн")
            elif elem_type == 'C':
                print(f"    - C: {elem.capacity} Ф")
            elif elem_type == 'E':
                print(f"    - E: {elem.voltage} В")
            elif elem_type == 'J':
                print(f"    - J: {elem.current} А")
    
    # Создание генератора схемы с шагом интегрирования dt
    dt = 0.000001  # 1 мкс
    schem_generator = SchemGenerator(elements, dt)
    
    # =========================================================================
    # ЭТАП 2: Преобразование накопителей в активные сопротивления с источниками
    # =========================================================================
    print("\n" + "=" * 70)
    print("ЭТАП 2: ПРЕОБРАЗОВАНИЕ НАКОПИТЕЛЕЙ В АКТИВНЫЕ СОПРОТИВЛЕНИЯ")
    print("         (МЕТОД ДОММЕЛЯ)")
    print("=" * 70)
    
    print(f"\nПараметры преобразования:")
    print(f"  Шаг интегрирования dt = {dt} с ({dt*1e6:.0f} мкс)")
    
    # Преобразование элементов по методу Доммеля
    dommel_branches = schem_generator.transform_to_dommel()
    
    print(f"\nСхема после преобразования по методу Доммеля:")
    print(f"  Количество ветвей: {len(dommel_branches)}")
    
    print("\n  Параметры ветвей (активное сопротивление + источники):")
    for i, branch in enumerate(dommel_branches, 1):
        print(f"\n  Ветвь {i} (узлы {branch.node_begin}-{branch.node_end}):")
        print(f"    Активное сопротивление R = {branch.resistance:.6f} Ом")
        print(f"    Источник напряжения E = {branch.voltage_source:.6f} В")
        print(f"    Источник тока J = {branch.current_source:.6f} А")
        
        # Показываем эквивалентную схему
        if branch.voltage_source != 0 or branch.current_source != 0:
            print(f"    Эквивалентная схема: R последовательно с E или R параллельно с J")
    
    # =========================================================================
    # ЭТАП 3: Преобразование к схеме с источниками тока и активными сопротивлениями
    # =========================================================================
    print("\n" + "=" * 70)
    print("ЭТАП 3: ПРЕОБРАЗОВАНИЕ К СХЕМЕ С ИСТОЧНИКАМИ ТОКА")
    print("         (ПРЕОБРАЗОВАНИЕ НОРТОНА ДЛЯ МЕТОДА УЗЛОВЫХ ПОТЕНЦИАЛОВ)")
    print("=" * 70)
    
    nodal_branches, nodes_count = schem_generator.convert_to_nodal_analysis()
    
    print(f"\nСхема для метода узловых потенциалов:")
    print(f"  Количество узлов: {nodes_count}")
    print(f"  Количество ветвей: {len(nodal_branches)}")
    
    print("\n  Параметры ветвей (проводимости и источники тока):")
    for i, branch in enumerate(nodal_branches, 1):
        conductance = 1.0 / branch.resistance if branch.resistance > 0 else float('inf')
        print(f"\n  Ветвь {i} (узлы {branch.node_begin}-{branch.node_end}):")
        print(f"    Сопротивление R = {branch.resistance:.6f} Ом")
        if branch.resistance > 0:
            print(f"    Проводимость G = {conductance:.6f} См")
        else:
            print(f"    Проводимость G = ∞ (идеальный источник)")
        print(f"    Источник тока J = {branch.current_source:.6f} А")
    
    print("\n" + "-" * 70)
    print("  ИТОГО в новой схеме:")
    print(f"    Ветвей: {len(nodal_branches)}")
    print(f"    Узлов: {nodes_count} (из них базисный узел 0)")
    print(f"    Независимых узловых потенциалов: {nodes_count - 1}")
    print("-" * 70)
    
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
