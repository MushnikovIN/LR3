import matplotlib.pyplot as plt
import numpy as np

def graph_maker(time_array, T, I_res, branch_num, U_res, node_begin, node_end, filename):

    # Создаем фигуру с подграфиками
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    time_ticks = np.arange(0, T+0.000001, 0.001)

    # График токов
    ax1 = axes[0]
    label = f'Ток ветви {branch_num}'
    ax1.plot(time_array, I_res[branch_num-1], label=label, linewidth=1.5)
    ax1.set_xlabel('Время, с')
    ax1.set_ylabel('Ток, А')
    ax1.set_title('Зависимость токов в ветвях от времени')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(time_ticks)
    ax1.legend(loc='best')

    # График напряжений
    ax2 = axes[1]
    label = f'Напряжение между углами {node_end} и {node_begin}'
    ax2.plot(time_array, U_res[node_end] - U_res[node_begin] , label=label, linewidth=1.5)
    ax2.set_xlabel('Время, с')
    ax2.set_ylabel('Напряжение, В')
    ax2.set_title('Зависимость напряжения узла от времени')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(time_ticks)
    ax2.legend(loc='best')

    plt.tight_layout()
    plt.savefig(f'modeling_results/{filename}_graph.png', dpi=150, bbox_inches='tight')
    print(f"\nГрафики сохранены в файл: {filename}_graph.png")
    plt.show()