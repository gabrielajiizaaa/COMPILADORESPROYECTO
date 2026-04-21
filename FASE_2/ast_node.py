"""
Definición de nodos del Árbol Sintáctico Abstracto (AST) para MiniLang — Fase 2.
Son estructuras de datos simples para representar el árbol sintáctico.
No contienen lógica de ejecución ni interpretación; solo representación estructural.
"""

from dataclasses import dataclass
from typing import Optional, List, Any


@dataclass
class NodoAST:
    # Clase base de todos los nodos del AST.
    pass


@dataclass
class Programa(NodoAST):
    # Nodo raíz que representa el programa completo.
    sentencias: List['Sentencia']


@dataclass
class Sentencia(NodoAST):
    # Clase base para todas las sentencias.
    pass


@dataclass
class Declaracion(Sentencia):
    # Declaración de variable: int x, float y, etc.
    tipo: str        # 'int', 'float', 'string', 'bool'
    identificador: str


@dataclass
class Asignacion(Sentencia):
    # Asignación de variable: x = valor, x += valor, etc.
    identificador: str
    operador: str    # '=', '+=', '-=', '*=', '/='
    valor: 'Expresion'


@dataclass
class DefinicionFuncion(Sentencia):
    # Definición de función: func nombre(tipo param1, ...): BLOQUE
    nombre: str
    parametros: List[tuple]  # lista de (tipo, nombre)
    cuerpo: 'Bloque'


@dataclass
class SentenciaIf(Sentencia):
    # Sentencia if/else con sus bloques de cuerpo.
    condicion: 'Expresion'
    bloque_entonces: 'Bloque'
    bloque_sino: Optional['Bloque'] = None


@dataclass
class SentenciaMientras(Sentencia):
    # Bucle while.
    condicion: 'Expresion'
    cuerpo: 'Bloque'


@dataclass
class SentenciaRetornar(Sentencia):
    # Sentencia return.
    valor: Optional['Expresion']


@dataclass
class SentenciaLeer(Sentencia):
    # Sentencia de entrada: read(variable)
    identificador: str


@dataclass
class SentenciaEscribir(Sentencia):
    # Sentencia de salida: write(expresion)
    expresion: 'Expresion'


@dataclass
class SentenciaExpresion(Sentencia):
    # Expresión usada como sentencia (principalmente llamadas a función).
    expresion: 'Expresion'


@dataclass
class Bloque(NodoAST):
    # Bloque de sentencias delimitado por indentación.
    sentencias: List[Sentencia]


@dataclass
class Expresion(NodoAST):
    # Clase base para todas las expresiones.
    pass


@dataclass
class OperacionBinaria(Expresion):
    # Operación binaria: a + b, a * b, a == b, etc.
    izquierda: Expresion
    operador: str
    derecha: Expresion


@dataclass
class OperacionUnaria(Expresion):
    # Operación unaria: -x, not x
    operador: str
    operando: Expresion


@dataclass
class LlamadaFuncion(Expresion):
    # Llamada a función: nombre(arg1, arg2, ...)
    nombre: str
    argumentos: List[Expresion]


@dataclass
class Identificador(Expresion):
    # Identificador de variable o función.
    nombre: str


@dataclass
class LiteralEntero(Expresion):
    # Literal entero.
    valor: int


@dataclass
class LiteralFlotante(Expresion):
    # Literal flotante.
    valor: float


@dataclass
class LiteralCadena(Expresion):
    # Literal de cadena de texto.
    valor: str


@dataclass
class LiteralBooleano(Expresion):
    # Literal booleano (true / false).
    valor: bool


@dataclass
class ExpresionParentizada(Expresion):
    # Expresión encerrada entre paréntesis.
    expresion: Expresion


def bloque_vacio():
    # Crea y retorna un bloque sin sentencias.
    return Bloque([])
