import json
from typing import List
import sys
sys.path.append('/workspace')

from Element.Element import R, L, C, E, J, Element


class ConfigReader:
    """Читатель конфигурации схемы из JSON файла
    
    Args:
        config_path: Путь к JSON файлу с конфигурацией схемы
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.branch_count = 0
        self.branches_data = []
    
    def read(self) -> List[Element]:
        """Читает конфиг и возвращает список элементов схемы
        
        Returns:
            Список объектов элементов схемы
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        circuit = config.get('circuit', {})
        self.branch_count = circuit.get('branch_count', 0)
        self.branches_data = circuit.get('branches', [])
        
        elements = []
        
        for branch in self.branches_data:
            node_begin = branch['node_begin']
            node_end = branch['node_end']
            
            # Создаем элементы для каждой ветви
            # R элемент
            if branch.get('R', 0) != 0:
                elements.append(R(branch['R'], node_begin, node_end))
            
            # L элемент
            if branch.get('L', 0) != 0:
                elements.append(L(branch['L'], node_begin, node_end))
            
            # C элемент
            if branch.get('C', 0) != 0:
                elements.append(C(branch['C'], node_begin, node_end))
            
            # E источник напряжения
            if branch.get('E', 0) != 0:
                elements.append(E(branch['E'], node_begin, node_end))
            
            # J источник тока
            if branch.get('J', 0) != 0:
                elements.append(J(branch['J'], node_begin, node_end))
        
        return elements
    
    def get_branch_count(self) -> int:
        """Возвращает количество ветвей в схеме"""
        return self.branch_count
    
    def get_nodes_count(self) -> int:
        """Возвращает количество узлов в схеме"""
        if not self.branches_data:
            return 0
        
        max_node = 0
        for branch in self.branches_data:
            max_node = max(max_node, branch['node_begin'], branch['node_end'])
        
        return max_node + 1  # Узлы нумеруются с 0
