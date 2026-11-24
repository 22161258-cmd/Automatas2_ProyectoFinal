"""Lexer manual: reconoce tokens y conserva linea y columna."""
from dataclasses import dataclass
from decimal import Decimal
from errores import ErrorLexico

@dataclass(frozen=True)
class Token:
    tipo:str; valor:object; linea:int; columna:int
    def __str__(self): return f"{self.tipo}({self.valor!r})@{self.linea}:{self.columna}"

RESERVADAS={"presupuesto":"PRESUPUESTO","categoria":"CATEGORIA","limite":"LIMITE","gasto":"GASTO","descripcion":"DESCRIPCION","si":"SI","sino":"SINO","mientras":"MIENTRAS","para":"PARA","cada":"CADA","en":"EN","entero":"TIPO_ENTERO","decimal":"TIPO_DECIMAL","texto":"TIPO_TEXTO","logico":"TIPO_LOGICO","verdadero":"VERDADERO","falso":"FALSO","y":"Y","o":"O","no":"NO","alerta":"ALERTA","mostrar":"MOSTRAR"}

class Lexer:
    def __init__(self, fuente): self.fuente=fuente; self.i=0; self.linea=1; self.columna=1
    def actual(self): return self.fuente[self.i] if self.i<len(self.fuente) else ""
    def mirar(self,n=1): return self.fuente[self.i+n] if self.i+n<len(self.fuente) else ""
    def avanzar(self):
        c=self.actual()
        if c:
            self.i+=1
            if c=="\n": self.linea+=1; self.columna=1
            else: self.columna+=1
        return c
    def cadena(self):
        ln,col=self.linea,self.columna; self.avanzar(); partes=[]; escapes={"n":"\n","t":"\t",'"':'"',"\\":"\\"}
        while self.actual() and self.actual()!='"':
            c=self.actual()
            if c=="\n": raise ErrorLexico("una cadena no puede contener salto de linea literal",ln,col)
            if c=="\\":
                self.avanzar(); e=self.actual()
                if e not in escapes: raise ErrorLexico(f"secuencia de escape no valida: \\{e}",self.linea,self.columna)
                partes.append(escapes[e]); self.avanzar()
            else: partes.append(self.avanzar())
        if not self.actual(): raise ErrorLexico("falta la comilla doble de cierre",ln,col)
        self.avanzar(); return Token("CADENA","".join(partes),ln,col)
    def numero(self):
        ln,col,ini=self.linea,self.columna,self.i
        while "0"<=self.actual()<="9": self.avanzar()
        tipo="ENTERO_LITERAL"
        if self.actual()==".":
            self.avanzar(); start=self.i
            while "0"<=self.actual()<="9": self.avanzar()
            n=self.i-start
            if n==0: raise ErrorLexico("se requiere un digito despues del punto decimal",ln,col)
            if n>2: raise ErrorLexico("se permiten hasta dos cifras decimales",ln,col)
            tipo="DECIMAL_LITERAL"
        s=self.fuente[ini:self.i]; v=Decimal(s) if tipo=="DECIMAL_LITERAL" else int(s)
        return Token(tipo,v,ln,col)
    def analizar(self):
        ts=[]; simple={"{":"LLAVE_IZQ","}":"LLAVE_DER","(":"PAREN_IZQ",")":"PAREN_DER",";":"PUNTO_COMA",".":"PUNTO","+":"MAS","-":"MENOS","*":"POR","/":"DIVIDIDO"}; dobles={"<=":"MENOR_IGUAL",">=":"MAYOR_IGUAL","==":"IGUAL_IGUAL","!=":"DISTINTO"}
        while self.actual():
            c=self.actual()
            if c.isspace(): self.avanzar(); continue
            if c=="/" and self.mirar()=="/":
                while self.actual() and self.actual()!="\n": self.avanzar()
                continue
            if c=='"': ts.append(self.cadena()); continue
            if "0"<=c<="9": ts.append(self.numero()); continue
            if c.isalpha() or c=="_":
                ln,col,ini=self.linea,self.columna,self.i
                while self.actual() and (self.actual().isalnum() or self.actual()=="_"): self.avanzar()
                s=self.fuente[ini:self.i]; ts.append(Token(RESERVADAS.get(s,"IDENTIFICADOR"),s,ln,col)); continue
            ln,col=self.linea,self.columna; par=c+self.mirar()
            if par in dobles: self.avanzar(); self.avanzar(); ts.append(Token(dobles[par],par,ln,col)); continue
            if c in "<> =".replace(" ",""):
                self.avanzar(); ts.append(Token({"<":"MENOR",">":"MAYOR","=":"ASIGNAR"}[c],c,ln,col)); continue
            if c in simple: self.avanzar(); ts.append(Token(simple[c],c,ln,col)); continue
            raise ErrorLexico(f"caracter no reconocido: {c!r}",ln,col)
        ts.append(Token("EOF",None,self.linea,self.columna)); return ts

def tokenizar(fuente): return Lexer(fuente).analizar()