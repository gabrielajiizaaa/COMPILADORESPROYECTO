MiniLango - FASE 1 - ANALISIS LEXICO :D

GABRIEL ALEJANDRO AJIN IZAGUIRRE - 1184924
DIEGO ALEJANDRO SOTO MEJIA - 1044424


## Expresiones Regulares
Estas son las reglas que definen cómo se ven cada tipo de token en MiniLang.
### Bases
N          = [0-9]+
L          = [A-Za-z]+

### Identificadores
ID         = [A-Za-z_][A-Za-z0-9_]{0,30}


### Números
NENTERO    = [0-9]+
NFLOAT     = [0-9]+\.[0-9]+

### Cadenas
CADENA     = "(?:\\.|[^"\\\n])*"  |  '(?:\\.|[^'\\\n])*'

### Booleanos
OBOOL      = true | false

### Operadores aritméticos
OSUM       = +
OREST      = -
OMULT      = *
ODIV       = /
OPOTENCIA  = **
ODIVENTER  = //
OPORCEN    = %

### Operadores de comparación
IQ         = ==
DQ         = !=
MQ         = >
MNQ        = <
MOIQ       = >=
MNOIQ      = <=

### Operadores de asignación
OASIG      = =
OMASIG     = +=
OMENOSIG   = -=
OMULTASIG  = *=
ODIVASIG   = /=

### Palabras reservadas
DTIPO      = int | float | bool | string
FTIPO      = if | else | while | func
ES         = read | write
RETORNO    = return

### Delimitadores
APARE      = (
CPARE      = )
ALLAVE     = {
CLLAVE     = }
ACORCH     = [
CCORCH     = ]
COMA       = ,
PCOMA      = ;
DPUNTO     = :
PUNTO      = .

### Espacios, saltos y comentarios
SLINEA     = [ \t]+
NLINEA     = \n
COMENT     = #[^\n]*

### Tabulacion - INDENT
INDENTAR    = aumento de nivel de indentacion
DESINDENTAR = disminucion de nivel de indentacion

## GRAMATICA

### Identificadores
ID          -->    letra ID'
ID'         -->    letra ID' | digito ID' | _ ID' | epsilon

### Palabras reservadas
FTIPO       -->    i f | w h i l e | f u n c | e l s e
DTIPO       -->    i n t | f l o a t | s t r i n g | b o o l
ES          -->    w r i t e | r e a d
RETORNO     -->    r e t u r n

### Literales numéricos
NENTERO     -->    digito NENTERO'
NENTERO'    -->    digito NENTERO' | epsilon

NFLOAT      -->    digito NENTERO' . digito NENTERO'

### Cadenas
CADENA      -->    " CADENA'
CADENA'     -->    caracter CADENA' | "
caracter    -->    cualquier char excepto " y \n *

### Booleanos
OBOOL       -->    t r u e | f a l s e

### Operadores de asignación
OASIG       -->    =
OMASIG      -->    + =
OMENOSIG    -->    - =
OMULTASIG   -->    * =
ODIVASIG    -->    / =

### Operadores aritméticos
OSUM        -->    +
OREST       -->    -
OMULT       -->    *
ODIV        -->    /
OPORCEN     -->    %
ODIVENTER   -->    / /
OPOTENCIA   -->    * *

### Operadores de comparación
IQ          -->    = =
DQ          -->    ! =
MNQ         -->    <
MQ          -->    >
MNOIQ       -->    < =
MOIQ        -->    > =

### Delimitadores
APARE       -->    (
CPARE       -->    )
DPUNTO      -->    :
COMA        -->    ,

### Nueva línea
NLINEA      -->    \n

### Indentación
INDENTAR    -->    espacio INDENTAR'
INDENTAR'   -->    espacio INDENTAR' | epsilon
DESINDENTAR -->    epsilon

espacio     -->    ' ' | \t


## Gramática Regular (GR)

PROGRAMA        -->    SENTENCIA PROGRAMA'
PROGRAMA'       -->    SENTENCIA PROGRAMA' | epsilon

SENTENCIA       -->    DTIPO DECL_R
                     | ID SENT_ID_R
                     | if SENT_IF_R
                     | while SENT_WHILE_R
                     | func SENT_FUNC_R
                     | return SENT_RET_R
                     | write SENT_WRITE_R
                     | read SENT_READ_R
                     | NLINEA SENTENCIA'

SENTENCIA'      -->    epsilon

DECL_R          -->    ID DECL_R'
DECL_R'         -->    NLINEA

SENT_ID_R       -->    OASIG ASIG_R
                     | OMASIG ASIG_R
                     | OMENOSIG ASIG_R
                     | OMULTASIG ASIG_R
                     | ODIVASIG ASIG_R
                     | APARE LLAMADA_R

ASIG_R          -->    EXPR ASIG_R'
ASIG_R'         -->    NLINEA

EXPR            -->    TERM EXPR'
EXPR'           -->    OSUM TERM EXPR'
                     | OREST TERM EXPR'
                     | OP_COMP TERM EXPR'
                     | epsilon

TERM            -->    FACTOR TERM'
TERM'           -->    OMULT FACTOR TERM'
                     | ODIV FACTOR TERM'
                     | OPORCEN FACTOR TERM'
                     | ODIVENTER FACTOR TERM'
                     | OPOTENCIA FACTOR TERM'
                     | epsilon

FACTOR          -->    OREST FACTOR
                     | APARE EXPR CPARE
                     | NENTERO
                     | NFLOAT
                     | CADENA
                     | true
                     | false
                     | ID FACTOR'

FACTOR'         -->    APARE LLAMADA_ARGS CPARE
                     | epsilon

LLAMADA_R       -->    ARGS_R CPARE NLINEA
LLAMADA_ARGS    -->    ARGS_R CPARE | epsilon

ARGS_R          -->    EXPR ARGS_R'
ARGS_R'         -->    COMA EXPR ARGS_R' | epsilon

SENT_IF_R       -->    EXPR DPUNTO NLINEA INDENTAR BLOQUE DESINDENTAR SENT_IF_R'
SENT_IF_R'      -->    else DPUNTO NLINEA INDENTAR BLOQUE DESINDENTAR
                     | epsilon

SENT_WHILE_R    -->    EXPR DPUNTO NLINEA INDENTAR BLOQUE DESINDENTAR

SENT_FUNC_R     -->    ID APARE PARAMS_R CPARE DPUNTO NLINEA INDENTAR BLOQUE DESINDENTAR

PARAMS_R        -->    DTIPO ID PARAMS_R'
                     | epsilon
PARAMS_R'       -->    COMA DTIPO ID PARAMS_R'
                     | epsilon

SENT_RET_R      -->    EXPR NLINEA

SENT_WRITE_R    -->    APARE EXPR CPARE NLINEA
SENT_READ_R     -->    APARE ID CPARE NLINEA

BLOQUE          -->    SENTENCIA BLOQUE'
BLOQUE'         -->    SENTENCIA BLOQUE' | epsilon



## Decisiones de diseño

**SIN RECURSIVIDAD A LA IZQUIERDA**
Las expresiones se dividen en niveles de precedencia.
Cada nivel llama al siguiente, nunca a sí mismo por la izquierda, lo que hace la gramática compatible con un parser descendente recursivo.

**IDENTACION**
El programa usa indentación para delimitar bloques. El lexer mantiene una pila de niveles — cuando el nivel sube emite INDENTAR, cuando baja emite DESINDENTAR. Esto elimina la necesidad de llaves o palabras clave de cierre.

**JERARQUIA DE OPERADORES**
Para aplicar la regla del token más largo posible. Si se revisara = antes que ==, el lexer rompería == en dos tokens de asignación separados. Al revisar primero los de dos caracteres se garantiza el match correcto.

**TOKEN NLINEA**
Porque en el programa el salto de línea indica el final de una sentencia. Sin él, la gramática no sabría dónde termina una instrucción y empieza la siguiente.

**FUNCION DE COMENTARIOS AL MOMENTO GENERAR ANALISI**
Los comentarios son útiles para el programador pero irrelevantes para el compilador. Se reconocen y se descartan, no generan tokens en el .out.



## Manejo de errores

El analizador nunca se detiene ante un error. Siempre va a seguir leyendo hasta el final del archivo.

- **Carácter no reconocido** — avanza un carácter y emite DESCONOCIDO.
        linea N, col M: ERROR carácter inesperado 'X'

- **Cadena sin cerrar** — recupera al fin de línea.
        linea N, col M: ERROR cadena sin cerrar antes de NUEVA_LINEA/FIN

- **Identificador mayor a 31 caracteres** — lo corta a 31 y sigue normalmente.
        linea N, col M: ERROR identificador demasiado largo (K caracteres); truncado a 31

- **Indentación inválida** — va al nivel inferior más cercano de la pila.
        linea N, col M: ERROR indentación inválida

- **Más de 5 niveles de indentación** — ignora el nuevo nivel y continúa.
        linea N, col M: ERROR máximo de niveles de indentación alcanzado

El archivo .out se genera siempre, incluso cuando hay errores.


## Pruebas

prueba1_hola_mundo.mlng  ---- write con cadena de texto
prueba2_aritmetica.mlng ---- Declaración de variables y operadores aritméticos
prueba3_condicional.mlng ---- read, if/else e indentación
prueba4_funciones.mlng ---- func, parámetros tipados y return
prueba5_while.mlng ---- Variables, read/write y bucle while
prueba_errores.mlng ---- Recuperación ante errores léxicos intencionales

