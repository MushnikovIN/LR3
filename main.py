import sys
sys.path.append('/workspace')

from Config.ConfigReader import ConfigReader
from SchemGenerator.SchemGenerator import SchemGenerator, Branch
from Solver.Solver import Solver
import matplotlib.pyplot as plt
from collections import defaultdict


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
    
    # Параметры моделирования
    dt = 0.000001  # 1 мкс - шаг интегрирования
    total_time = 0.01  # 10 мс - общее время моделирования
    num_steps = int(total_time / dt)
    
    print(f"\nПараметры моделирования:")
    print(f"  Шаг интегрирования dt = {dt} с ({dt*1e6:.0f} мкс)")
    print(f"  Общее время моделирования = {total_time} с ({total_time*1e3:.1f} мс)")
    print(f"  Количество шагов = {num_steps}")
    
    # Создание генератора схемы
    schem_generator = SchemGenerator(elements, dt)
    
    # =========================================================================
    # ЭТАП 2: Преобразование накопителей в активные сопротивления с источниками
    # =========================================================================
    print("\n" + "=" * 70)
    print("ЭТАП 2: ПРЕОБРАЗОВАНИЕ НАКОПИТЕЛЕЙ В АКТИВНЫЕ СОПРОТИВЛЕНИЯ")
    print("         (МЕТОД ДОММЕЛЯ)")
    print("=" * 70)
    
    # Преобразование элементов по методу Доммеля
    dommel_branches = schem_generator.transform_to_dommel()
    
    print(f"\nСхема после преобразования по методу Доммеля:")
    print(f"  Количество ветвей: {len(dommel_branches)}")
    
    print("\n  Параметры ветвей (активное сопротивление + источники):")
    for i, branch in enumerate(dommel_branches, 1):
        print(f"\n  Ветчь {i} (узлы {branch.node_begin}-{branch.node_end}):")
        print(f"    Активное сопротивление R = {branch.resistance:.6f} Ом")
        print(f"    Источник напряжения E = {branch.voltage_source:.6f} В")
        print(f"    Источник тока J = {branch.current_source:.6f} А")
    
    # =========================================================================
    # ЭТАП 3: ПОШАГОВОЕ МОДЕЛИРОВАНИЕ С СОХРАНЕНИЕМ ДАННЫХ
    # =========================================================================
    print("\n" + "=" * 70)
    print("ЭТАП 3: ПОШАГОВОЕ МОДЕЛИРОВАНИЕ")
    print("=" * 70)
    
    # Массивы для сохранения результатов
    time_array = []
    currents_history = defaultdict(list)  # Токи по ветвям
    voltages_history = defaultdict(list)  # Напряжения по ветвям
    
    solver = Solver()
    
    print(f"\nЗапуск моделирования...")
    print(f"  Шаг 0 из {num_steps}")
    
    # Начальный расчет (шаг 0)
    nodal_branches, nodes_count = schem_generator.convert_to_nodal_analysis()
    G = schem_generator.get_conductance_matrix(nodal_branches, nodes_count)
    I = schem_generator.get_current_vector(nodal_branches, nodes_count)
    
    node_potentials = solver.solve_nodal_analysis(G, I)
    currents = solver.calculate_branch_currents(nodal_branches, node_potentials)
    voltages = solver.calculate_branch_voltages(nodal_branches, node_potentials)
    
    # Сохраняем начальные значения
    time_array.append(0.0)
    for key, current in currents.items():
        currents_history[key].append(current)
    for key, voltage in voltages.items():
        voltages_history[key].append(voltage)
    
    # Обновляем историю реактивных элементов
    schem_generator.update_history(voltages, currents)
    
    # Основной цикл моделирования
    for step in range(1, num_steps + 1):
        # Преобразование по методу Доммеля с обновленными значениями истории
        dommel_branches = schem_generator.transform_to_dommel()
        
        # Преобразование к схеме для метода узловых потенциалов
        nodal_branches, nodes_count = schem_generator.convert_to_nodal_analysis()
        
        # Формирование матрицы проводимостей и вектора токов
        G = schem_generator.get_conductance_matrix(nodal_branches, nodes_count)
        I = schem_generator.get_current_vector(nodal_branches, nodes_count)
        
        # Решение системы уравнений
        node_potentials = solver.solve_nodal_analysis(G, I)
        
        # Расчет токов и напряжений в ветвях
        currents = solver.calculate_branch_currents(nodal_branches, node_potentials)
        voltages = solver.calculate_branch_voltages(nodal_branches, node_potentials)
        
        # Сохранение результатов
        current_time = step * dt
        time_array.append(current_time)
        for key, current in currents.items():
            currents_history[key].append(current)
        for key, voltage in voltages.items():
            voltages_history[key].append(voltage)
        
        # Обновление истории реактивных элементов
        schem_generator.update_history(voltages, currents)
        
        # Вывод прогресса
        if step % (num_steps // 10) == 0 or step == num_steps:
            print(f"  Шаг {step} из {num_steps} ({100*step/num_steps:.0f}%)")
    
    print(f"\nМоделирование завершено!")
    print(f"  Всего сохранено точек: {len(time_array)}")
    print(f"  Ветвей с данными: {len(currents_history)}")
    
    # =========================================================================
    # ЭТАП 4: ПОСТРОЕНИЕ ГРАФИКОВ
    # =========================================================================
    print("\n" + "=" * 70)
    print("ЭТАП 4: ПОСТРОЕНИЕ ГРАФИКОВ")
    print("=" * 70)
    
    # Создаем фигуру с подграфиками
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # График токов
    ax1 = axes[0]
    for key, values in currents_history.items():
        label = f'Ток ветви {key[0]}-{key[1]}'
        ax1.plot(time_array, values, label=label, linewidth=1.5)
    ax1.set_xlabel('Время, с')
    ax1.set_ylabel('Ток, А')
    ax1.set_title('Зависимость токов в ветвях от времени')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')
    
    # График напряжений
    ax2 = axes[1]
    for key, values in voltages_history.items():
        label = f'Напряжение ветви {key[0]}-{key[1]}'
        ax2.plot(time_array, values, label=label, linewidth=1.5)
    ax2.set_xlabel('Время, с')
    ax2.set_ylabel('Напряжение, В')
    ax2.set_title('Зависимость напряжений на ветвях от времени')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best')
    
    plt.tight_layout()
    plt.savefig('/workspace/results.png', dpi=150, bbox_inches='tight')
    print(f"\nГрафики сохранены в файл: /workspace/results.png")
    plt.show()
    
    # Вывод финальных значений
    print("\n" + "=" * 60)
    print("Финальные значения (на последний момент времени):")
    print("=" * 60)
    
    print("\nТоки в ветвях:")
    for key, values in currents_history.items():
        print(f"  Ветвь {key[0]}-{key[1]}: {values[-1]:.6f} А")
    
    print("\nНапряжения на ветвях:")
    for key, values in voltages_history.items():
        print(f"  Ветвь {key[0]}-{key[1]}: {values[-1]:.6f} В")


if __name__ == "__main__":
    main()
