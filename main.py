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
    
    # =========================================================================
    # РАСЧЕТ ТОКОВ И НАПРЯЖЕНИЙ ИСХОДНОЙ СХЕМЫ
    # =========================================================================
    print("\nРасчет токов ветвей и напряжений узлов исходной схемы...")
    
    # Массивы для сохранения результатов исходной схемы
    time_array_orig = time_array.copy()
    original_branch_currents_history = defaultdict(list)  # Токи ветвей исходной схемы
    node_voltages_history = defaultdict(list)  # Напряжения между узлами
    
    # Получаем уникальные узлы исходной схемы
    all_nodes = set()
    for elem in elements:
        all_nodes.add(elem.node_begin)
        all_nodes.add(elem.node_end)
    all_nodes = sorted(list(all_nodes))
    
    # Группируем элементы исходной схемы по ветвям
    original_branches_dict = {}
    for elem in elements:
        key = (elem.node_begin, elem.node_end)
        if key not in original_branches_dict:
            original_branches_dict[key] = []
        original_branches_dict[key].append(elem)
    
    # Используем уже рассчитанные данные из основного цикла
    # Для каждого шага времени восстанавливаем потенциалы узлов и рассчитываем токи
    print(f"  Обработка {len(time_array)} шагов времени...")
    
    # Временный генератор схемы для восстановления состояния на каждом шаге
    schem_gen_replay = SchemGenerator(elements, dt)
    
    # Начальный шаг (0)
    nodal_branches_0, nodes_count_0 = schem_gen_replay.convert_to_nodal_analysis()
    G_0 = schem_gen_replay.get_conductance_matrix(nodal_branches_0, nodes_count_0)
    I_0 = schem_gen_replay.get_current_vector(nodal_branches_0, nodes_count_0)
    node_potentials_0 = solver.solve_nodal_analysis(G_0, I_0)
    currents_0 = solver.calculate_branch_currents(nodal_branches_0, node_potentials_0)
    voltages_0 = solver.calculate_branch_voltages(nodal_branches_0, node_potentials_0)
    schem_gen_replay.update_history(voltages_0, currents_0)
    
    # Сохраняем потенциалы узлов для шага 0
    # Узел 0 - базисный с потенциалом 0
    # node_potentials_0 содержит потенциалы узлов 1, 2, ..., nodes_count-1
    potentials_full_0 = [0.0] + node_potentials_0
    for node in all_nodes:
        if node == 0:
            node_voltages_history[node].append(0.0)  # Базисный узел
        elif node < len(potentials_full_0):
            node_voltages_history[node].append(potentials_full_0[node])
        else:
            node_voltages_history[node].append(0.0)  # Если узла нет в решениях
    
    # Рассчитываем токи через каждую ветвь исходной схемы для шага 0
    for (node_begin, node_end), elems in original_branches_dict.items():
        u_begin = potentials_full_0[node_begin] if node_begin < len(potentials_full_0) else 0.0
        u_end = potentials_full_0[node_end] if node_end < len(potentials_full_0) else 0.0
        u_branch = u_begin - u_end
        
        R_total = 0.0
        L_elem = None
        C_elem = None
        E_total = 0.0
        J_total = 0.0
        
        for elem in elems:
            elem_type = elem.__class__.__name__
            if elem_type == 'R':
                R_total += elem.resistance
            elif elem_type == 'L':
                L_elem = elem
            elif elem_type == 'C':
                C_elem = elem
            elif elem_type == 'E':
                E_total += elem.voltage
            elif elem_type == 'J':
                J_total += elem.current
        
        branch_key = f"{node_begin}-{node_end}"
        
        if J_total != 0:
            branch_current = J_total
        elif L_elem is not None:
            elem_key = (L_elem.node_begin, L_elem.node_end)
            branch_current = schem_gen_replay.L_current_history.get(elem_key, 0.0)
        elif C_elem is not None:
            branch_current = 0.0  # Начальный ток через емкость
        else:
            if R_total > 0:
                branch_current = (u_branch - E_total) / R_total
            else:
                branch_current = 0.0
        
        original_branch_currents_history[branch_key].append(branch_current)
    
    # Основной цикл для остальных шагов
    for step_idx in range(1, len(time_array)):
        dommel_branches = schem_gen_replay.transform_to_dommel()
        nodal_branches, nodes_count = schem_gen_replay.convert_to_nodal_analysis()
        G = schem_gen_replay.get_conductance_matrix(nodal_branches, nodes_count)
        I = schem_gen_replay.get_current_vector(nodal_branches, nodes_count)
        node_potentials = solver.solve_nodal_analysis(G, I)
        currents = solver.calculate_branch_currents(nodal_branches, node_potentials)
        voltages = solver.calculate_branch_voltages(nodal_branches, node_potentials)
        
        # Добавляем базисный узел с потенциалом 0
        potentials_full = [0.0] + node_potentials
        
        # Сохраняем потенциалы узлов
        for node in all_nodes:
            if node == 0:
                node_voltages_history[node].append(0.0)  # Базисный узел
            elif node < len(potentials_full):
                node_voltages_history[node].append(potentials_full[node])
            else:
                node_voltages_history[node].append(0.0)
        
        # Рассчитываем токи через каждую ветвь исходной схемы
        for (node_begin, node_end), elems in original_branches_dict.items():
            u_begin = potentials_full[node_begin] if node_begin < len(potentials_full) else 0.0
            u_end = potentials_full[node_end] if node_end < len(potentials_full) else 0.0
            u_branch = u_begin - u_end
            
            R_total = 0.0
            L_elem = None
            C_elem = None
            E_total = 0.0
            J_total = 0.0
            
            for elem in elems:
                elem_type = elem.__class__.__name__
                if elem_type == 'R':
                    R_total += elem.resistance
                elif elem_type == 'L':
                    L_elem = elem
                elif elem_type == 'C':
                    C_elem = elem
                elif elem_type == 'E':
                    E_total += elem.voltage
                elif elem_type == 'J':
                    J_total += elem.current
            
            branch_key = f"{node_begin}-{node_end}"
            
            if J_total != 0:
                branch_current = J_total
            elif L_elem is not None:
                elem_key = (L_elem.node_begin, L_elem.node_end)
                branch_current = schem_gen_replay.L_current_history.get(elem_key, 0.0)
            elif C_elem is not None:
                elem_key = (C_elem.node_begin, C_elem.node_end)
                u_C_prev = schem_gen_replay.C_voltage_history.get(elem_key, 0.0)
                u_C_curr = u_branch
                branch_current = C_elem.capacity * (u_C_curr - u_C_prev) / dt
            else:
                if R_total > 0:
                    branch_current = (u_branch - E_total) / R_total
                else:
                    branch_current = 0.0
            
            original_branch_currents_history[branch_key].append(branch_current)
        
        # Обновляем историю реактивных элементов
        schem_gen_replay.update_history(voltages, currents)
        
        # Прогресс
        if step_idx % (len(time_array) // 10) == 0 or step_idx == len(time_array) - 1:
            progress = 100 * step_idx / (len(time_array) - 1)
            print(f"  Шаг {step_idx} из {len(time_array)-1} ({progress:.0f}%)")
    
    print(f"  Рассчитано токов для {len(original_branch_currents_history)} ветвей")
    print(f"  Рассчитано потенциалов для {len(node_voltages_history)} узлов")
    
    # Создаем фигуру с подграфиками
    num_plots = len(original_branch_currents_history) + len(all_nodes)
    fig_height = max(6, num_plots * 2.5)
    
    if num_plots == 1:
        fig, ax_single = plt.subplots(1, 1, figsize=(12, fig_height))
        axes = [ax_single]
    else:
        fig, axes = plt.subplots(num_plots, 1, figsize=(12, fig_height))
        axes = list(axes) if not isinstance(axes, list) else axes
    
    plot_idx = 0
    
    # График токов ветвей исходной схемы
    for branch_key, values in original_branch_currents_history.items():
        ax = axes[plot_idx]
        ax.plot(time_array_orig, values, label=f'Ток ветви {branch_key}', color='blue', linewidth=1.5)
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Ток, А')
        ax.set_title(f'Ток ветви {branch_key} исходной схемы')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        plot_idx += 1
    
    # График потенциалов узлов
    for node in all_nodes:
        ax = axes[plot_idx]
        ax.plot(time_array_orig, node_voltages_history[node], label=f'Потенциал узла {node}', color='green', linewidth=1.5)
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Напряжение, В')
        ax.set_title(f'Потенциал узла {node}')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        plot_idx += 1
    
    plt.tight_layout()
    plt.savefig('/workspace/results.png', dpi=150, bbox_inches='tight')
    print(f"\nГрафики сохранены в файл: /workspace/results.png")
    plt.show()
    
    # Вывод финальных значений
    print("\n" + "=" * 60)
    print("Финальные значения (на последний момент времени):")
    print("=" * 60)
    
    print("\nТоки в ветвях исходной схемы:")
    for branch_key, values in original_branch_currents_history.items():
        print(f"  Ветвь {branch_key}: {values[-1]:.6f} А")
    
    print("\nПотенциалы узлов:")
    for node in all_nodes:
        print(f"  Узел {node}: {node_voltages_history[node][-1]:.6f} В")
    
    print("\nНапряжения между узлами:")
    for i, node1 in enumerate(all_nodes):
        for node2 in all_nodes[i+1:]:
            voltage_diff = node_voltages_history[node1][-1] - node_voltages_history[node2][-1]
            print(f"  U({node1}-{node2}): {voltage_diff:.6f} В")


if __name__ == "__main__":
    main()
