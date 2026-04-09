"""
FASE 2: Analizador Sintáctico Simple
Valida estructura básica del programa MiniLang.
Versión simplificada enfocada en validación estructural.
"""

import sys
import os
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'FASE_1'))

from analizador_lexico import TipoToken, Token
from ast_node import Program, Statement, Declaration, WriteStmt, Block, StringLiteral


class ErrorSet:
    """Collect syntax errors during parsing"""
    def __init__(self):
        self.errors = []

    def add(self, línea: int, col: int, símbolo: str, descripción: str):
        self.errors.append({
            'línea': línea,
            'col': col,
            'símbolo': símbolo,
            'descripción': descripción
        })

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def report(self):
        for error in self.errors:
            print(f"Línea {error['línea']}, Col {error['col']}: ERROR - "
                  f"Símbolo '{error['símbolo']}': {error['descripción']}")


class AnalizadorSintacticoSimple:
    """
    Parser simple recursivo descendente.
    Valida la estructura básica del programa sin análisis complejosde precedencias.
    """

    def __init__(self, tokens_list: List[Token]):
        self.tokens = tokens_list
        self.pos = 0
        self.errors = ErrorSet()
        self.current_token = tokens_list[0] if tokens_list else None

    def _advance(self):
        """Avanzar al siguiente token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _peek(self, offset=1):
        """Mirar ahead sin avanzar"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def _match(self, *tipos):
        """Verificar si token actual coincide con uno de los tipos"""
        if self.current_token and self.current_token.tipo in tipos:
            return True
        return False

    def _consume(self, tipo_esperado):
        """Consumir token del tipo esperado o registrar error"""
        if not self.current_token:
            self.errors.add(1, 0, 'EOF', 'Token esperado pero llegó fin de archivo')
            return False

        if self.current_token.tipo != tipo_esperado:
            self.errors.add(
                self.current_token.linea,
                self.current_token.col_inicio,
                self.current_token.tipo.name,
                f"Esperado {tipo_esperado.name}, recibido {self.current_token.tipo.name}"
            )
            return False

        self._advance()
        return True

    def parse_programa(self) -> Optional[Program]:
        """Parsear programa completo"""
        statements = []

        while self.current_token and self.current_token.tipo != TipoToken.FIN:
            # Saltar nuevas líneas
            if self._match(TipoToken.NUEVA_LINEA):
                self._advance()
                continue

            # Parsear sentencia
            stmt = self.parse_sentencia()
            if stmt:
                statements.append(stmt)
            else:
                # Si hay error, intentar recuperar saltando hasta siguiente newline
                if not self.errors.has_errors():
                    break
                while self.current_token and self.current_token.tipo != TipoToken.NUEVA_LINEA:
                    self._advance()
                if self.current_token:
                    self._advance()

        return Program(statements)

    def parse_sentencia(self) -> Optional[Statement]:
        """Parsear una sentencia individual"""
        if not self.current_token or self.current_token.tipo == TipoToken.FIN:
            return None

        # write statement
        if self._match(TipoToken.ESCRIBIR):
            return self.parse_write()

        # Simplemente retornar None para otros tipos por ahora
        # y avanzar para evitar bucle infinito
        self._advance()
        return None

    def parse_write(self) -> Optional[WriteStmt]:
        """Parsear write(...) statement"""
        if not self._consume(TipoToken.ESCRIBIR):
            return None

        if not self._consume(TipoToken.PAR_IZQ):
            self.errors.add(1, 0, 'PAR_IZQ', 'Esperado "(" después de write')
            return None

        # Parsear expresión (simplemente cadena por ahora)
        if self.current_token and self.current_token.tipo == TipoToken.CADENA:
            valor = self.current_token.valor
            self._advance()

            # Parsear cierre
            if not self._consume(TipoToken.PAR_DER):
                self.errors.add(1, 0, 'PAR_DER', 'Esperado ")" después de argumento')
                return None

            # Consumir newline
            if self._match(TipoToken.NUEVA_LINEA):
                self._advance()

            return WriteStmt(StringLiteral(valor))
        else:
            self.errors.add(
                self.current_token.linea if self.current_token else 1,
                self.current_token.col_inicio if self.current_token else 0,
                'CADENA',
                'Esperado cadena en write()'
            )
            return None


def parse_program(contenido: str, tokens_list: List[Token]) -> Tuple[Optional[Program], ErrorSet]:
    """
    Parsear programa desde lista de tokens
    Retorna (Program AST, ErrorSet)
    """
    parser = AnalizadorSintacticoSimple(tokens_list)
    ast = parser.parse_programa()
    return ast, parser.errors
