import sys
import os
from pathlib import Path
from analizador_lexico import AnalizadorLexico, TipoToken


def analizar(ruta_entrada: str) -> None:
    ruta = Path(ruta_entrada)

    if not ruta.exists():
        print(f"Error: el archivo '{ruta_entrada}' no existe.")
        sys.exit(1)

    if ruta.suffix.lower() != '.mlng':
        print(f"Advertencia: se esperaba extensión .mlng, pero se recibió '{ruta.suffix}'")

    codigo = ruta.read_text(encoding='utf-8')

    analizador = AnalizadorLexico(codigo)
    tokens     = analizador.tokenizar(incluir_comentarios=False, incluir_nuevas_lineas=True)

    # hacer archivo out
    lineas_out = []
    for tok in tokens:
        if tok.tipo == TipoToken.FIN:
            lineas_out.append(f"({tok.linea},{tok.col_inicio}-{tok.col_fin}) FIN")
        else:
            val_str = ""
            if tok.valor is not None and tok.tipo not in (
                    TipoToken.NUEVA_LINEA, TipoToken.INDENTAR, TipoToken.DESINDENTAR):
                val_str = f" {tok.valor}"
            lineas_out.append(
                f"({tok.linea},{tok.col_inicio}-{tok.col_fin}) "
                f"{tok.tipo.name}{val_str}"
            )

    contenido_out = "\n".join(lineas_out) + "\n"

    # escribir en el archivo out
    ruta_out = ruta.with_suffix('.out')
    ruta_out.write_text(contenido_out, encoding='utf-8')
    print(f"Tokens escritos en: {ruta_out}")

    # imprimir los errores y tokens en consola
    if analizador.errores:
        print("\n=== ERRORES LÉXICOS ===")
        for err in analizador.errores:
            print(err)
    else:
        print("Análisis léxico exitoso — sin errores.")
        print("\n=== TOKENS LEÍDOS ===")
        print(f"{'TIPO':<20} {'VALOR':<25} {'LÍNEA:COL'}")
        print("-" * 55)
        for tok in tokens:
            valor    = str(tok.valor) if tok.valor is not None else ""
            posicion = f"{tok.linea}:{tok.col_inicio}-{tok.col_fin}"
            print(f"{tok.tipo.name:<20} {valor:<25} {posicion}")

def main():
    while True:
        ruta = input("Ingresa la ruta del archivo .mlng a analizar: ").strip()
        
        if os.path.exists(ruta):
            break
        else:
            print("El archivo no existe. Intenta nuevamente.\n")

    analizar(ruta)


if __name__ == "__main__":
    main()