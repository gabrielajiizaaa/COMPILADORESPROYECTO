"""
FASE 2: Analizador Sintáctico Ascendente para MiniLang
Implementado con PLY (Python Lex-Yacc) — parser LALR(1).
Se integra con el analizador léxico de la Fase 1.
"""

import os
import sys
from typing import List, Tuple

import ply.yacc as yacc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'FASE_1'))
from analizador_lexico import TipoToken, Token

# ADAPTADOR: convierte los Token de Fase 1 al formato que PLY espera


# Mapa de TipoToken (enum de Fase 1) → nombre de terminal PLY (cadena)
_MAPA: dict = {
    TipoToken.NENTERO:      'NENTERO',
    TipoToken.NFLOAT:       'NFLOAT',
    TipoToken.CADENA:       'CADENA',
    TipoToken.ID:           'ID',
    TipoToken.SI:           'SI',
    TipoToken.SINO:         'SINO',
    TipoToken.MIENTRAS:     'MIENTRAS',
    TipoToken.FUNCION:      'FUNCION',
    TipoToken.TIPO_ENTERO:  'TIPO_ENTERO',
    TipoToken.TIPO_FLOAT:   'TIPO_FLOAT',
    TipoToken.TIPO_BOOL:    'TIPO_BOOL',
    TipoToken.TIPO_CADENA:  'TIPO_CADENA',
    TipoToken.VERDADERO:    'VERDADERO',
    TipoToken.FALSO:        'FALSO',
    TipoToken.LEER:         'LEER',
    TipoToken.ESCRIBIR:     'ESCRIBIR',
    TipoToken.RETORNAR:     'RETORNAR',
    TipoToken.MAS:          'MAS',
    TipoToken.MENOS:        'MENOS',
    TipoToken.MULT:         'MULT',
    TipoToken.DIV:          'DIV',
    TipoToken.MODULO:       'MODULO',
    TipoToken.POTENCIA:     'POTENCIA',
    TipoToken.DIV_ENTERA:   'DIV_ENTERA',
    TipoToken.IGUAL:        'IGUAL',
    TipoToken.DIFERENTE:    'DIFERENTE',
    TipoToken.MENOR_QUE:    'MENOR_QUE',
    TipoToken.MAYOR_QUE:    'MAYOR_QUE',
    TipoToken.MENOR_IGUAL:  'MENOR_IGUAL',
    TipoToken.MAYOR_IGUAL:  'MAYOR_IGUAL',
    TipoToken.ASIGNAR:      'ASIGNAR',
    TipoToken.MAS_IGUAL:    'MAS_IGUAL',
    TipoToken.MENOS_IGUAL:  'MENOS_IGUAL',
    TipoToken.MULT_IGUAL:   'MULT_IGUAL',
    TipoToken.DIV_IGUAL:    'DIV_IGUAL',
    TipoToken.PAR_IZQ:      'PAR_IZQ',
    TipoToken.PAR_DER:      'PAR_DER',
    TipoToken.COMA:         'COMA',
    TipoToken.DOS_PUNTOS:   'DOS_PUNTOS',
    TipoToken.NUEVA_LINEA:  'NUEVA_LINEA',
    TipoToken.INDENTAR:     'INDENTAR',
    TipoToken.DESINDENTAR:  'DESINDENTAR',
}

# El lexer de Fase 1 no reserva 'or', 'and', 'not'; los trata como ID.
# Los convertimos aquí para que PLY los reconozca como operadores lógicos.
_LOGICOS: dict = {'or': 'OR', 'and': 'AND', 'not': 'NOT'}


class _TokenPLY:
    """Objeto token mínimo compatible con PLY yacc."""
    # Sin __slots__: PLY necesita agregar atributos internos como 'lexer' en recovery

    def __init__(self, tipo: str, valor, linea: int, col: int):
        self.type   = tipo
        self.value  = valor
        self.lineno = linea
        self.lexpos = 0   # PLY lo requiere; usamos col para los mensajes
        self.col    = col


class AdaptadorLexer:
    """
    Envuelve la lista de tokens de Fase 1 y los expone con la interfaz
    que PLY yacc espera: método token() que devuelve None al terminar.
    """

    def __init__(self, tokens_lista: List[Token]):
        self._tokens = tokens_lista
        self._pos    = 0
        self.lineno  = 1   # PLY lo consulta para rastrear líneas

    def token(self):
        """Devuelve el siguiente token compatible con PLY, o None si terminó."""
        while self._pos < len(self._tokens):
            tok = self._tokens[self._pos]
            self._pos += 1
            self.lineno = tok.linea

            # Fin de archivo → señal de fin para PLY
            if tok.tipo == TipoToken.FIN:
                return None

            # Token desconocido: ya fue reportado por el lexer de Fase 1
            if tok.tipo == TipoToken.DESCONOCIDO:
                continue

            # IDs que actúan como operadores lógicos en la gramática
            if tok.tipo == TipoToken.ID and tok.valor in _LOGICOS:
                return _TokenPLY(_LOGICOS[tok.valor], tok.valor,
                                  tok.linea, tok.col_inicio)

            nombre = _MAPA.get(tok.tipo)
            if nombre is None:
                # Tokens sin rol en la gramática (LLAVE_IZQ, PUNTO_COMA, etc.)
                continue

            return _TokenPLY(nombre, tok.valor, tok.linea, tok.col_inicio)

        return None

    def input(self, _data):
        """Interfaz que PLY requiere; no se usa porque ya tenemos los tokens."""
        pass


# ─────────────────────────────────────────────────────────────────────────────
# TERMINALES Y PRECEDENCIA
# ─────────────────────────────────────────────────────────────────────────────

tokens = (
    'NENTERO', 'NFLOAT', 'CADENA', 'ID',
    'SI', 'SINO', 'MIENTRAS', 'FUNCION',
    'TIPO_ENTERO', 'TIPO_FLOAT', 'TIPO_BOOL', 'TIPO_CADENA',
    'VERDADERO', 'FALSO',
    'LEER', 'ESCRIBIR', 'RETORNAR',
    'OR', 'AND', 'NOT',
    'MAS', 'MENOS', 'MULT', 'DIV', 'MODULO', 'POTENCIA', 'DIV_ENTERA',
    'IGUAL', 'DIFERENTE', 'MENOR_QUE', 'MAYOR_QUE', 'MENOR_IGUAL', 'MAYOR_IGUAL',
    'ASIGNAR', 'MAS_IGUAL', 'MENOS_IGUAL', 'MULT_IGUAL', 'DIV_IGUAL',
    'PAR_IZQ', 'PAR_DER',
    'COMA', 'DOS_PUNTOS',
    'NUEVA_LINEA', 'INDENTAR', 'DESINDENTAR',
)

# Precedencia de MENOR a MAYOR (las últimas filas ganan sobre las primeras)
precedence = (
    ('left',  'OR'),
    ('left',  'AND'),
    ('right', 'NOT'),
    ('left',  'IGUAL', 'DIFERENTE',
               'MENOR_QUE', 'MAYOR_QUE', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
    ('left',  'MAS', 'MENOS'),
    ('left',  'MULT', 'DIV', 'MODULO', 'DIV_ENTERA'),
    ('right', 'POTENCIA'),
    ('right', 'UMENOS'),  # seudotoken para el menos unario (%prec)
)


# ─────────────────────────────────────────────────────────────────────────────
# REGLAS GRAMATICALES
# ─────────────────────────────────────────────────────────────────────────────

# ── Programa ──────────────────────────────────────────────────────────────────

def p_programa(p):
    """programa : sentencias"""
    p[0] = ('programa', p[1])

# ── Lista de sentencias ────────────────────────────────────────────────────────

def p_sentencias_varias(p):
    """sentencias : sentencias sentencia"""
    p[0] = p[1] + ([p[2]] if p[2] is not None else [])

def p_sentencias_una(p):
    """sentencias : sentencia"""
    p[0] = [p[1]] if p[1] is not None else []

# ── Sentencias individuales ────────────────────────────────────────────────────

def p_sentencia_vacia(p):
    """sentencia : NUEVA_LINEA"""
    # Línea en blanco: válida pero no genera nodo
    p[0] = None

def p_sentencia_decl(p):
    """sentencia : decl_variable NUEVA_LINEA"""
    p[0] = p[1]

def p_sentencia_asig(p):
    """sentencia : asignacion NUEVA_LINEA"""
    p[0] = p[1]

def p_sentencia_if(p):
    """sentencia : sent_if"""
    p[0] = p[1]

def p_sentencia_while(p):
    """sentencia : sent_while"""
    p[0] = p[1]

def p_sentencia_func(p):
    """sentencia : sent_func"""
    p[0] = p[1]

def p_sentencia_return_valor(p):
    """sentencia : RETORNAR expr NUEVA_LINEA"""
    p[0] = ('return', p[2])

def p_sentencia_return_vacio(p):
    """sentencia : RETORNAR NUEVA_LINEA"""
    p[0] = ('return', None)

def p_sentencia_write(p):
    """sentencia : ESCRIBIR PAR_IZQ expr PAR_DER NUEVA_LINEA"""
    p[0] = ('write', p[3])

def p_sentencia_read(p):
    """sentencia : LEER PAR_IZQ ID PAR_DER NUEVA_LINEA"""
    p[0] = ('read', p[3])

def p_sentencia_llamada(p):
    """sentencia : ID PAR_IZQ args PAR_DER NUEVA_LINEA"""
    # Llamada a función usada como sentencia (descarta el valor de retorno)
    p[0] = ('call_stmt', p[1], p[3])

def p_sentencia_error(p):
    """sentencia : error NUEVA_LINEA"""
    # Recuperación: al encontrar un error, PLY descarta tokens hasta NUEVA_LINEA
    p[0] = None

# ── Declaración de variable ────────────────────────────────────────────────────

def p_decl_simple(p):
    """decl_variable : tipo ID"""
    p[0] = ('decl', p[1], p[2], None)

def p_decl_con_asig(p):
    """decl_variable : tipo ID ASIGNAR expr"""
    p[0] = ('decl', p[1], p[2], p[4])

def p_tipo(p):
    """tipo : TIPO_ENTERO
            | TIPO_FLOAT
            | TIPO_BOOL
            | TIPO_CADENA"""
    p[0] = p[1]

# ── Asignación ────────────────────────────────────────────────────────────────

def p_asignacion(p):
    """asignacion : ID ASIGNAR     expr
                  | ID MAS_IGUAL   expr
                  | ID MENOS_IGUAL expr
                  | ID MULT_IGUAL  expr
                  | ID DIV_IGUAL   expr"""
    p[0] = ('asig', p[1], p[2], p[3])

# ── Bloque indentado ──────────────────────────────────────────────────────────

def p_bloque(p):
    """bloque : INDENTAR sentencias DESINDENTAR"""
    p[0] = ('bloque', p[2])

def p_bloque_error(p):
    """bloque : INDENTAR error DESINDENTAR"""
    # Recuperación dentro de un bloque mal formado
    p[0] = ('bloque', [])

# ── If / else ─────────────────────────────────────────────────────────────────

def p_sent_if(p):
    """sent_if : SI expr DOS_PUNTOS NUEVA_LINEA bloque"""
    p[0] = ('if', p[2], p[5], None)

def p_sent_if_else(p):
    """sent_if : SI expr DOS_PUNTOS NUEVA_LINEA bloque SINO DOS_PUNTOS NUEVA_LINEA bloque"""
    p[0] = ('if', p[2], p[5], p[9])

# ── While ─────────────────────────────────────────────────────────────────────

def p_sent_while(p):
    """sent_while : MIENTRAS expr DOS_PUNTOS NUEVA_LINEA bloque"""
    p[0] = ('while', p[2], p[5])

# ── Definición de función ─────────────────────────────────────────────────────

def p_sent_func(p):
    """sent_func : FUNCION ID PAR_IZQ params PAR_DER DOS_PUNTOS NUEVA_LINEA bloque"""
    p[0] = ('func', p[2], p[4], p[8])

# ── Parámetros formales ────────────────────────────────────────────────────────

def p_params_vacio(p):
    """params : """
    p[0] = []

def p_params_uno(p):
    """params : tipo ID"""
    p[0] = [(p[1], p[2])]

def p_params_mult(p):
    """params : params COMA tipo ID"""
    p[0] = p[1] + [(p[3], p[4])]

# ── Argumentos de llamada ─────────────────────────────────────────────────────

def p_args_vacio(p):
    """args : """
    p[0] = []

def p_args_uno(p):
    """args : expr"""
    p[0] = [p[1]]

def p_args_mult(p):
    """args : args COMA expr"""
    p[0] = p[1] + [p[3]]

# ── Expresiones ───────────────────────────────────────────────────────────────

def p_expr_binaria(p):
    """expr : expr OR          expr
            | expr AND         expr
            | expr IGUAL       expr
            | expr DIFERENTE   expr
            | expr MENOR_QUE   expr
            | expr MAYOR_QUE   expr
            | expr MENOR_IGUAL expr
            | expr MAYOR_IGUAL expr
            | expr MAS         expr
            | expr MENOS       expr
            | expr MULT        expr
            | expr DIV         expr
            | expr MODULO      expr
            | expr DIV_ENTERA  expr
            | expr POTENCIA    expr"""
    p[0] = ('binop', p[2], p[1], p[3])

def p_expr_not(p):
    """expr : NOT expr"""
    p[0] = ('unop', 'not', p[2])

def p_expr_umenos(p):
    """expr : MENOS expr %prec UMENOS"""
    # %prec UMENOS le da mayor precedencia que el MENOS binario
    p[0] = ('unop', '-', p[2])

def p_expr_paren(p):
    """expr : PAR_IZQ expr PAR_DER"""
    p[0] = p[2]

def p_expr_llamada(p):
    """expr : ID PAR_IZQ args PAR_DER"""
    p[0] = ('call', p[1], p[3])

def p_expr_id(p):
    """expr : ID"""
    p[0] = ('id', p[1])

def p_expr_entero(p):
    """expr : NENTERO"""
    p[0] = ('int', p[1])

def p_expr_float(p):
    """expr : NFLOAT"""
    p[0] = ('float', p[1])

def p_expr_cadena(p):
    """expr : CADENA"""
    p[0] = ('str', p[1])

def p_expr_true(p):
    """expr : VERDADERO"""
    p[0] = ('bool', True)

def p_expr_false(p):
    """expr : FALSO"""
    p[0] = ('bool', False)


# ─────────────────────────────────────────────────────────────────────────────
# MANEJO Y RECUPERACIÓN DE ERRORES SINTÁCTICOS
# ─────────────────────────────────────────────────────────────────────────────

_errores: List[str] = []

def p_error(p):
    """Reportar el error sintáctico. PLY usa las reglas 'error' para recuperarse."""
    global _errores

    if p is None:
        # EOF inesperado antes de que la gramática se complete
        _errores.append(
            "Línea ?, Col ?: Símbolo 'EOF': Error: fin de archivo inesperado"
        )
        return

    col = getattr(p, 'col', 0)
    _errores.append(
        f"Línea {p.lineno}, Col {col}: Símbolo '{p.value}': "
        f"Error: token inesperado '{p.type}'"
    )
    # PLY descarta tokens automáticamente hasta que puede aplicar la regla
    # 'sentencia : error NUEVA_LINEA' o 'bloque : INDENTAR error DESINDENTAR'


# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL PARSER
# ─────────────────────────────────────────────────────────────────────────────

_DIR = os.path.dirname(os.path.abspath(__file__))

# outputdir: donde PLY guarda parsetab.py (tabla LALR precalculada)
# errorlog=NullLogger(): suprime las advertencias internas de PLY en consola
parser = yacc.yacc(
    outputdir=_DIR,
    debug=False,
    errorlog=yacc.NullLogger(),
)


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PÚBLICA
# ─────────────────────────────────────────────────────────────────────────────

def parse_program(tokens_lista: List[Token],
                  errores_lexicos: List[str]) -> Tuple[bool, List[str]]:
    """
    Analizar sintácticamente la lista de tokens producida por Fase 1.

    Parámetros:
        tokens_lista   : lista de Token devuelta por AnalizadorLexico.tokenizar()
        errores_lexicos: lista de strings de error del lexer (Fase 1)

    Retorna:
        (exito, todos_los_errores)
        exito=True solo cuando no hay ningún error léxico ni sintáctico.
    """
    global _errores
    _errores = []

    adaptador = AdaptadorLexer(tokens_lista)

    try:
        parser.parse(lexer=adaptador, tracking=False)
    except Exception as exc:
        _errores.append(f"Error interno del parser: {exc}")

    todos = list(errores_lexicos) + _errores
    return (len(todos) == 0), todos
