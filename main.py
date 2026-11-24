"""CLI del compilador e interprete TopScript."""
import argparse,sys
from pathlib import Path
from compiler import compilar
from cuadruplos import formatear
from errores import TopScriptError
from lexer import tokenizar
from optimizador import optimizar
from parser import parsear
from runtime import ejecutar

def mostrar_tabla(comp):
    filas=["Nombre | Clase | Tipo | Direccion | Ambito | Linea","-"*70]
    filas.extend("{} | {} | {} | {} | {} | {}".format(*f) for f in comp.tabla.filas())
    return "\n".join(filas)
def main():
    p=argparse.ArgumentParser(description="Compilador e interprete de TopScript")
    p.add_argument("archivo",type=Path,help="archivo fuente .top")
    p.add_argument("--tokens",action="store_true",help="mostrar tokens")
    p.add_argument("--tabla-simbolos",action="store_true",help="mostrar tabla de simbolos")
    p.add_argument("--cuadruplos",action="store_true",help="mostrar codigo intermedio")
    p.add_argument("--optimizar",action="store_true",help="optimizar cuaduplos")
    a=p.parse_args()
    try:
        fuente=a.archivo.read_text(encoding="utf-8-sig"); tokens=tokenizar(fuente)
        if a.tokens: print("TOKENS\n"+"\n".join(map(str,(t for t in tokens if t.tipo!="EOF")))+"\n")
        programa=parsear(tokens); comp=compilar(programa)
        codigo=optimizar(comp.codigo) if a.optimizar else comp.codigo
        if a.tabla_simbolos: print("TABLA DE SIMBOLOS\n"+mostrar_tabla(comp)+"\n")
        if a.cuadruplos: print("CUADRUPLOS"+(" OPTIMIZADOS" if a.optimizar else "")+"\n"+formatear(codigo)+"\n")
        print(ejecutar(codigo,comp.nombre_presupuesto)); return 0
    except TopScriptError as e: print(e,file=sys.stderr); return 1
    except (OSError,UnicodeError) as e: print(f"No se pudo leer {a.archivo}: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())