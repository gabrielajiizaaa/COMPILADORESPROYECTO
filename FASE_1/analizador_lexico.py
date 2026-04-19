import re
from enum import Enum, auto
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# TIPOS DE TOKENS
class TipoToken(Enum):
    # Literales
    NENTERO  = auto()   # Número entero:   [0-9]+
    NFLOAT   = auto()   # Número flotante: [0-9]+\.[0-9]+
    CADENA   = auto()   # Cadena de texto: "..." o '...'

    # Identificadores
    ID       = auto()   # [A-Za-z_][A-Za-z0-9_]{0,30}

    # Palabras reservadas — control de flujo
    SI       = auto()   # if
    SINO     = auto()   # else
    MIENTRAS = auto()   # while
    FUNCION  = auto()   # func

    # Tipos primitivos
    TIPO_ENTERO  = auto()   # int
    TIPO_FLOAT   = auto()   # float
    TIPO_BOOL    = auto()   # bool
    TIPO_CADENA  = auto()   # string

    # Booleanos
    VERDADERO = auto()   # true
    FALSO     = auto()   # false

    # Entrada / Salida
    LEER      = auto()   # read
    ESCRIBIR  = auto()   # write

    # Retorno
    RETORNAR  = auto()   # return

    # Operadores aritméticos
    MAS        = auto()   # +
    MENOS      = auto()   # -
    MULT       = auto()   # *
    DIV        = auto()   # /
    MODULO     = auto()   # %
    POTENCIA   = auto()   # **
    DIV_ENTERA = auto()   # //

    # Operadores de comparación
    IGUAL         = auto()   # ==
    DIFERENTE     = auto()   # !=
    MENOR_QUE     = auto()   # <
    MAYOR_QUE     = auto()   # >
    MENOR_IGUAL   = auto()   # <=
    MAYOR_IGUAL   = auto()   # >=

    # Operadores de asignación
    ASIGNAR      = auto()   # =
    MAS_IGUAL    = auto()   # +=
    MENOS_IGUAL  = auto()   # -=
    MULT_IGUAL   = auto()   # *=
    DIV_IGUAL    = auto()   # /=

    # Delimitadores / puntuación
    PAR_IZQ    = auto()   # (
    PAR_DER    = auto()   # )
    LLAVE_IZQ  = auto()   # {
    LLAVE_DER  = auto()   # }
    CORCH_IZQ  = auto()   # [
    CORCH_DER  = auto()   # ]
    COMA       = auto()   # ,
    PUNTO_COMA = auto()   # ;
    DOS_PUNTOS = auto()   # :
    PUNTO      = auto()   # .

    # Especiales
    COMENTARIO  = auto()   # # comentario
    NUEVA_LINEA = auto()   # \n  (significativo)
    INDENTAR    = auto()   # aumento de indentación
    DESINDENTAR = auto()   # disminución de indentación
    FIN         = auto()   # fin de archivo
    DESCONOCIDO = auto()   # carácter no reconocido (error)

# DATACLASS TOKEN
@dataclass
class Token:
    tipo:       TipoToken
    valor:      object      # lexema / valor
    linea:      int
    col_inicio: int
    col_fin:    int         # columna final inclusiva

    def __repr__(self):
        return (f"Token({self.tipo.name}, {repr(self.valor)}, "
                f"L{self.linea}:C{self.col_inicio}-{self.col_fin})")

    def a_linea_salida(self) -> str:
        """Genera la línea de salida con formato para el archivo .out"""
        val = "" if self.valor is None else f" {self.valor}"
        return (f"({self.linea},{self.col_inicio}-{self.col_fin}) "
                f"{self.tipo.name}{val}")

# ANALIZADOR LÉXICO
class AnalizadorLexico:
    """Analizador léxico completo para el lenguaje MiniLang."""

    # Expresiones regulares 
    RE_ID       = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    RE_NFLOAT   = re.compile(r"[0-9]+\.[0-9]+")
    RE_NENTERO  = re.compile(r"[0-9]+")
    RE_ESPACIOS = re.compile(r"[ \t]+")
    RE_COMENTARIO = re.compile(r"#[^\n]*")
    RE_CADENA   = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')

    MAX_LONGITUD_ID     = 31   # longitud máxima de identificador
    MAX_NIVELES_INDENT  = 5    # máximo de niveles de indentación

    #Palabras reservadas
    PALABRAS_RESERVADAS: dict = {
        'if':     TipoToken.SI,
        'else':   TipoToken.SINO,
        'while':  TipoToken.MIENTRAS,
        'func':   TipoToken.FUNCION,
        'int':    TipoToken.TIPO_ENTERO,
        'float':  TipoToken.TIPO_FLOAT,
        'bool':   TipoToken.TIPO_BOOL,
        'string': TipoToken.TIPO_CADENA,
        'true':   TipoToken.VERDADERO,
        'false':  TipoToken.FALSO,
        'read':   TipoToken.LEER,
        'write':  TipoToken.ESCRIBIR,
        'return': TipoToken.RETORNAR,
    }

    def __init__(self, codigo_fuente: str):
        self.fuente   = codigo_fuente
        self.pos      = 0
        self.linea    = 1
        self.col      = 1
        self.errores: List[str] = []

        # Pila de indentación (nivel 0 base)
        self.pila_indent:      List[int]   = [0]
        self.tokens_pendientes: List[Token] = []
        self.inicio_de_linea   = True

    #Utilidades internas 

    @property
    def _car(self) -> Optional[str]:
        return self.fuente[self.pos] if self.pos < len(self.fuente) else None

    def _ver(self, desplazamiento: int = 0) -> Optional[str]:
        idx = self.pos + desplazamiento
        return self.fuente[idx] if idx < len(self.fuente) else None

    def _resto(self) -> str:
        return self.fuente[self.pos:]

    def _avanzar(self, n: int = 1):
        for _ in range(n):
            if self.pos >= len(self.fuente):
                return
            if self.fuente[self.pos] == '\n':
                self.linea += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _registrar_error(self, mensaje: str):
        self.errores.append(f"linea {self.linea}, col {self.col}: ERROR {mensaje}")

    # Procesamiento de indentación

    def _procesar_indentacion(self) -> Optional[Token]:
        if not self.inicio_de_linea:
            return None

        linea_guardada = self.linea
        nivel = 0
        consumido = 0

        # Contar espacios/tabulaciones
        while True:
            car = self._ver(consumido)
            if car == ' ':
                nivel += 1
                consumido += 1
            elif car == '\t':
                nivel += 4
                consumido += 1
            else:
                break

        siguiente = self._ver(consumido)

        # Línea vacía o solo comentario → no altera la pila
        if siguiente in (None, '\n', '#'):
            if consumido:
                self._avanzar(consumido)
            return None

        if consumido:
            self._avanzar(consumido)

        self.inicio_de_linea = False
        nivel_actual = self.pila_indent[-1]

        if nivel > nivel_actual:
            if len(self.pila_indent) >= self.MAX_NIVELES_INDENT + 1:
                self._registrar_error("máximo de niveles de indentación alcanzado")
                return None
            self.pila_indent.append(nivel)
            self.tokens_pendientes.append(
                Token(TipoToken.INDENTAR, nivel, linea_guardada, 1, 1))

        elif nivel < nivel_actual:
            while len(self.pila_indent) > 1 and nivel < self.pila_indent[-1]:
                self.pila_indent.pop()
                self.tokens_pendientes.append(
                    Token(TipoToken.DESINDENTAR, self.pila_indent[-1], linea_guardada, 1, 1))
            if nivel != self.pila_indent[-1]:
                self._registrar_error("indentación inválida — no coincide con ningún nivel anterior")
                while len(self.pila_indent) > 1 and nivel < self.pila_indent[-1]:
                    self.pila_indent.pop()
                    self.tokens_pendientes.append(
                        Token(TipoToken.DESINDENTAR, self.pila_indent[-1], linea_guardada, 1, 1))

        if self.tokens_pendientes:
            return self.tokens_pendientes.pop(0)
        return None

    #Lectores específicos

    def _leer_numero(self) -> Token:
        l, c = self.linea, self.col

        # Intentar flotante primero (mayor especificidad)
        m = self.RE_NFLOAT.match(self._resto())
        if m:
            self._avanzar(len(m.group()))
            return Token(TipoToken.NFLOAT, float(m.group()), l, c, c + len(m.group()) - 1)

        m = self.RE_NENTERO.match(self._resto())
        if m:
            self._avanzar(len(m.group()))
            return Token(TipoToken.NENTERO, int(m.group()), l, c, c + len(m.group()) - 1)

        self._registrar_error("número mal formado")
        self._avanzar(1)
        return Token(TipoToken.DESCONOCIDO, self.fuente[self.pos - 1], l, c, c)

    def _desescapar(self, texto: str) -> str:
        interior = texto[1:-1]
        escapes = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
        resultado, i = '', 0
        while i < len(interior):
            if interior[i] == '\\' and i + 1 < len(interior):
                i += 1
                resultado += escapes.get(interior[i], interior[i])
            else:
                resultado += interior[i]
            i += 1
        return resultado

    def _leer_cadena(self) -> Token:
        l, c = self.linea, self.col
        m = self.RE_CADENA.match(self._resto())
        if m:
            cruda = m.group()
            self._avanzar(len(cruda))
            return Token(TipoToken.CADENA, self._desescapar(cruda), l, c, c + len(cruda) - 1)

        # Cadena sin cerrar → recuperar hasta fin de línea
        self._registrar_error("cadena sin cerrar antes de NUEVA_LINEA/FIN")
        fin = self._resto().find('\n')
        consumido = fin if fin != -1 else len(self._resto())
        cruda = self._resto()[:consumido]
        self._avanzar(consumido)
        return Token(TipoToken.DESCONOCIDO, cruda, l, c, c + consumido - 1)

    def _leer_id_o_reservada(self) -> Token:
        l, c = self.linea, self.col
        m = self.RE_ID.match(self._resto())
        lexema = m.group()

        if len(lexema) > self.MAX_LONGITUD_ID:
            self._registrar_error(
                f"identificador demasiado largo ({len(lexema)} caracteres); "
                f"truncado a {self.MAX_LONGITUD_ID}")
            lexema = lexema[:self.MAX_LONGITUD_ID]

        self._avanzar(len(m.group()))  # avanzar el texto original aunque se haya truncado
        tipo = self.PALABRAS_RESERVADAS.get(lexema, TipoToken.ID)
        return Token(tipo, lexema, l, c, c + len(m.group()) - 1)

    def _leer_comentario(self) -> Token:
        """Lee y retorna un token de comentario de línea."""
        l, c = self.linea, self.col
        m = self.RE_COMENTARIO.match(self._resto())
        texto = m.group() if m else '#'
        self._avanzar(len(texto))
        return Token(TipoToken.COMENTARIO, texto, l, c, c + len(texto) - 1)

    #Obtener siguiente token

    def siguiente_token(self) -> Token:
        if self.tokens_pendientes:
            return self.tokens_pendientes.pop(0)

        while self._car is not None:

            # Indentación al inicio de línea
            if self.inicio_de_linea:
                tok = self._procesar_indentacion()
                if tok:
                    return tok

            # Ignorar espacios y tabulaciones
            m = self.RE_ESPACIOS.match(self._resto())
            if m:
                self._avanzar(len(m.group()))
                continue

            # Salto de línea → NUEVA_LINEA (significativo en MiniLang)
            if self._car == '\n':
                l, c = self.linea, self.col
                self._avanzar(1)
                self.inicio_de_linea = True
                return Token(TipoToken.NUEVA_LINEA, '\\n', l, c, c)

            self.inicio_de_linea = False

            # Comentario
            if self._car == '#':
                return self._leer_comentario()

            # Cadena de texto
            if self._car in ('"', "'"):
                return self._leer_cadena()

            # Número
            if self._car.isdigit():
                return self._leer_numero()

            # Identificador o palabra reservada
            if self._car.isalpha() or self._car == '_':
                return self._leer_id_o_reservada()

            l, c = self.linea, self.col

            # Operadores de dos caracteres (mayor especificidad primero)
            dos = self._resto()[:2]
            OPS_DOS = {
                '==': TipoToken.IGUAL,
                '!=': TipoToken.DIFERENTE,
                '>=': TipoToken.MAYOR_IGUAL,
                '<=': TipoToken.MENOR_IGUAL,
                '+=': TipoToken.MAS_IGUAL,
                '-=': TipoToken.MENOS_IGUAL,
                '*=': TipoToken.MULT_IGUAL,
                '/=': TipoToken.DIV_IGUAL,
                '**': TipoToken.POTENCIA,
                '//': TipoToken.DIV_ENTERA,
            }
            if dos in OPS_DOS:
                self._avanzar(2)
                return Token(OPS_DOS[dos], dos, l, c, c + 1)

            # Operadores / delimitadores de un carácter
            OPS_UNO = {
                '+': TipoToken.MAS,
                '-': TipoToken.MENOS,
                '*': TipoToken.MULT,
                '/': TipoToken.DIV,
                '%': TipoToken.MODULO,
                '=': TipoToken.ASIGNAR,
                '>': TipoToken.MAYOR_QUE,
                '<': TipoToken.MENOR_QUE,
                '(': TipoToken.PAR_IZQ,
                ')': TipoToken.PAR_DER,
                '{': TipoToken.LLAVE_IZQ,
                '}': TipoToken.LLAVE_DER,
                '[': TipoToken.CORCH_IZQ,
                ']': TipoToken.CORCH_DER,
                ',': TipoToken.COMA,
                ';': TipoToken.PUNTO_COMA,
                ':': TipoToken.DOS_PUNTOS,
                '.': TipoToken.PUNTO,
            }
            if self._car in OPS_UNO:
                car = self._car
                self._avanzar(1)
                return Token(OPS_UNO[car], car, l, c, c)

            # Carácter desconocido → error y recuperación
            desconocido = self._car
            self._registrar_error(f"carácter inesperado '{desconocido}'")
            self._avanzar(1)
            return Token(TipoToken.DESCONOCIDO, desconocido, l, c, c)

        # Fin de archivo
        while len(self.pila_indent) > 1:
            self.pila_indent.pop()
            return Token(TipoToken.DESINDENTAR, self.pila_indent[-1], self.linea, self.col, self.col)

        return Token(TipoToken.FIN, None, self.linea, self.col, self.col)

    # Tokenizar todo el código 

    def tokenizar(self,
                  incluir_comentarios: bool = False,
                  incluir_nuevas_lineas: bool = True) -> List[Token]:

        tokens: List[Token] = []
        while True:
            tok = self.siguiente_token()
            if tok.tipo == TipoToken.COMENTARIO and not incluir_comentarios:
                continue
            if tok.tipo == TipoToken.NUEVA_LINEA and not incluir_nuevas_lineas:
                continue
            tokens.append(tok)
            if tok.tipo == TipoToken.FIN:
                break
        return tokens


# Alias para usar en el minilang.py
Lexer = AnalizadorLexico
TokenType = TipoToken