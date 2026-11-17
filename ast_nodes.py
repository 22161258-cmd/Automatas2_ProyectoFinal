"""Nodos del arbol de sintaxis abstracta de TopScript."""
from dataclasses import dataclass, field
@dataclass
class Nodo: linea:int; columna:int
@dataclass
class Programa(Nodo): nombre:str; instrucciones:list[object]=field(default_factory=list)
@dataclass
class Bloque(Nodo): instrucciones:list[object]=field(default_factory=list)
@dataclass
class Declaracion(Nodo): tipo:str; nombre:str; expresion:object
@dataclass
class Asignacion(Nodo): nombre:str; expresion:object
@dataclass
class Categoria(Nodo): nombre:str; limite:object; cuerpo:Bloque
@dataclass
class Gasto(Nodo): monto:object; descripcion:object
@dataclass
class Condicional(Nodo): condicion:object; entonces:Bloque; sino:Bloque|None
@dataclass
class Mientras(Nodo): condicion:object; cuerpo:Bloque
@dataclass
class ParaCada(Nodo): nombre:str; cuerpo:Bloque
@dataclass
class Accion(Nodo): tipo:str; expresion:object
@dataclass
class Literal(Nodo): valor:object; tipo:str
@dataclass
class Variable(Nodo): nombre:str; atributo:str|None=None
@dataclass
class Unaria(Nodo): operador:str; operando:object
@dataclass
class Binaria(Nodo): izquierda:object; operador:str; derecha:object
