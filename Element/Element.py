
from abc import ABC, abstractmethod
from typing import Literal

class Element(ABC):
    def __init__(self, el_type : Literal["R", "L", "C", "E", "J"], node_begin : int, node_end : int):
        self.el_type = el_type
        self.__node_begin = node_begin
        self.__node_end = node_end
    
    @property
    def node_begin(self) -> int:
        return self.__node_begin
    
    @property
    def node_end(self) -> int:
        return self.__node_end


class R(Element):
    """Активный элемент
    Args:
        resistance: Сопротивление в Омах (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, resistance : float, node_begin : int, node_end : int):
        super().__init__("R", node_begin, node_end)
        self.__resistance = resistance
    
    @property
    def resistance(self) -> float:
        return self.__resistance


class L(Element):
    """Индуктивный элемент
    Args:
        inductance: Индуктивность в Гн (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, inductance: float, node_begin: int, node_end: int):
        super().__init__("L", node_begin, node_end)
        self.__inductance = inductance
    
    @property
    def inductance(self) -> float:
        return self.__inductance


class C(Element):
    """Емкостной элемент
    Args:
        capacity: Емкость в Ф (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, capacity: float, node_begin: int, node_end: int):
        super().__init__("C", node_begin, node_end)
        self.__capacity = capacity
    
    @property
    def capacity(self) -> float:
        return self.__capacity

class E(Element):
    """Источник напряжения
    Args:
        voltage: ЭДС источника в В
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, voltage: float, node_begin: int, node_end: int):
        super().__init__("E", node_begin, node_end)
        self.__voltage = voltage
    
    @property
    def voltage(self) -> float:
        return self.__voltage


class J(Element):
    """Источник тока
    Args:
        current: Ток источника в А
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, current: float, node_begin: int, node_end: int):
        super().__init__("J", node_begin, node_end)
        self.__current = current
    
    @property
    def current(self) -> float:
        return self.__current


