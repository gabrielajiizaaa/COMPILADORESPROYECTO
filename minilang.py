"""
MiniLang — punto de entrada principal.
Uso: python minilang.py <archivo.mlng>
"""

import sys
import os

# Forzar UTF-8 en la consola de Windows para mostrar tildes y caracteres especiales
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path

# Agregar FASE_2 al path para importar el orquestador
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'FASE_2'))

from minilang_fase2 import compilar_archivo


def main():
    """Función principal: pide el archivo si no se pasa como argumento."""
    # Si se pasa archivo como argumento, usarlo directamente
    if len(sys.argv) >= 2:
        archivo = sys.argv[1]
    else:
        # Buscar archivos .mlng disponibles para orientar al usuario
        directorio = Path(os.path.dirname(os.path.abspath(__file__)))
        archivos = sorted(directorio.rglob('*.mlng'))

        if archivos:
            print("Archivos .mlng disponibles:")
            for f in archivos:
                print(f"  {f.relative_to(directorio)}")
            print()

        print("Ingresa la ruta del archivo .mlng a compilar:")
        archivo = input("> ").strip()

        if not archivo:
            print("Error: debes ingresar un archivo.")
            sys.exit(1)

    # Resolver la ruta
    ruta = Path(archivo)
    if not ruta.is_absolute():
        # Intentar relativo al directorio del script
        alt = Path(os.path.dirname(os.path.abspath(__file__))) / archivo
        if alt.exists():
            ruta = alt

    if not ruta.exists():
        print(f"Error: el archivo '{archivo}' no existe.")
        sys.exit(1)

    sys.exit(compilar_archivo(str(ruta)))


if __name__ == "__main__":
    main()
