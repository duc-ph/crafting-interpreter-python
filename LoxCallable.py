from __future__ import annotations
from typing import List, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from Interpreter import Interpreter


class LoxCallable(ABC):

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: List[object]) -> object:
        ...

    @abstractmethod
    def arity(self) -> int:
        ...

    @abstractmethod
    def toString(self) -> str:
        ...
