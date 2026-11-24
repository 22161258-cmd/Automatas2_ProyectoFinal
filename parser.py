"""Parser de descenso recursivo para TopScript v1."""
from ast_nodes import (Accion,Asignacion,Binaria,Bloque,Categoria,Condicional,Declaracion,Gasto,Literal,Mientras,ParaCada,Programa,Unaria,Variable)
from errores import ErrorSintactico

TIPOS={"TIPO_ENTERO":"entero","TIPO_DECIMAL":"decimal","TIPO_TEXTO":"texto","TIPO_LOGICO":"logico"}
REL={"MENOR":"<","MAYOR":">","MENOR_IGUAL":"<=","MAYOR_IGUAL":">=","IGUAL_IGUAL":"==","DISTINTO":"!="}

class Parser:
    def __init__(self,tokens): self.tokens=tokens; self.i=0
    def actual(self): return self.tokens[self.i]
    def avanzar(self):
        t=self.actual()
        if t.tipo!="EOF": self.i+=1
        return t
    def aceptar(self,tipo): return self.avanzar() if self.actual().tipo==tipo else None
    def esperar(self,tipo,esperado):
        t=self.actual()
        if t.tipo!=tipo:
            recibido="fin de archivo" if t.tipo=="EOF" else repr(t.valor)
            raise ErrorSintactico(f"se esperaba {esperado}; se encontro {recibido}",t.linea,t.columna)
        return self.avanzar()
    def analizar(self):
        inicio=self.esperar("PRESUPUESTO","'presupuesto'"); nombre=self.esperar("CADENA","nombre del presupuesto entre comillas")
        cuerpo=self.bloque(); self.esperar("EOF","fin del archivo")
        return Programa(inicio.linea,inicio.columna,nombre.valor,cuerpo.instrucciones)
    def bloque(self):
        apertura=self.esperar("LLAVE_IZQ","'{' "); instrucciones=[]
        while self.actual().tipo not in {"LLAVE_DER","EOF"}: instrucciones.append(self.instruccion())
        self.esperar("LLAVE_DER","'}'"); return Bloque(apertura.linea,apertura.columna,instrucciones)
    def instruccion(self):
        t=self.actual()
        if t.tipo in TIPOS: return self.declaracion()
        if t.tipo=="CATEGORIA": return self.categoria()
        if t.tipo=="GASTO": return self.gasto()
        if t.tipo=="SI": return self.condicional()
        if t.tipo=="MIENTRAS": return self.mientras()
        if t.tipo=="PARA": return self.para_cada()
        if t.tipo in {"MOSTRAR","ALERTA"}: return self.accion()
        if t.tipo=="IDENTIFICADOR": return self.asignacion()
        if t.tipo=="LLAVE_IZQ": return self.bloque()
        raise ErrorSintactico("se esperaba una instruccion",t.linea,t.columna)
    def declaracion(self):
        t=self.avanzar(); nombre=self.esperar("IDENTIFICADOR","nombre de variable")
        self.esperar("ASIGNAR","'='; toda variable requiere inicializacion"); expr=self.expresion(); self.esperar("PUNTO_COMA","';'")
        return Declaracion(t.linea,t.columna,TIPOS[t.tipo],nombre.valor,expr)
    def asignacion(self):
        n=self.avanzar(); self.esperar("ASIGNAR","'=' despues del identificador"); e=self.expresion(); self.esperar("PUNTO_COMA","';'")
        return Asignacion(n.linea,n.columna,n.valor,e)
    def categoria(self):
        t=self.avanzar(); n=self.esperar("IDENTIFICADOR","nombre de categoria"); self.esperar("LIMITE","'limite'"); lim=self.expresion()
        return Categoria(t.linea,t.columna,n.valor,lim,self.bloque())
    def gasto(self):
        t=self.avanzar(); monto=self.expresion(); self.esperar("DESCRIPCION","'descripcion'"); desc=self.expresion(); self.esperar("PUNTO_COMA","';'")
        return Gasto(t.linea,t.columna,monto,desc)
    def condicional(self):
        t=self.avanzar(); self.esperar("PAREN_IZQ","'('"); cond=self.expresion(); self.esperar("PAREN_DER","')'"); si=self.bloque(); sino=self.bloque() if self.aceptar("SINO") else None
        return Condicional(t.linea,t.columna,cond,si,sino)
    def mientras(self):
        t=self.avanzar(); self.esperar("PAREN_IZQ","'('"); cond=self.expresion(); self.esperar("PAREN_DER","')'")
        return Mientras(t.linea,t.columna,cond,self.bloque())
    def para_cada(self):
        t=self.avanzar(); self.esperar("PAREN_IZQ","'('"); self.esperar("CADA","'cada'"); n=self.esperar("IDENTIFICADOR","alias de categoria")
        self.esperar("EN","'en'"); self.esperar("PRESUPUESTO","'presupuesto'"); self.esperar("PAREN_DER","')'")
        return ParaCada(t.linea,t.columna,n.valor,self.bloque())
    def accion(self):
        t=self.avanzar(); self.esperar("PAREN_IZQ","'('"); e=self.expresion(); self.esperar("PAREN_DER","')'"); self.esperar("PUNTO_COMA","';'")
        return Accion(t.linea,t.columna,"mostrar" if t.tipo=="MOSTRAR" else "alerta",e)
    def expresion(self): return self.expresion_o()
    def expresion_o(self):
        n=self.expresion_y()
        while self.aceptar("O"):
            d=self.expresion_y(); n=Binaria(n.linea,n.columna,n,"o",d)
        return n
    def expresion_y(self):
        n=self.expresion_no()
        while self.aceptar("Y"):
            d=self.expresion_no(); n=Binaria(n.linea,n.columna,n,"y",d)
        return n
    def expresion_no(self):
        if self.actual().tipo=="NO":
            t=self.avanzar(); return Unaria(t.linea,t.columna,"no",self.expresion_no())
        return self.relacional()
    def relacional(self):
        n=self.aditiva()
        if self.actual().tipo in REL:
            t=self.avanzar(); n=Binaria(n.linea,n.columna,n,REL[t.tipo],self.aditiva())
            if self.actual().tipo in REL:
                t=self.actual(); raise ErrorSintactico("no se encadenan comparaciones; combine condiciones con 'y'",t.linea,t.columna)
        return n
    def aditiva(self):
        n=self.multiplicativa()
        while self.actual().tipo in {"MAS","MENOS"}:
            t=self.avanzar(); n=Binaria(n.linea,n.columna,n,t.valor,self.multiplicativa())
        return n
    def multiplicativa(self):
        n=self.unaria()
        while self.actual().tipo in {"POR","DIVIDIDO"}:
            t=self.avanzar(); n=Binaria(n.linea,n.columna,n,t.valor,self.unaria())
        return n
    def unaria(self):
        if self.actual().tipo=="MENOS":
            t=self.avanzar(); return Unaria(t.linea,t.columna,"-",self.unaria())
        return self.primaria()
    def primaria(self):
        t=self.actual(); tipos={"ENTERO_LITERAL":"entero","DECIMAL_LITERAL":"decimal","CADENA":"texto","VERDADERO":"logico","FALSO":"logico"}
        if t.tipo in tipos:
            self.avanzar(); v=True if t.tipo=="VERDADERO" else False if t.tipo=="FALSO" else t.valor
            return Literal(t.linea,t.columna,v,tipos[t.tipo])
        if t.tipo=="IDENTIFICADOR":
            self.avanzar(); attr=None
            if self.aceptar("PUNTO"):
                atributo=self.actual()
                if atributo.tipo not in {"IDENTIFICADOR","LIMITE"}:
                    raise ErrorSintactico("se esperaba atributo de categoria",atributo.linea,atributo.columna)
                attr=self.avanzar().valor
            return Variable(t.linea,t.columna,t.valor,attr)
        if self.aceptar("PAREN_IZQ"):
            n=self.expresion(); self.esperar("PAREN_DER","')'"); return n
        raise ErrorSintactico("se esperaba literal, variable o expresion entre parentesis",t.linea,t.columna)

def parsear(tokens): return Parser(tokens).analizar()