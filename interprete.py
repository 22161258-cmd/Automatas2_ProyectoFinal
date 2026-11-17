"""Ejecucion de un programa TopScript y generacion del reporte."""

from decimal import Decimal

from modelos import Presupuesto


CENTAVO = Decimal("0.01")


def _dinero(monto: Decimal) -> str:
    return f"${monto.quantize(CENTAVO):,.2f} MXN"


def ejecutar(presupuesto: Presupuesto) -> str:
    lineas = [f"Presupuesto: {presupuesto.nombre}", ""]
    excedidas = []

    for categoria in presupuesto.categorias:
        gastado = sum((gasto.monto for gasto in categoria.gastos), Decimal("0"))
        disponible = categoria.limite - gastado
        estado = "EXCEDIDO" if gastado > categoria.limite else (
            "AL LIMITE" if gastado == categoria.limite else "Dentro del limite"
        )
        lineas.append(
            f"{categoria.nombre} | Limite: {_dinero(categoria.limite)} | "
            f"Gastado: {_dinero(gastado)} | Disponible: {_dinero(disponible)} | {estado}"
        )
        if gastado > categoria.limite:
            excedidas.append((categoria.nombre, gastado - categoria.limite))

    lineas.append("")
    if excedidas:
        lineas.append("Alertas:")
        for nombre, exceso in excedidas:
            lineas.append(f"- {nombre}: excedio su limite por {_dinero(exceso)}.")
    else:
        lineas.append("Estado: dentro de los limites en todas las categorias.")

    return "\n".join(lineas)
