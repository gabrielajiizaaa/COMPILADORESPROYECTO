from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class FuncionInfo:
    nombre: str
    parametros: List[Tuple[str, str]]


class TablaSimbolos:
    def __init__(self):
        self._ambitos: List[Dict[str, str]] = [{}]

    def entrar_ambito(self):
        self._ambitos.append({})

    def salir_ambito(self):
        if len(self._ambitos) > 1:
            self._ambitos.pop()

    def declarar(self, nombre: str, tipo: str) -> bool:
        ambito = self._ambitos[-1]
        if nombre in ambito:
            return False
        ambito[nombre] = tipo
        return True

    def buscar(self, nombre: str) -> Optional[str]:
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None


class AnalizadorSemantico:
    def __init__(self):
        self.errores: List[str] = []
        self.variables = TablaSimbolos()
        self.funciones: Dict[str, FuncionInfo] = {}
        self._funcion_actual: Optional[str] = None

    def analizar(self, arbol) -> List[str]:
        if not arbol or arbol[0] != 'programa':
            self.errores.append("Arbol sintactico invalido o vacio")
            return self.errores

        for sentencia in arbol[1]:
            self._analizar_sentencia(sentencia)
        return self.errores

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
            self._tipo_expr(sentencia[1])
        elif tipo == 'read':
            nombre = sentencia[1]
            if self.variables.buscar(nombre) is None:
                self.errores.append(f"Variable no declarada en read: '{nombre}'")
        elif tipo == 'call_stmt':
            self._tipo_expr(('call', sentencia[1], sentencia[2]))
        else:
            self.errores.append(f"Sentencia no soportada en fase 3: {tipo}")

    def _analizar_bloque(self, bloque):
        if not bloque or bloque[0] != 'bloque':
            self.errores.append("Bloque invalido")
            return

        self.variables.entrar_ambito()
        for sentencia in bloque[1]:
            self._analizar_sentencia(sentencia)
        self.variables.salir_ambito()

    def _analizar_declaracion(self, sentencia):
        _, tipo_decl, nombre, expr = sentencia
        if not self.variables.declarar(nombre, tipo_decl):
            self.errores.append(f"Variable redeclarada en el mismo ambito: '{nombre}'")
            return

        if expr is not None:
            tipo_expr = self._tipo_expr(expr)
            if not self._tipos_compatibles(tipo_decl, tipo_expr):
                self.errores.append(
                    f"Asignacion incompatible en declaracion de '{nombre}': {tipo_decl} <- {tipo_expr}"
                )

    def _analizar_asignacion(self, sentencia):
        _, nombre, operador, expr = sentencia
        tipo_var = self.variables.buscar(nombre)
        if tipo_var is None:
            self.errores.append(f"Variable no declarada: '{nombre}'")
            return

        tipo_expr = self._tipo_expr(expr)
        if operador == '=':
            if not self._tipos_compatibles(tipo_var, tipo_expr):
                self.errores.append(
                    f"Asignacion incompatible en '{nombre}': {tipo_var} <- {tipo_expr}"
                )
            return

        if operador in ('+=', '-=', '*=', '/='):
            if tipo_var not in ('int', 'float') or tipo_expr not in ('int', 'float'):
                self.errores.append(
                    f"Operador {operador} requiere tipos numericos en '{nombre}'"
                )

    def _analizar_if(self, sentencia):
        _, condicion, bloque_then, bloque_else = sentencia
        tipo_cond = self._tipo_expr(condicion)
        if tipo_cond != 'bool':
            self.errores.append(f"Condicion de if debe ser bool, no {tipo_cond}")

        self._analizar_bloque(bloque_then)
        if bloque_else is not None:
            self._analizar_bloque(bloque_else)

    def _analizar_while(self, sentencia):
        _, condicion, bloque = sentencia
        tipo_cond = self._tipo_expr(condicion)
        if tipo_cond != 'bool':
            self.errores.append(f"Condicion de while debe ser bool, no {tipo_cond}")
        self._analizar_bloque(bloque)

    def _analizar_funcion(self, sentencia):
        _, nombre, parametros, bloque = sentencia
        if nombre in self.funciones:
            self.errores.append(f"Funcion redeclarada: '{nombre}'")
            return

        self.funciones[nombre] = FuncionInfo(nombre=nombre, parametros=parametros)

        anterior = self._funcion_actual
        self._funcion_actual = nombre

        self.variables.entrar_ambito()
        for tipo_param, nombre_param in parametros:
            if not self.variables.declarar(nombre_param, tipo_param):
                self.errores.append(
                    f"Parametro duplicado '{nombre_param}' en funcion '{nombre}'"
                )

        for st in bloque[1]:
            self._analizar_sentencia(st)

        self.variables.salir_ambito()
        self._funcion_actual = anterior

    def _analizar_return(self, sentencia):
        _, expr = sentencia
        if self._funcion_actual is None:
            self.errores.append("return fuera de una funcion")
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
            nombre = expr[1]
            tipo_var = self.variables.buscar(nombre)
            if tipo_var is None:
                self.errores.append(f"Variable no declarada: '{nombre}'")
                return 'error'
            return tipo_var

        if tag == 'call':
            nombre = expr[1]
            args = expr[2]
            info = self.funciones.get(nombre)
            if info is None:
                self.errores.append(f"Funcion no declarada: '{nombre}'")
                for arg in args:
                    self._tipo_expr(arg)
                return 'error'

            if len(args) != len(info.parametros):
                self.errores.append(
                    f"Cantidad de argumentos invalida en '{nombre}': {len(args)} != {len(info.parametros)}"
                )
            else:
                for idx, arg in enumerate(args):
                    tipo_arg = self._tipo_expr(arg)
                    tipo_param = info.parametros[idx][0]
                    if not self._tipos_compatibles(tipo_param, tipo_arg):
                        self.errores.append(
                            f"Tipo de argumento invalido en '{nombre}' posicion {idx + 1}: "
                            f"{tipo_param} <- {tipo_arg}"
                        )

            return 'any'

        if tag == 'unop':
            op = expr[1]
            tipo_rhs = self._tipo_expr(expr[2])

            if op == '-':
                if tipo_rhs not in ('int', 'float'):
                    self.errores.append(f"Operador unario '-' requiere numerico, no {tipo_rhs}")
                    return 'error'
                return tipo_rhs

            if op == 'not':
                if tipo_rhs != 'bool':
                    self.errores.append(f"Operador 'not' requiere bool, no {tipo_rhs}")
                    return 'error'
                return 'bool'

            self.errores.append(f"Operador unario no soportado: {op}")
            return 'error'

        if tag == 'binop':
            op = expr[1]
            izq = self._tipo_expr(expr[2])
            der = self._tipo_expr(expr[3])

            if op in ('+', '-', '*', '/', '%', '//', '**'):
                if op == '+' and izq == 'string' and der == 'string':
                    return 'string'
                if izq not in ('int', 'float') or der not in ('int', 'float'):
                    self.errores.append(
                        f"Operador '{op}' requiere operandos numericos (o string+string), no {izq} y {der}"
                    )
                    return 'error'
                if op == '/':
                    return 'float'
                return 'float' if 'float' in (izq, der) else 'int'

            if op in ('==', '!=', '<', '>', '<=', '>='):
                if not self._comparables(izq, der):
                    self.errores.append(
                        f"Comparacion invalida entre tipos {izq} y {der}"
                    )
                return 'bool'

            if op in ('and', 'or'):
                if izq != 'bool' or der != 'bool':
                    self.errores.append(
                        f"Operador logico '{op}' requiere bool y bool, no {izq} y {der}"
                    )
                    return 'error'
                return 'bool'

            self.errores.append(f"Operador binario no soportado: {op}")
            return 'error'

        self.errores.append(f"Nodo de expresion no soportado: {tag}")
        return 'error'

    @staticmethod
    def _tipos_compatibles(destino: str, origen: str) -> bool:
        if destino == origen:
            return True
        if destino == 'float' and origen == 'int':
            return True
        return False

    @staticmethod
    def _comparables(izq: str, der: str) -> bool:
        if izq == der:
            return True
        if izq in ('int', 'float') and der in ('int', 'float'):
            return True
        return False
