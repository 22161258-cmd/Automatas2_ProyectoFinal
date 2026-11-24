"""Valida semantica y genera el codigo intermedio de TopScript."""
from dataclasses import dataclass
from decimal import Decimal
from ast_nodes import (Accion,Asignacion,Binaria,Bloque,Categoria,Condicional,Declaracion,Gasto,Literal,Mientras,ParaCada,Programa,Unaria,Variable)
from cuadruplos import Cuadruplo,Operando
from errores import ErrorSemantico
from symbol_table import TablaSimbolos
ENTERO,DECIMAL,TEXTO,LOGICO,CATEGORIA="entero","decimal","texto","logico","categoria"
NUMERICOS={ENTERO,DECIMAL}
@dataclass
class Compilacion:
    codigo:list[Cuadruplo]; tabla:TablaSimbolos; nombre_presupuesto:str
class Compilador:
    def __init__(self):
        self.codigo=[]; self.tabla=TablaSimbolos(); self.temporal=0; self.categoria_actual=None
        self.cantidad_categorias=0; self.cantidad_gastos_categoria=0; self.nombres_categorias=set()
    def emitir(self,op,a=None,b=None,r=None,linea=1):
        self.codigo.append(Cuadruplo(op,a,b,r,linea)); return len(self.codigo)-1
    def temp(self): self.temporal+=1; return f"t{self.temporal}"
    def error(self,n,m): raise ErrorSemantico(m,n.linea,n.columna)
    def compilar(self,programa):
        if not programa.nombre.strip(): self.error(programa,"el nombre del presupuesto no puede estar vacio")
        for n in programa.instrucciones: self.instruccion(n,superior=True)
        if not self.cantidad_categorias: self.error(programa,"el presupuesto debe declarar al menos una categoria")
        self.emitir("HALT",linea=programa.linea)
        return Compilacion(self.codigo,self.tabla,programa.nombre)
    def instruccion(self,n,superior=False):
        if isinstance(n,Declaracion):
            t,op=self.expresion(n.expresion)
            if not self.compatible(n.tipo,t): self.error(n,f"no se puede inicializar {n.tipo} con {t}")
            s=self.tabla.declarar(n.nombre,n.tipo,n.linea)
            if s is None: self.error(n,f"variable redeclarada en este ambito: {n.nombre!r}")
            op=self.convertir(t,n.tipo,op,n.linea); self.emitir("ASSIGN",op,r=s.direccion,linea=n.linea); return
        if isinstance(n,Asignacion):
            s=self.tabla.buscar(n.nombre)
            if s is None: self.error(n,f"variable no declarada: {n.nombre!r}")
            if s.tipo==CATEGORIA or s.clase=="alias_categoria": self.error(n,"no se puede asignar a una categoria")
            t,op=self.expresion(n.expresion)
            if not self.compatible(s.tipo,t): self.error(n,f"no se puede asignar {t} a una variable {s.tipo}")
            self.emitir("ASSIGN",self.convertir(t,s.tipo,op,n.linea),r=s.direccion,linea=n.linea); return
        if isinstance(n,Categoria):
            if not superior or self.categoria_actual is not None: self.error(n,"categoria solo se declara directamente dentro del presupuesto")
            if n.nombre in self.nombres_categorias: self.error(n,f"categoria duplicada: {n.nombre!r}")
            t,lim=self.expresion(n.limite)
            if t not in NUMERICOS: self.error(n,"el limite debe ser numerico")
            if lim.es_literal and lim.valor<=0: self.error(n,"el limite debe ser mayor que cero")
            lim=self.convertir(t,DECIMAL,lim,n.linea)
            s=self.tabla.declarar(n.nombre,CATEGORIA,n.linea,"categoria")
            if s is None: self.error(n,f"nombre ya declarado en este ambito: {n.nombre!r}")
            self.nombres_categorias.add(n.nombre); self.cantidad_categorias+=1
            self.emitir("CATEGORY",Operando.literal(n.nombre),lim,s.direccion,n.linea)
            self.emitir("ENTER_CATEGORY",Operando.ref(s.direccion),linea=n.linea)
            self.tabla.abrir(); self.categoria_actual=n.nombre; antes=self.cantidad_gastos_categoria
            for hijo in n.cuerpo.instrucciones: self.instruccion(hijo)
            if antes==self.cantidad_gastos_categoria: self.error(n,"cada categoria debe incluir al menos un gasto")
            self.categoria_actual=None; self.tabla.cerrar(); self.emitir("EXIT_CATEGORY",linea=n.linea); return
        if isinstance(n,Gasto):
            if self.categoria_actual is None: self.error(n,"gasto solo se permite dentro de una categoria")
            tm,m=self.expresion(n.monto); td,d=self.expresion(n.descripcion)
            if tm not in NUMERICOS: self.error(n,"el monto del gasto debe ser numerico")
            if td!=TEXTO: self.error(n,"la descripcion del gasto debe ser texto")
            self.emitir("EXPENSE",self.convertir(tm,DECIMAL,m,n.linea),d,linea=n.linea)
            self.cantidad_gastos_categoria+=1; return
        if isinstance(n,Condicional):
            t,c=self.expresion(n.condicion)
            if t!=LOGICO: self.error(n,"la condicion de si debe ser logica")
            j=self.emitir("GOTOF",c,r=None,linea=n.linea); self.bloque(n.entonces)
            if n.sino:
                fin=self.emitir("GOTO",r=None,linea=n.linea); self.codigo[j].resultado=len(self.codigo); self.bloque(n.sino); self.codigo[fin].resultado=len(self.codigo)
            else: self.codigo[j].resultado=len(self.codigo)
            return
        if isinstance(n,Mientras):
            inicio=len(self.codigo); t,c=self.expresion(n.condicion)
            if t!=LOGICO: self.error(n,"la condicion de mientras debe ser logica")
            salida=self.emitir("GOTOF",c,r=None,linea=n.linea); self.bloque(n.cuerpo)
            self.emitir("GOTO",r=inicio,linea=n.linea); self.codigo[salida].resultado=len(self.codigo); return
        if isinstance(n,ParaCada):
            self.tabla.abrir(); s=self.tabla.declarar(n.nombre,CATEGORIA,n.linea,"alias_categoria")
            if s is None: self.error(n,f"alias duplicado: {n.nombre!r}")
            it=self.temp(); self.emitir("ITER_INIT",r=it,linea=n.linea); inicio=len(self.codigo)
            salto=self.emitir("ITER_NEXT",Operando.ref(it),Operando.ref(s.direccion),None,n.linea)
            self.bloque(n.cuerpo); self.emitir("GOTO",r=inicio,linea=n.linea); self.codigo[salto].resultado=len(self.codigo); self.tabla.cerrar(); return
        if isinstance(n,Accion):
            _,op=self.expresion(n.expresion); self.emitir("PRINT" if n.tipo=="mostrar" else "ALERT",op,linea=n.linea); return
        if isinstance(n,Bloque): self.bloque(n); return
        self.error(n,"instruccion desconocida")
    def bloque(self,b):
        self.tabla.abrir()
        for n in b.instrucciones: self.instruccion(n)
        self.tabla.cerrar()
    def compatible(self,dest,src): return dest==src or (dest==DECIMAL and src==ENTERO)
    def convertir(self,src,dest,op,linea):
        if src==ENTERO and dest==DECIMAL:
            t=self.temp(); self.emitir("INT_TO_DEC",op,r=t,linea=linea); return Operando.ref(t)
        return op
    def expresion(self,n):
        if isinstance(n,Literal): return n.tipo,Operando.literal(n.valor)
        if isinstance(n,Variable):
            s=self.tabla.buscar(n.nombre)
            if s is None: self.error(n,f"identificador no declarado: {n.nombre!r}")
            if n.atributo is None:
                if s.tipo==CATEGORIA: self.error(n,"use un atributo de categoria: limite, gastado o nombre")
                return s.tipo,Operando.ref(s.direccion)
            if s.tipo!=CATEGORIA: self.error(n,"solo una categoria tiene atributos")
            attrs={"limite":DECIMAL,"gastado":DECIMAL,"nombre":TEXTO}
            if n.atributo not in attrs: self.error(n,f"atributo inexistente {n.atributo!r}; use limite, gastado o nombre")
            t=self.temp(); self.emitir("GET_ATTR",Operando.ref(s.direccion),Operando.literal(n.atributo),t,n.linea)
            return attrs[n.atributo],Operando.ref(t)
        if isinstance(n,Unaria):
            tipo,op=self.expresion(n.operando)
            if n.operador=="-":
                if tipo not in NUMERICOS: self.error(n,"el signo '-' requiere un operando numerico")
                t=self.temp(); self.emitir("NEG",op,r=t,linea=n.linea); return tipo,Operando.ref(t)
            if n.operador=="no":
                if tipo!=LOGICO: self.error(n,"'no' requiere un valor logico")
                t=self.temp(); self.emitir("NOT",op,r=t,linea=n.linea); return LOGICO,Operando.ref(t)
        if isinstance(n,Binaria):
            ta,a=self.expresion(n.izquierda); tb,b=self.expresion(n.derecha); op=n.operador
            if op in {"+","-","*","/"}:
                if op=="+" and ta==tb==TEXTO:
                    t=self.temp(); self.emitir("CONCAT",a,b,t,n.linea); return TEXTO,Operando.ref(t)
                if ta not in NUMERICOS or tb not in NUMERICOS: self.error(n,f"{op!r} requiere numeros; '+' tambien acepta dos textos")
                tr=DECIMAL if op=="/" or DECIMAL in {ta,tb} else ENTERO
                if tr==DECIMAL: a=self.convertir(ta,DECIMAL,a,n.linea); b=self.convertir(tb,DECIMAL,b,n.linea)
                cod={"+":"ADD","-":"SUB","*":"MUL","/":"DIV"}[op]; t=self.temp(); self.emitir(cod,a,b,t,n.linea)
                return tr,Operando.ref(t)
            if op in {"<",">","<=",">=","==","!="}:
                if ta in NUMERICOS and tb in NUMERICOS:
                    if DECIMAL in {ta,tb}: a=self.convertir(ta,DECIMAL,a,n.linea); b=self.convertir(tb,DECIMAL,b,n.linea)
                elif op in {"==","!="} and ta==tb and ta in {TEXTO,LOGICO}: pass
                else: self.error(n,f"tipos incompatibles para {op!r}: {ta} y {tb}")
                cod={"<":"LT",">":"GT","<=":"LE",">=":"GE","==":"EQ","!=":"NE"}[op]
                t=self.temp(); self.emitir(cod,a,b,t,n.linea); return LOGICO,Operando.ref(t)
            if op in {"y","o"}:
                if ta!=LOGICO or tb!=LOGICO: self.error(n,f"{op!r} requiere dos operandos logicos")
                t=self.temp(); self.emitir("AND" if op=="y" else "OR",a,b,t,n.linea); return LOGICO,Operando.ref(t)
        self.error(n,"expresion no reconocida")
        raise AssertionError("inalcanzable")

def compilar(programa): return Compilador().compilar(programa)