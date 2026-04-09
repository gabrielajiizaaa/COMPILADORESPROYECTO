
import sys
import os
from pathlib import Path

# Agregar rutas para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'FASE_1'))
sys.path.insert(0, os.path.dirname(__file__))

from analizador_lexico import AnalizadorLexico
from analizador_sintactico import parse_program, ErrorSet
from ast_node import Program


class CompiladoresFase2:
    """Orchestrador de Fase 2: Análisis Sintáctico"""

    def __init__(self, archivo_path: str):
        """
        Inicializar compilador Fase 2
        Args:
            archivo_path: Ruta al archivo .mlng a compilar
        """
        self.archivo_path = Path(archivo_path)
        self.contenido = None
        self.ast = None
        self.errores = None

    def validar_entrada(self) -> bool:
        """Validar que el archivo exista y tenga extensión correcta"""
        if not self.archivo_path.exists():
            print(f"ERROR: Archivo '{self.archivo_path}' no encontrado")
            return False

        if self.archivo_path.suffix.lower() != '.mlng':
            print(f"Advertencia: se esperaba extensión .mlng, pero se recibió '{self.archivo_path.suffix}'")

        return True

    def leer_archivo(self) -> bool:
        """Leer contenido del archivo"""
        try:
            with open(self.archivo_path, 'r', encoding='utf-8') as f:
                self.contenido = f.read()
            return True
        except UnicodeDecodeError:
            print(f"ERROR: No se puede leer el archivo {self.archivo_path} - encoding no soportado")
            return False
        except Exception as e:
            print(f"ERROR: No se puede leer el archivo: {str(e)}")
            return False

    def ejecutar_fase1(self) -> bool:
        """
        Ejecutar Fase 1: Análisis Léxico
        Valida que el contenido genere tokens sin errores irrecuperables
        """
        try:
            lexer = AnalizadorLexico(self.contenido)
            tokens_list = lexer.tokenizar(incluir_comentarios=False, incluir_nuevas_lineas=True)

            if lexer.errores:
                print("\n=== ERRORES LÉXICOS DETECTADOS ===")
                for error in lexer.errores:
                    print(error)

            # Continuamos incluso con errores léxicos (recuperación)
            if not tokens_list:
                print("ERROR: No se generaron tokens. Verifique el contenido del archivo.")
                return False

            print(f"[Fase 1] Análisis léxico completado: {len(tokens_list)} tokens generados")
            self.tokens_list = tokens_list
            return True

        except Exception as e:
            print(f"ERROR en Fase 1 (Análisis Léxico): {str(e)}")
            return False

    def ejecutar_fase2(self) -> bool:
        """
        Ejecutar Fase 2: Análisis Sintáctico
        Valida la estructura del programa
        """
        try:
            self.ast, self.errores = parse_program(self.contenido, self.tokens_list)

            if self.errores.has_errors():
                print("\n=== ERRORES SINTÁCTICOS DETECTADOS ===")
                self.errores.report()
                return False

            print("[Fase 2] Análisis sintáctico exitoso")
            return True

        except Exception as e:
            print(f"ERROR en Fase 2 (Análisis Sintáctico): {str(e)}")
            return False

    def compilar(self) -> bool:
        """
        Ejecutar compilación completa (Fase 1 + Fase 2)
        Retorna True si éxito, False si hay errores
        """
        print(f"\n=== Compilando: {self.archivo_path} ===\n")

        # Validar entrada
        if not self.validar_entrada():
            return False

        # Leer archivo
        if not self.leer_archivo():
            return False

        print(f"[Entrada] Archivo leído correctamente ({len(self.contenido)} caracteres)")

        # Ejecutar Fase 1: Análisis Léxico
        if not self.ejecutar_fase1():
            return False

        # Ejecutar Fase 2: Análisis Sintáctico
        if not self.ejecutar_fase2():
            return False

        print("\n=== ANÁLISIS COMPLETADO EXITOSAMENTE ===\n")
        return True


def compilar_archivo(archivo_path: str) -> int:
    """
    Función principal para compilar un archivo
    Retorna código de salida (0 = éxito, 1 = error)
    """
    compilador = CompiladoresFase2(archivo_path)

    if compilador.compilar():
        return 0
    else:
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python minilang_fase2.py <archivo.mlng>")
        sys.exit(1)

    archivo = sys.argv[1]
    exit_code = compilar_archivo(archivo)
    sys.exit(exit_code)
