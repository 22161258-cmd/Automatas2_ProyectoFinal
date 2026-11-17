"""Estructuras de datos que representan un programa TopScript."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Gasto:
    monto: Decimal
    descripcion: str
    linea: int
    columna: int


@dataclass(frozen=True)
class Categoria:
    nombre: str
    limite: Decimal
    gastos: tuple[Gasto, ...]
    linea: int
    columna: int


@dataclass(frozen=True)
class Presupuesto:
    nombre: str
    categorias: tuple[Categoria, ...]
