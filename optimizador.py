"""Optimizacion local: plegado de constantes e identidades algebraicas."""
from decimal import InvalidOperation
from cuadruplos import Cuadruplo,Operando
OPS={"ADD","SUB","MUL","DIV","CONCAT","LT","GT","LE","GE","EQ","NE","AND","OR"}
def calcular(op,a,b):
    return {"ADD":lambda:a+b,"SUB":lambda:a-b,"MUL":lambda:a*b,"DIV":lambda:a/b,"CONCAT":lambda:a+b,"LT":lambda:a<b,"GT":lambda:a>b,"LE":lambda:a<=b,"GE":lambda:a>=b,"EQ":lambda:a==b,"NE":lambda:a!=b,"AND":lambda:bool(a and b),"OR":lambda:bool(a or b)}[op]()
def optimizar(codigo):
    salida=[]
    for q in codigo:
        if q.operador in OPS and q.arg1 and q.arg2 and q.arg1.es_literal and q.arg2.es_literal:
            try: valor=calcular(q.operador,q.arg1.valor,q.arg2.valor)
            except (ArithmeticError,InvalidOperation,TypeError): salida.append(q); continue
            salida.append(Cuadruplo("ASSIGN",Operando.literal(valor),None,q.resultado,q.linea)); continue
        b=q.arg2.valor if q.arg2 and q.arg2.es_literal else None
        identidad=(q.operador=="ADD" and b==0) or (q.operador=="SUB" and b==0) or (q.operador=="MUL" and b==1) or (q.operador=="DIV" and b==1)
        if identidad: salida.append(Cuadruplo("ASSIGN",q.arg1,None,q.resultado,q.linea))
        elif q.operador=="MUL" and b==0: salida.append(Cuadruplo("ASSIGN",q.arg2,None,q.resultado,q.linea))
        else: salida.append(q)
    return salida
