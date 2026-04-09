import sys
import os
from pathlib import Path

# Agregar ruta de FASE_2
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FASE_2'))

from minilang_fase2 import compilar_archivo


def main():
    """Función principal"""
    print("=" * 60)
    print("MiniLang Compilador - Fase 2: Análisis Sintáctico")
    print("=" * 60)

    # Si se pasa archivo como argumento, usarlo
    if len(sys.argv) >= 2:
        archivo = sys.argv[1]
    else:
        # Si no, pedir al usuario que lo ingrese
        print("\nArchivos disponibles:")
        directorio = Path(os.path.dirname(__file__))
        archivos_mlng = list(directorio.glob("*.mlng"))

        if archivos_mlng:
            for i, f in enumerate(archivos_mlng, 1):
                print(f"  {i}. {f.name}")

        print("\nIngresa el nombre del archivo .mlng a compilar")
        print("(o la ruta completa si está en otra carpeta):")
        archivo = input("> ").strip()

        if not archivo:
            print("Error: Debes ingresar un archivo.")
            sys.exit(1)

    # Verificar que el archivo exista
    ruta = Path(archivo)

    # Si la ruta no existe, intentar buscarla en el directorio del script
    if not ruta.exists():
        ruta_script = Path(os.path.dirname(__file__)) / archivo
        if ruta_script.exists():
            ruta = ruta_script
        else:
            print(f"Error: El archivo '{archivo}' no existe.")
            print(f"  Buscado en directorio actual: {Path(archivo).resolve()}")
            print(f"  Buscado en directorio del script: {ruta_script}")
            sys.exit(1)

    if ruta.suffix.lower() != '.mlng':
        print(f"Advertencia: se esperaba extensión .mlng, pero se recibió '{ruta.suffix}'")

    print()
    # Ejecutar compilación
    exit_code = compilar_archivo(str(ruta))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()