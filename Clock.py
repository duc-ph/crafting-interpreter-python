from __future__ import annotations
import time
from typing import List, TYPE_CHECKING
from LoxCallable import LoxCallable

if TYPE_CHECKING:
    from Interpreter import Interpreter


class Clock(LoxCallable):
    def arity(self):
        return 0

    def call(self, interpreter: Interpreter, arguments: List[object]):
        return time.time()

    def toString(self) -> str:
        return '<native fn>'
