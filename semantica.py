"""Validaciones semanticas de TopScript v1."""

from errores import ErrorSemantico
from modelos import Presupuesto


def validar(presupuesto: Presupuesto) -> None:
    if not presupuesto.nombre.strip():
        raise ErrorSemantico("el nombre del presupuesto no puede estar vacio", 1, 1)

    nombres = set()
    for categoria in presupuesto.categorias:
        if categoria.nombre in nombres:
            raise ErrorSemantico(
                f"la categoria {categoria.nombre!r} esta declarada mas de una vez",
                categoria.linea,
                categoria.columna,
            )
        nombres.add(categoria.nombre)

        if categoria.limite <= 0:
            raise ErrorSemantico(
                "el limite debe ser mayor que cero",
                categoria.linea,
                categoria.columna,
            )

        for gasto in categoria.gastos:
            if gasto.monto < 0:
                raise ErrorSemantico(
                    "el monto de un gasto no puede ser negativo",
                    gasto.linea,
                    gasto.columna,
                )
