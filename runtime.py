"""Maquina virtual que ejecuta la representacion intermedia de TopScript."""
from dataclasses import dataclass,field
from decimal import Decimal,InvalidOperation
from cuadruplos import Operando
from errores import ErrorEjecucion
@dataclass
class CategoriaRuntime:
    nombre:str; limite:Decimal; gastado:Decimal=Decimal("0"); gastos:list[tuple[Decimal,str]]=field(default_factory=list)
class MaquinaVirtual:
    def __init__(self,codigo,nombre):
        self.codigo=codigo; self.nombre=nombre; self.memoria={}; self.categorias={}; self.iteradores={}; self.activa=None; self.salida=[]
    def leer(self,op):
        if op is None: return None
        if op.es_literal: return op.valor
        if op.direccion not in self.memoria: raise ErrorEjecucion(f"direccion sin inicializar {op.direccion}")
        return self.memoria[op.direccion]
    def ejecutar(self):
        ip=0; pasos=0
        while ip<len(self.codigo):
            pasos+=1
            if pasos>1000000: raise ErrorEjecucion("se excedio el limite de 1,000,000 pasos; posible ciclo infinito",self.codigo[ip].linea,1)
            q=self.codigo[ip]; op=q.operador; a,b=(None,None) if op=="ITER_NEXT" else (self.leer(q.arg1),self.leer(q.arg2)); siguiente=ip+1
            try:
                if op=="HALT": break
                if op=="ASSIGN": self.memoria[q.resultado]=a
                elif op=="INT_TO_DEC": self.memoria[q.resultado]=Decimal(a)
                elif op=="ADD": self.memoria[q.resultado]=a+b
                elif op=="SUB": self.memoria[q.resultado]=a-b
                elif op=="MUL": self.memoria[q.resultado]=a*b
                elif op=="DIV":
                    if b==0: raise ErrorEjecucion("division entre cero",q.linea,1)
                    self.memoria[q.resultado]=a/b
                elif op=="CONCAT": self.memoria[q.resultado]=a+b
                elif op=="NEG": self.memoria[q.resultado]=-a
                elif op=="NOT": self.memoria[q.resultado]=not a
                elif op=="LT": self.memoria[q.resultado]=a<b
                elif op=="GT": self.memoria[q.resultado]=a>b
                elif op=="LE": self.memoria[q.resultado]=a<=b
                elif op=="GE": self.memoria[q.resultado]=a>=b
                elif op=="EQ": self.memoria[q.resultado]=a==b
                elif op=="NE": self.memoria[q.resultado]=a!=b
                elif op=="AND": self.memoria[q.resultado]=bool(a and b)
                elif op=="OR": self.memoria[q.resultado]=bool(a or b)
                elif op=="CATEGORY":
                    if a in self.categorias: raise ErrorEjecucion(f"categoria duplicada {a!r}",q.linea,1)
                    if b<=0: raise ErrorEjecucion("el limite debe ser mayor que cero",q.linea,1)
                    cat=CategoriaRuntime(a,Decimal(b)); self.categorias[a]=cat; self.memoria[q.resultado]=cat
                elif op=="ENTER_CATEGORY": self.activa=a
                elif op=="EXIT_CATEGORY": self.activa=None
                elif op=="EXPENSE":
                    if self.activa is None: raise ErrorEjecucion("gasto fuera de categoria activa",q.linea,1)
                    monto=Decimal(a)
                    if monto<0: raise ErrorEjecucion("un gasto no puede ser negativo",q.linea,1)
                    self.activa.gastado+=monto; self.activa.gastos.append((monto,str(b)))
                elif op=="GET_ATTR":
                    if not isinstance(a,CategoriaRuntime): raise ErrorEjecucion("el valor no es una categoria",q.linea,1)
                    self.memoria[q.resultado]={"nombre":a.nombre,"limite":a.limite,"gastado":a.gastado}[b]
                elif op=="PRINT": self.salida.append(self.mostrar(a))
                elif op=="ALERT": self.salida.append("ALERTA: "+self.mostrar(a))
                elif op=="GOTO": siguiente=int(q.resultado)
                elif op=="GOTOF":
                    if not a: siguiente=int(q.resultado)
                elif op=="ITER_INIT": self.iteradores[q.resultado]={"indice":0}; self.memoria[q.resultado]=True
                elif op=="ITER_NEXT":
                    it=self.iteradores[q.arg1.direccion]; categorias=list(self.categorias.values())
                    if it["indice"]>=len(categorias): siguiente=int(q.resultado)
                    else: self.memoria[q.arg2.direccion]=categorias[it["indice"]]; it["indice"]+=1
                else: raise ErrorEjecucion(f"operador intermedio desconocido {op}",q.linea,1)
            except ErrorEjecucion: raise
            except (ArithmeticError,InvalidOperation,KeyError,TypeError,ValueError) as exc:
                raise ErrorEjecucion(f"no se pudo ejecutar {op}: {exc}",q.linea,1) from exc
            ip=siguiente
        self.salida.extend(self.reporte())
        return "\n".join(self.salida)
    @staticmethod
    def mostrar(v): return ("verdadero" if v else "falso") if isinstance(v,bool) else str(v)
    @staticmethod
    def dinero(v): return f"${v.quantize(Decimal('0.01')):,.2f} MXN"
    def reporte(self):
        lineas=["",f"Reporte del presupuesto: {self.nombre}"]; excedidas=[]
        for c in self.categorias.values():
            disponible=c.limite-c.gastado
            estado="EXCEDIDO" if c.gastado>c.limite else "AL LIMITE" if c.gastado==c.limite else "Dentro del limite"
            lineas.append(f"{c.nombre} | Limite: {self.dinero(c.limite)} | Gastado: {self.dinero(c.gastado)} | Disponible: {self.dinero(disponible)} | {estado}")
            if c.gastado>c.limite: excedidas.append((c.nombre,c.gastado-c.limite))
        if excedidas:
            lineas.append("Alertas de presupuesto:"); lineas.extend(f"- {n}: excedio su limite por {self.dinero(e)}." for n,e in excedidas)
        else: lineas.append("Estado: ninguna categoria excede su limite.")
        return lineas
def ejecutar(codigo,nombre): return MaquinaVirtual(codigo,nombre).ejecutar()



