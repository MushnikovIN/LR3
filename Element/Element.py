
from abc import ABC, abstractmethod
from typing import Literal

class Element(ABC):
    def __init__(self, el_type : Literal["R", "L", "C"], node_begin : int, node_end : int):
        self.el_type = el_type
        self.__node_begin = node_begin
        self.__node_end = node_end


class R(Element):
    """Активный элемент
    Args:
        resistance: Сопротивление в Омах (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, resistance : int, node_begin : int, node_end : int):
        super().__init__(node_begin, node_end)
        self.__resistance = resistance


class L(Element):
    """Индуктивный элемент
    Args:
        inductance: Индуктивность в Гн (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, inductance: int, node_begin: int, node_end: int):
        super().__init__(node_begin, node_end)
        self.__inductance = inductance


class C(Element):
    """Емкостной элемент
    Args:
        capacity: Емкость в Ф (целое число больше 0)
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, capacity: int, node_begin: int, node_end: int):
        super().__init__(node_begin, node_end)
        self.__capacity = capacity

class E(Element):
    """Источник напряжения
    Args:
        voltage: ЭДС источника в В
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, voltage: int, node_begin: int, node_end: int):
        super().__init__(node_begin, node_end)
        self.__voltage = voltage


class J(Element):
    """Источник тока
    Args:
        current: Ток источника в А
        node_begin: Номер начального узла
        node_end: Номер конечного узла
    """
    def __init__(self, current: int, node_begin: int, node_end: int):
        super().__init__(node_begin, node_end)
        self.__current = current


