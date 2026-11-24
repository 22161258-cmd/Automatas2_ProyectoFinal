"""Operandos y cuaduplos (operador, argumento1, argumento2, resultado)."""
from dataclasses import dataclass
from decimal import Decimal
@dataclass(frozen=True)
class Operando:
    direccion:str|None=None; valor:object=None
    @classmethod
    def ref(cls,direccion): return cls(direccion=direccion)
    @classmethod
    def literal(cls,valor): return cls(valor=valor)
    @property
    def es_literal(self): return self.direccion is None
    def __str__(self):
        if not self.es_literal: return self.direccion or "_"
        if isinstance(self.valor,str): return repr(self.valor)
        if isinstance(self.valor,Decimal): return format(self.valor,"f")
        return "_" if self.valor is None else str(self.valor)
@dataclass
class Cuadruplo:
    operador:str; arg1:Operando|None=None; arg2:Operando|None=None; resultado:str|int|None=None; linea:int=1
    def fila(self,indice): return f"{indice:04d}  ({self.operador}, {self.arg1 or '_'}, {self.arg2 or '_'}, {self.resultado if self.resultado is not None else '_'})"
def formatear(codigo): return "\n".join(q.fila(i) for i,q in enumerate(codigo))