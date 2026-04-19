"""
FASE 2: Orquestador del Analizador Sintáctico Ascendente de MiniLang.
Ejecuta Fase 1 (léxico) y Fase 2 (sintáctico) en cadena.
"""

import sys
import os
from pathlib import Path

# Rutas para importar módulos de ambas fases
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'FASE_1'))
sys.path.insert(0, os.path.dirname(__file__))

from analizador_lexico import AnalizadorLexico
from analizador_sintactico import parse_program


class CompiladoresFase2:
    """Orquesta el análisis léxico (Fase 1) y sintáctico (Fase 2) de MiniLang."""

    def __init__(self, archivo_path: str):
        self.archivo_path = Path(archivo_path)
        self.contenido    = None
        self.tokens_lista = []
        self.errores_lex  = []

    def validar_entrada(self) -> bool:
        """Verificar que el archivo exista y tenga la extensión correcta."""
        if not self.archivo_path.exists():
            print(f"ERROR: Archivo '{self.archivo_path}' no encontrado.")
            return False
        if self.archivo_path.suffix.lower() != '.mlng':
            print(f"Advertencia: se esperaba extensión .mlng, "
                  f"se recibió '{self.archivo_path.suffix}'.")
        return True

    def leer_archivo(self) -> bool:
        """Leer el contenido del archivo fuente."""
        try:
            with open(self.archivo_path, 'r', encoding='utf-8') as f:
                self.contenido = f.read()
            return True
        except UnicodeDecodeError:
            print(f"ERROR: No se puede leer '{self.archivo_path}' — encoding no soportado.")
            return False
        except Exception as exc:
            print(f"ERROR al leer el archivo: {exc}")
            return False

    def ejecutar_fase1(self) -> bool:
        """Fase 1: Análisis Léxico — obtener tokens y recopilar errores léxicos."""
        try:
            lexer = AnalizadorLexico(self.contenido)
            self.tokens_lista = lexer.tokenizar(
                incluir_comentarios=False,
                incluir_nuevas_lineas=True
            )
            self.errores_lex = list(lexer.errores)

            if not self.tokens_lista:
                print("ERROR: No se generaron tokens. Verifique el archivo.")
                return False

            return True
        except Exception as exc:
            print(f"ERROR en Fase 1 (Análisis Léxico): {exc}")
            return False

    def ejecutar_fase2(self) -> bool:
        """
        Fase 2: Análisis Sintáctico — validar la estructura del programa.
        Imprime OK si es correcto, o la lista de errores si los hay.
        """
        try:
            exito, errores = parse_program(self.tokens_lista, self.errores_lex)

            if exito:
                print("OK")
                return True
            else:
                for err in errores:
                    print(err)
                return False

        except Exception as exc:
            print(f"ERROR en Fase 2 (Análisis Sintáctico): {exc}")
            return False

    def compilar(self) -> bool:
        """Ejecutar la compilación completa. Retorna True si no hubo errores."""
        if not self.validar_entrada():
            return False
        if not self.leer_archivo():
            return False
        if not self.ejecutar_fase1():
            return False
        return self.ejecutar_fase2()


def compilar_archivo(archivo_path: str) -> int:
    """Compilar un archivo y retornar código de salida (0=éxito, 1=error)."""
    compilador = CompiladoresFase2(archivo_path)
    return 0 if compilador.compilar() else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python minilang_fase2.py <archivo.mlng>")
        sys.exit(1)

    sys.exit(compilar_archivo(sys.argv[1]))
