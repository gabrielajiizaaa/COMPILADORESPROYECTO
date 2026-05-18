from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class SimboloInfo:
    tipo: str
    valor: Any = None


@dataclass
class FuncionInfo:
    nombre: str
    parametros: List[Tuple[str, str]]


class TablaSimbolos:
    def __init__(self):
        self._ambitos: List[Dict[str, SimboloInfo]] = [{}]
        self._historial: List[Dict[str, Any]] = []

    def entrar_ambito(self):
        self._ambitos.append({})

    def salir_ambito(self):
        if len(self._ambitos) > 1:
            self._ambitos.pop()

    def declarar(self, nombre: str, tipo: str, valor: Any = None) -> bool:
        ambito = self._ambitos[-1]
        if nombre in ambito:
            return False
        info = SimboloInfo(tipo=tipo, valor=valor)
        ambito[nombre] = info
        self._historial.append({
            'nombre': nombre,
            'ambito': len(self._ambitos) - 1,
            'info': info,
        })
        return True

    def actualizar_valor(self, nombre: str, valor: Any):
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                ambito[nombre].valor = valor
                return

    def buscar(self, nombre: str) -> Optional[str]:
        """Devuelve solo el tipo (retrocompatibilidad)."""
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre].tipo
        return None

    def buscar_info(self, nombre: str) -> Optional[SimboloInfo]:
        """Devuelve el SimboloInfo completo (tipo + valor)."""
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def obtener_todos(self) -> List[Dict]:
        """Devuelve todos los símbolos declarados (histórico completo)."""
        resultado = []
        for item in self._historial:
            info = item['info']
            resultado.append({
                'nombre': item['nombre'],
                'tipo': info.tipo,
                'valor': info.valor,
                'ambito': item['ambito'],
                'activo': self._simbolo_activo(info),
            })
        return resultado

    def _simbolo_activo(self, info_obj: SimboloInfo) -> bool:
        for ambito in self._ambitos:
            for info in ambito.values():
                if info is info_obj:
                    return True
        return False


class AnalizadorSemantico:
    def __init__(self):
        self.errores: List[str] = []
        self.variables = TablaSimbolos()
        self.funciones: Dict[str, FuncionInfo] = {}
        self._funcion_actual: Optional[str] = None
        self._pos_actual: Tuple[int, int] = (0, 0)  # (linea, col) de la sentencia en curso

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _error(self, linea: int, col: int, mensaje: str):
        """Registra un error con formato uniforme: linea X, col Y: ERROR <msg>"""
        self.errores.append(f"linea {linea}, col {col}: ERROR {mensaje}")

    @staticmethod
    def _extraer_pos(nodo, idx_linea: int, idx_col: int) -> Tuple[int, int]:
        """Extrae (linea, col) de un nodo AST por índice, o (0,0) si no existe."""
        try:
            return int(nodo[idx_linea]), int(nodo[idx_col])
        except (IndexError, TypeError):
            return (0, 0)

    def analizar(self, arbol) -> List[str]:
        if not arbol or arbol[0] != 'programa':
            self.errores.append("Arbol sintactico invalido o vacio")
            return self.errores

        for sentencia in arbol[1]:
            self._analizar_sentencia(sentencia)
        return self.errores

    def obtener_tabla_completa(self) -> List[Dict[str, Any]]:
        filas: List[Dict[str, Any]] = []

        for var in self.variables.obtener_todos():
            filas.append({
                'categoria': 'variable',
                'nombre': var['nombre'],
                'tipo': var['tipo'],
                'ambito': var['ambito'],
                'valor': var['valor'],
                'detalle': 'activa' if var.get('activo') else 'fuera de ambito',
            })

        for fun in self.funciones.values():
            firma = ', '.join([f"{t} {n}" for t, n in fun.parametros])
            filas.append({
                'categoria': 'funcion',
                'nombre': fun.nombre,
                'tipo': 'func',
                'ambito': 0,
                'valor': '-',
                'detalle': f"params: ({firma})",
            })

        return filas

    def generar_archivo_tabla(self, archivo_fuente: str) -> str:
        src = Path(archivo_fuente)
        salida = src.with_name(f"{src.stem}_tabla_simbolos.txt")

        filas = self.obtener_tabla_completa()

        with open(salida, 'w', encoding='utf-8') as f:
            f.write("TABLA DE SIMBOLOS - FASE 3\n")
            f.write(f"Archivo analizado: {src.name}\n")
            f.write("\n")
            f.write("categoria | nombre | tipo | ambito | valor | detalle\n")
            f.write("-" * 72 + "\n")

            if not filas:
                f.write("(sin simbolos)\n")
            else:
                for fila in filas:
                    valor = fila['valor']
                    valor_txt = '-' if valor is None else str(valor)
                    linea = (
                        f"{fila['categoria']} | {fila['nombre']} | {fila['tipo']} | "
                        f"{fila['ambito']} | {valor_txt} | {fila['detalle']}\n"
                    )
                    f.write(linea)

        return str(salida)

    def _analizar_sentencia(self, sentencia):
        if sentencia is None:
            return

        tipo = sentencia[0]

        if tipo == 'decl':
            self._analizar_declaracion(sentencia)
        elif tipo == 'asig':
            self._analizar_asignacion(sentencia)
        elif tipo == 'if':
            self._analizar_if(sentencia)
        elif tipo == 'while':
            self._analizar_while(sentencia)
        elif tipo == 'func':
            self._analizar_funcion(sentencia)
        elif tipo == 'return':
            self._analizar_return(sentencia)
        elif tipo == 'write':
            # ('write', expr, linea, col)
            linea, col = self._extraer_pos(sentencia, 2, 3)
            self._pos_actual = (linea, col)
            self._tipo_expr(sentencia[1])
        elif tipo == 'read':
            # ('read', nombre, linea, col)
            nombre = sentencia[1]
            linea, col = self._extraer_pos(sentencia, 2, 3)
            self._pos_actual = (linea, col)
            if self.variables.buscar(nombre) is None:
                self._error(linea, col, f"Variable no declarada en read: '{nombre}'")
        elif tipo == 'call_stmt':
            # ('call_stmt', nombre, args, linea, col)
            linea, col = self._extraer_pos(sentencia, 3, 4)
            self._pos_actual = (linea, col)
            self._tipo_expr(('call', sentencia[1], sentencia[2], linea, col))
        else:
            l, c = self._pos_actual
            self._error(l, c, f"Sentencia no soportada en fase 3: {tipo}")

    def _analizar_bloque(self, bloque):
        if not bloque or bloque[0] != 'bloque':
            self.errores.append("Bloque invalido")
            return

        self.variables.entrar_ambito()
        for sentencia in bloque[1]:
            self._analizar_sentencia(sentencia)
        self.variables.salir_ambito()

    def _analizar_declaracion(self, sentencia):
        # ('decl', tipo, nombre, expr, linea, col)
        tipo_decl, nombre, expr = sentencia[1], sentencia[2], sentencia[3]
        linea, col = self._extraer_pos(sentencia, 4, 5)
        self._pos_actual = (linea, col)

        if not self.variables.declarar(nombre, tipo_decl):
            self._error(linea, col, f"Variable redeclarada en el mismo ambito: '{nombre}'")
            return

        if expr is not None:
            tipo_expr = self._tipo_expr(expr)
            if not self._tipos_compatibles(tipo_decl, tipo_expr):
                self._error(linea, col,
                    f"Asignacion incompatible en declaracion de '{nombre}': {tipo_decl} <- {tipo_expr}"
                )
            else:
                valor = self._evaluar_expr(expr)
                if valor is not None:
                    self.variables.actualizar_valor(nombre, valor)

    def _analizar_asignacion(self, sentencia):
        # ('asig', nombre, operador, expr, linea, col)
        nombre, operador, expr = sentencia[1], sentencia[2], sentencia[3]
        linea, col = self._extraer_pos(sentencia, 4, 5)
        self._pos_actual = (linea, col)

        tipo_var = self.variables.buscar(nombre)
        if tipo_var is None:
            self._error(linea, col, f"Variable no declarada: '{nombre}'")
            return

        tipo_expr = self._tipo_expr(expr)
        if operador == '=':
            if not self._tipos_compatibles(tipo_var, tipo_expr):
                self._error(linea, col,
                    f"Asignacion incompatible en '{nombre}': {tipo_var} <- {tipo_expr}"
                )
            else:
                valor = self._evaluar_expr(expr)
                if valor is not None:
                    self.variables.actualizar_valor(nombre, valor)
            return

        if operador in ('+=', '-=', '*=', '/='):
            if tipo_var not in ('int', 'float') or tipo_expr not in ('int', 'float'):
                self._error(linea, col,
                    f"Operador {operador} requiere tipos numericos en '{nombre}'"
                )
            else:
                valor_actual = self.variables.buscar_info(nombre).valor
                valor_expr = self._evaluar_expr(expr)
                if valor_actual is not None and valor_expr is not None:
                    if operador == '+=':
                        nuevo = valor_actual + valor_expr
                    elif operador == '-=':
                        nuevo = valor_actual - valor_expr
                    elif operador == '*=':
                        nuevo = valor_actual * valor_expr
                    elif operador == '/=':
                        nuevo = valor_actual / valor_expr if valor_expr != 0 else None
                    if nuevo is not None:
                        self.variables.actualizar_valor(nombre, nuevo)

    def _analizar_if(self, sentencia):
        # ('if', condicion, bloque_then, bloque_else, linea, col)
        condicion, bloque_then, bloque_else = sentencia[1], sentencia[2], sentencia[3]
        linea, col = self._extraer_pos(sentencia, 4, 5)
        self._pos_actual = (linea, col)

        tipo_cond = self._tipo_expr(condicion)
        if tipo_cond not in ('bool', 'any'):
            self._error(linea, col, f"Condicion de if debe ser bool, no {tipo_cond}")

        self._analizar_bloque(bloque_then)
        if bloque_else is not None:
            self._analizar_bloque(bloque_else)

    def _analizar_while(self, sentencia):
        # ('while', condicion, bloque, linea, col)
        condicion, bloque = sentencia[1], sentencia[2]
        linea, col = self._extraer_pos(sentencia, 3, 4)
        self._pos_actual = (linea, col)

        tipo_cond = self._tipo_expr(condicion)
        if tipo_cond not in ('bool', 'any'):
            self._error(linea, col, f"Condicion de while debe ser bool, no {tipo_cond}")
        self._analizar_bloque(bloque)

    def _analizar_funcion(self, sentencia):
        # ('func', nombre, parametros, bloque, linea, col)
        nombre, parametros, bloque = sentencia[1], sentencia[2], sentencia[3]
        linea, col = self._extraer_pos(sentencia, 4, 5)
        self._pos_actual = (linea, col)

        if nombre in self.funciones:
            self._error(linea, col, f"Funcion redeclarada: '{nombre}'")
            return

        self.funciones[nombre] = FuncionInfo(nombre=nombre, parametros=parametros)

        anterior = self._funcion_actual
        self._funcion_actual = nombre

        self.variables.entrar_ambito()
        for tipo_param, nombre_param in parametros:
            if not self.variables.declarar(nombre_param, tipo_param):
                self._error(linea, col,
                    f"Parametro duplicado '{nombre_param}' en funcion '{nombre}'"
                )

        for st in bloque[1]:
            self._analizar_sentencia(st)

        self.variables.salir_ambito()
        self._funcion_actual = anterior

    def _analizar_return(self, sentencia):
        # ('return', expr, linea, col)
        expr = sentencia[1]
        linea, col = self._extraer_pos(sentencia, 2, 3)
        self._pos_actual = (linea, col)

        if self._funcion_actual is None:
            self._error(linea, col, "return fuera de una funcion")
            return

        if expr is not None:
            self._tipo_expr(expr)

    def _tipo_expr(self, expr) -> str:
        if expr is None:
            return 'void'

        tag = expr[0]

        if tag == 'int':
            return 'int'
        if tag == 'float':
            return 'float'
        if tag == 'str':
            return 'string'
        if tag == 'bool':
            return 'bool'

        if tag == 'id':
            # ('id', nombre, linea, col)
            nombre = expr[1]
            linea, col = self._extraer_pos(expr, 2, 3)
            if linea == 0:
                linea, col = self._pos_actual
            tipo_var = self.variables.buscar(nombre)
            if tipo_var is None:
                self._error(linea, col, f"Variable no declarada: '{nombre}'")
                return 'error'
            return tipo_var

        if tag == 'call':
            # ('call', nombre, args, linea, col)
            nombre = expr[1]
            args   = expr[2]
            linea, col = self._extraer_pos(expr, 3, 4)
            if linea == 0:
                linea, col = self._pos_actual
            info = self.funciones.get(nombre)
            if info is None:
                self._error(linea, col, f"Funcion no declarada: '{nombre}'")
                for arg in args:
                    self._tipo_expr(arg)
                return 'error'

            if len(args) != len(info.parametros):
                self._error(linea, col,
                    f"Cantidad de argumentos invalida en '{nombre}': "
                    f"{len(args)} != {len(info.parametros)}"
                )
            else:
                for idx, arg in enumerate(args):
                    tipo_arg = self._tipo_expr(arg)
                    tipo_param = info.parametros[idx][0]
                    if not self._tipos_compatibles(tipo_param, tipo_arg):
                        self._error(linea, col,
                            f"Tipo de argumento invalido en '{nombre}' posicion {idx + 1}: "
                            f"{tipo_param} <- {tipo_arg}"
                        )
            return 'any'

        if tag == 'unop':
            # ('unop', op, expr, linea, col)
            op = expr[1]
            linea, col = self._extraer_pos(expr, 3, 4)
            if linea == 0:
                linea, col = self._pos_actual
            tipo_rhs = self._tipo_expr(expr[2])

            if op == '-':
                if tipo_rhs not in ('int', 'float'):
                    self._error(linea, col,
                        f"Operador unario '-' requiere numerico, no {tipo_rhs}")
                    return 'error'
                return tipo_rhs

            if op == 'not':
                if tipo_rhs != 'bool':
                    self._error(linea, col,
                        f"Operador 'not' requiere bool, no {tipo_rhs}")
                    return 'error'
                return 'bool'

            self._error(linea, col, f"Operador unario no soportado: {op}")
            return 'error'

        if tag == 'binop':
            # ('binop', op, izq, der, linea, col)
            op = expr[1]
            linea, col = self._extraer_pos(expr, 4, 5)
            if linea == 0:
                linea, col = self._pos_actual
            izq = self._tipo_expr(expr[2])
            der = self._tipo_expr(expr[3])

            if op in ('+', '-', '*', '/', '%', '//', '**'):
                if op == '+' and izq == 'string' and der == 'string':
                    return 'string'
                if izq not in ('int', 'float') or der not in ('int', 'float'):
                    self._error(linea, col,
                        f"Operador '{op}' requiere operandos numericos "
                        f"(o string+string), no {izq} y {der}"
                    )
                    return 'error'
                if op == '/':
                    return 'float'
                return 'float' if 'float' in (izq, der) else 'int'

            if op in ('==', '!=', '<', '>', '<=', '>='):
                if not self._comparables(izq, der):
                    self._error(linea, col,
                        f"Comparacion invalida entre tipos {izq} y {der}")
                return 'bool'

            if op in ('and', 'or'):
                if izq != 'bool' or der != 'bool':
                    self._error(linea, col,
                        f"Operador logico '{op}' requiere bool y bool, no {izq} y {der}"
                    )
                    return 'error'
                return 'bool'

            self._error(linea, col, f"Operador binario no soportado: {op}")
            return 'error'

        l, c = self._pos_actual
        self._error(l, c, f"Nodo de expresion no soportado: {tag}")
        return 'error'

    def _evaluar_expr(self, expr) -> Any:
        """Evalúa el valor real de una expresión en tiempo de compilación.
        Devuelve None si el valor no puede determinarse (p.ej. read, llamadas a función)."""
        if expr is None:
            return None

        tag = expr[0]

        if tag == 'int':
            return int(expr[1])
        if tag == 'float':
            return float(expr[1])
        if tag == 'str':
            return str(expr[1])
        if tag == 'bool':
            return bool(expr[1])

        if tag == 'id':
            info = self.variables.buscar_info(expr[1])
            return info.valor if info else None

        if tag == 'unop':
            # ('unop', op, expr, linea, col)
            op = expr[1]
            val = self._evaluar_expr(expr[2])
            if val is None:
                return None
            if op == '-':
                return -val
            if op == 'not':
                return not val
            return None

        if tag == 'binop':
            # ('binop', op, izq, der, linea, col)
            op = expr[1]
            izq = self._evaluar_expr(expr[2])
            der = self._evaluar_expr(expr[3])
            if izq is None or der is None:
                return None
            try:
                if op == '+':
                    return izq + der
                if op == '-':
                    return izq - der
                if op == '*':
                    return izq * der
                if op == '/':
                    return float(izq) / float(der) if der != 0 else None
                if op == '//':
                    return izq // der if der != 0 else None
                if op == '%':
                    return izq % der if der != 0 else None
                if op == '**':
                    return izq ** der
                if op == '==':
                    return izq == der
                if op == '!=':
                    return izq != der
                if op == '<':
                    return izq < der
                if op == '>':
                    return izq > der
                if op == '<=':
                    return izq <= der
                if op == '>=':
                    return izq >= der
                if op == 'and':
                    return izq and der
                if op == 'or':
                    return izq or der
            except Exception:
                return None

        # call, read y otros nodos no se pueden evaluar en compilación
        return None

    @staticmethod
    def _tipos_compatibles(destino: str, origen: str) -> bool:
        # 'any' es el tipo de retorno de funciones (tipo desconocido en compilacion)
        # se acepta en cualquier contexto
        if origen == 'any' or destino == 'any':
            return True
        if destino == origen:
            return True
        if destino == 'float' and origen == 'int':
            return True
        return False

    @staticmethod
    def _comparables(izq: str, der: str) -> bool:
        if 'any' in (izq, der):
            return True
        if izq == der:
            return True
        if izq in ('int', 'float') and der in ('int', 'float'):
            return True
        return False
