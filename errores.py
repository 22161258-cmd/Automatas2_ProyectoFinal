"""Errores del compilador e interprete TopScript."""
class TopScriptError(Exception):
    tipo = "TopScript"
    def __init__(self, mensaje: str, linea: int = 1, columna: int = 1) -> None:
        super().__init__(mensaje); self.mensaje=mensaje; self.linea=linea; self.columna=columna
    def __str__(self) -> str:
        return f"Error {self.tipo} en linea {self.linea}, columna {self.columna}: {self.mensaje}"
class ErrorLexico(TopScriptError): tipo="lexico"
class ErrorSintactico(TopScriptError): tipo="sintactico"
class ErrorSemantico(TopScriptError): tipo="semantico"
class ErrorEjecucion(TopScriptError): tipo="de ejecucion"