import os
import sys
from pathlib import Path

# Permitir imports de FASE_1, FASE_2 y FASE_3
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_BASE, '..', 'FASE_1'))
sys.path.insert(0, os.path.join(_BASE, '..', 'FASE_2'))
sys.path.insert(0, _BASE)

from analizador_lexico import AnalizadorLexico
import analizador_sintactico as sint
from analizador_semantico import AnalizadorSemantico


class CompiladoresFase3:
    def __init__(self, archivo_path: str):
        self.archivo_path = Path(archivo_path)
        self.contenido = None
        self.tokens_lista = []
        self.errores_lex = []
        self.arbol = None

    def validar_entrada(self) -> bool:
        if not self.archivo_path.exists():
            print(f"ERROR: Archivo '{self.archivo_path}' no encontrado.")
            return False
        if self.archivo_path.suffix.lower() != '.mlng':
            print(
                f"Advertencia: se esperaba extension .mlng, se recibio '{self.archivo_path.suffix}'."
            )
        return True

    def leer_archivo(self) -> bool:
        try:
            with open(self.archivo_path, 'r', encoding='utf-8') as f:
                self.contenido = f.read()
            return True
        except Exception as exc:
            print(f"ERROR al leer el archivo: {exc}")
            return False

    def ejecutar_fase1(self) -> bool:
        try:
            lexer = AnalizadorLexico(self.contenido)
            self.tokens_lista = lexer.tokenizar(
                incluir_comentarios=False,
                incluir_nuevas_lineas=True,
            )
            self.errores_lex = list(lexer.errores)
            return bool(self.tokens_lista)
        except Exception as exc:
            print(f"ERROR en Fase 1: {exc}")
            return False

    def ejecutar_fase2(self):
        # Reutiliza parser y adaptador de la fase 2 para obtener arbol y errores.
        sint._errores = []
        adaptador = sint.AdaptadorLexer(self.tokens_lista)

        try:
            self.arbol = sint.parser.parse(lexer=adaptador, tracking=False)
        except Exception as exc:
            sint._errores.append(f"Error interno del parser: {exc}")

        errores = list(self.errores_lex) + list(sint._errores)
        return (len(errores) == 0), errores

    def ejecutar_fase3(self):
        semantico = AnalizadorSemantico()
        errores_sem = semantico.analizar(self.arbol)
        return (len(errores_sem) == 0), errores_sem

    def compilar(self) -> bool:
        if not self.validar_entrada():
            return False
        if not self.leer_archivo():
            return False
        if not self.ejecutar_fase1():
            return False

        exito_sint, errores_sint = self.ejecutar_fase2()
        if not exito_sint:
            for err in errores_sint:
                print(err)
            return False

        exito_sem, errores_sem = self.ejecutar_fase3()
        if not exito_sem:
            for err in errores_sem:
                print(err)
            return False

        print("OK")
        return True


def compilar_archivo_fase3(archivo_path: str) -> int:
    compilador = CompiladoresFase3(archivo_path)
    return 0 if compilador.compilar() else 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python FASE_3/minilang_fase3.py <archivo.mlng>')
        sys.exit(1)
    sys.exit(compilar_archivo_fase3(sys.argv[1]))
