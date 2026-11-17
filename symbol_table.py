"""Tabla de simbolos jerarquica para variables y categorias."""
from dataclasses import dataclass
@dataclass
class Simbolo:
    nombre:str; clase:str; tipo:str; direccion:str; ambito:int; linea:int
class TablaSimbolos:
    def __init__(self): self.ambitos=[{}]; self.registros=[]; self.contador=0; self.ambito_id=0
    @property
    def ambito_actual(self): return self.ambito_id
    def abrir(self): self.ambito_id+=1; self.ambitos.append({})
    def cerrar(self):
        if len(self.ambitos)>1: self.ambitos.pop()
    def declarar(self,nombre,tipo,linea,clase="variable"):
        if nombre in self.ambitos[-1]: return None
        direccion=f"v{self.contador}_{nombre}"; self.contador+=1
        s=Simbolo(nombre,clase,tipo,direccion,self.ambito_id,linea); self.ambitos[-1][nombre]=s; self.registros.append(s); return s
    def buscar(self,nombre):
        for ambito in reversed(self.ambitos):
            if nombre in ambito: return ambito[nombre]
        return None
    def filas(self): return [(s.nombre,s.clase,s.tipo,s.direccion,s.ambito,s.linea) for s in self.registros]
