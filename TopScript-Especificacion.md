# TopScript
## Especificación del lenguaje, semántica e implementación

**Proyecto Integrador — Lenguajes y Autómatas II**  
**Ingeniería en Sistemas Computacionales**  
**Instituto Tecnológico de Oaxaca**  
**Equipo:** Griselda Itzel Juárez Monjaraz, Jorge Emilio Núñez Reyes, Omar Rutilio Valencia Borja y Gael Velasquez Cruz  
**Docente:** Maricarmen Montserrat Velazquez Hernández  
**Versión:** 1.0 — especificación alineada con el prototipo en Python

## Resumen

TopScript es un lenguaje de dominio específico para describir presupuestos personales, registrar gastos por categoría y expresar reglas sencillas de cálculo y control. La persona escribe un archivo de texto `.top`; un compilador pequeño escrito en Python lo convierte en cuádruplos y una máquina virtual ejecuta esa representación intermedia. El programa presenta los totales, saldos y alertas en la consola.

Python es el lenguaje de implementación. TopScript es el lenguaje diseñado por el equipo. Una interfaz web puede añadirse en otra etapa para editar y ejecutar archivos, pero no forma parte del núcleo requerido para demostrar el diseño de un lenguaje.

## 1. Problema, justificación y objetivos

### 1.1 Planteamiento del problema

Llevar presupuestos personales con notas o cálculos manuales dificulta reunir los gastos de cada categoría y reconocer rápidamente cuándo se superó un límite. El proyecto explora una forma de describir categorías, límites y gastos mediante instrucciones propias que un intérprete pueda revisar y ejecutar.

### 1.2 Justificación

El problema ofrece un contexto concreto para estudiar cómo un lenguaje transforma texto en acciones. El equipo define tokens y gramática, construye un árbol de sintaxis, comprueba tipos y ámbitos, genera una representación intermedia y ejecuta sus instrucciones. El valor académico está en hacer explícitas y demostrables esas etapas; no se afirma que TopScript sustituya a una aplicación financiera ni se conecta a datos bancarios.

### 1.3 Objetivo general

Diseñar e implementar un lenguaje pequeño para declarar presupuestos, registrar gastos por categoría y generar un reporte, usando análisis léxico, sintáctico y semántico, generación de cuádruplos e interpretación.

### 1.4 Objetivos específicos

- Especificar el alfabeto, los tokens, la gramática, la precedencia y las reglas de tipos.
- Implementar un lexer que indique línea y columna de cada token.
- Implementar un parser de descenso recursivo que construya un AST.
- Validar declaraciones, tipos, ámbitos y restricciones presupuestarias.
- Generar y ejecutar cuádruplos, incluidos saltos para selección e iteración.
- Aplicar optimizaciones locales seguras y poder comparar el código intermedio.
- Reportar errores léxicos, sintácticos, semánticos y de ejecución con ubicación.

## 2. Definición del lenguaje y alcance

TopScript v1.0 es un lenguaje interpretado, imperativo y de dominio específico. Cada archivo contiene un programa `presupuesto` con declaraciones, categorías, gastos, asignaciones, acciones y estructuras de control.

### 2.1 Funciones de v1.0

- Tipos `entero`, `decimal`, `texto` y `logico`.
- Variables con inicialización obligatoria y asignación posterior.
- Categorías con límite y gastos asociados.
- Lectura de atributos de categoría: `limite`, `gastado` y `nombre`.
- Aritmética, comparación, igualdad y operadores lógicos.
- `si`/`sino`, `mientras` y `para (cada ... en presupuesto)`.
- `mostrar(...)` y `alerta(...)` en consola.
- AST, tabla de símbolos, tipado estático y cuádruplos ejecutables.
- Plegado de constantes e identidades algebraicas con `--optimizar`.

### 2.2 Límites deliberados

Un archivo contiene un solo presupuesto; las categorías se declaran directamente dentro de él y no se anidan. Un gasto solo es válido dentro del bloque de una categoría. Los atributos de categoría son de solo lectura. No hay funciones definidas por el usuario, arreglos, entrada interactiva, persistencia, conexión bancaria ni interfaz gráfica. La ejecución se limita a un millón de pasos para detener ciclos accidentales que no terminan.

Los comentarios, archivos y errores están pensados para uso académico local. El intérprete no representa asesoría financiera ni ofrece seguridad o almacenamiento de una aplicación de producción.

## 3. Ejemplo canónico

```topscript
// Presupuesto de ejemplo en pesos mexicanos
presupuesto "Octubre" {
  decimal ingreso = 5000.00;
  logico avisar = verdadero;

  categoria comida limite ingreso * 0.20 {
    gasto 450.50 descripcion "Supermercado";
    gasto 120 descripcion "Comida corrida";
  }

  categoria transporte limite 600.00 {
    gasto 80 descripcion "Autobus";
  }

  mostrar("Gasto en comida:");
  mostrar(comida.gastado);

  si (comida.gastado > comida.limite y avisar) {
    alerta("Se excedio el presupuesto de comida");
  } sino {
    mostrar("Comida se mantiene dentro del limite");
  }

  para (cada cat en presupuesto) {
    mostrar(cat.nombre);
    mostrar(cat.gastado);
  }
}
```

El intérprete procesa declaraciones y categorías en orden. `comida.gastado` vale 570.50; su límite se calcula como 20 % de 5000.00, es decir 1000.00. Por ello no se activa la alerta. Al terminar, el reporte incluye límite, total, disponible y estado de cada categoría.

## 4. Reglas léxicas

El lexer lee caracteres de izquierda a derecha, reconoce el token más largo aplicable y registra su posición inicial. Los espacios, tabulaciones y saltos de línea separan tokens y se ignoran salvo para actualizar la ubicación. Las palabras clave se escriben en minúsculas y sin acentos; los identificadores distinguen mayúsculas y minúsculas.

### 4.1 Alfabeto y formas

| Elemento | Regla | Ejemplo |
|---|---|---|
| Identificador | Inicia con letra Unicode o `_`; continúa con letras, dígitos o `_` | `comida`, `_cat2` |
| Entero | Uno o más dígitos ASCII | `0`, `120` |
| Decimal | Dígitos, punto y uno o dos dígitos | `0.20`, `450.5`, `600.00` |
| Cadena | Texto entre comillas dobles; no contiene salto de línea literal | `"Octubre"` |
| Escape | `\"`, `\\`, `\n`, `\t` dentro de cadenas | `"Comida \"rapida\""` |
| Comentario | `//` hasta el fin de línea | `// gasto del mes` |

Un signo negativo no forma parte del token numérico: se analiza como operador unario `-`. Esto permite usar negativos en cálculos, pero la semántica prohíbe límites no positivos y la ejecución prohíbe registrar gastos negativos. No se admite notación científica ni separador de miles en el código fuente.

### 4.2 Tokens

| Token | Lexemas / ejemplo |
|---|---|
| Palabras reservadas | `presupuesto categoria limite gasto descripcion si sino mientras para cada en entero decimal texto logico verdadero falso y o no alerta mostrar` |
| Literales | `ENTERO_LITERAL`, `DECIMAL_LITERAL`, `CADENA`, `verdadero`, `falso` |
| Identificador | `IDENTIFICADOR` |
| Delimitadores | `{ } ( ) ; .` |
| Aritméticos | `+ - * /` |
| Asignación y comparación | `= == != < > <= >=` |

Las palabras reservadas siempre producen su token dedicado y no pueden declararse como identificadores. Por ejemplo, `limite` es token reservado, aunque aparece como nombre de atributo después de `.`.

## 5. Gramática

La notación EBNF usa `{ X }` para cero o más repeticiones, `[ X ]` para una parte opcional y `|` para alternativas. Los terminales se escriben entre comillas o en mayúsculas.

```ebnf
programa       = "presupuesto", CADENA, bloque, EOF ;
bloque         = "{", { instruccion }, "}" ;
instruccion    = declaracion | asignacion | categoria | gasto
               | condicional | ciclo_mientras | ciclo_para
               | accion | bloque ;

declaracion    = tipo, IDENTIFICADOR, "=", expresion, ";" ;
tipo           = "entero" | "decimal" | "texto" | "logico" ;
asignacion     = IDENTIFICADOR, "=", expresion, ";" ;
categoria      = "categoria", IDENTIFICADOR, "limite", expresion, bloque ;
gasto          = "gasto", expresion, "descripcion", expresion, ";" ;
condicional    = "si", "(", expresion, ")", bloque, [ "sino", bloque ] ;
ciclo_mientras = "mientras", "(", expresion, ")", bloque ;
ciclo_para     = "para", "(", "cada", IDENTIFICADOR, "en", "presupuesto", ")", bloque ;
accion         = ( "mostrar" | "alerta" ), "(", expresion, ")", ";" ;

expresion      = expresion_o ;
expresion_o    = expresion_y, { "o", expresion_y } ;
expresion_y    = expresion_no, { "y", expresion_no } ;
expresion_no   = "no", expresion_no | comparacion ;
comparacion    = aritmetica, [ operador_relacional, aritmetica ] ;
operador_relacional = "<" | ">" | "<=" | ">=" | "==" | "!=" ;
aritmetica     = termino, { ( "+" | "-" ), termino } ;
termino        = unaria, { ( "*" | "/" ), unaria } ;
unaria         = "-", unaria | primaria ;
primaria       = ENTERO_LITERAL | DECIMAL_LITERAL | CADENA
               | "verdadero" | "falso"
               | IDENTIFICADOR, [ ".", atributo ]
               | "(", expresion, ")" ;
atributo       = IDENTIFICADOR | "limite" ;
```

La gramática permite que una categoría aparezca como instrucción en el árbol sintáctico; la regla semántica adicional exige que se declare directamente dentro del bloque del presupuesto, nunca dentro de otra categoría, condicional o ciclo. Un programa válido contiene al menos una categoría. Cada categoría contiene al menos una instrucción `gasto` en algún punto de su cuerpo. Las expresiones no aceptan una cadena de comparaciones como `a < b < c`; se deben combinar comparaciones con `y` u `o`.

### 5.1 Precedencia y asociatividad

De mayor a menor precedencia:

| Nivel | Operadores | Asociatividad | Regla |
|---:|---|---|---|
| 1 | `-` unario | Derecha | Niega un número |
| 2 | `*`, `/` | Izquierda | Multiplicación y división |
| 3 | `+`, `-` binarios | Izquierda | Suma, resta o concatenación de textos con `+` |
| 4 | `<`, `>`, `<=`, `>=`, `==`, `!=` | No asociativa | Produce un lógico; máximo una comparación seguida |
| 5 | `no` | Derecha | Negación lógica |
| 6 | `y` | Izquierda | Conjunción lógica |
| 7 | `o` | Izquierda | Disyunción lógica |

Los paréntesis pueden cambiar el agrupamiento. `y` y `o` evalúan ambos operandos; no hay cortocircuito. Las expresiones no tienen efectos laterales, por lo que el resultado lógico no depende de omitir una evaluación.

## 6. Tipos y reglas semánticas

### 6.1 Tipos

| Tipo | Valores | Uso |
|---|---|---|
| `entero` | Enteros de precisión arbitraria de Python | Contadores y cantidades sin fracciones |
| `decimal` | `Decimal` de base diez | Límites, gastos y operaciones con fracciones |
| `texto` | Cadenas Unicode | Nombres, descripciones y mensajes |
| `logico` | `verdadero`, `falso` | Condiciones y operadores lógicos |
| `categoria` | Referencia interna a una categoría | Solo alias y acceso a atributos |

Los montos de dinero se escriben con hasta dos decimales. El intérprete conserva los valores con aritmética decimal; el reporte los muestra con dos decimales. Los resultados de división pueden tener más de dos cifras internamente; el formato monetario redondea solo al presentarlos.

### 6.2 Compatibilidad de asignación

La inicialización es obligatoria. Se permite asignar `entero` a `decimal` con promoción automática `INT_TO_DEC`. No se permite asignar `decimal` a `entero`, pues ello descartaría fracciones. Los demás tipos requieren coincidencia exacta. Las categorías y los alias no se reasignan.

```topscript
entero intentos = 3;
decimal limite = intentos;  // valido: promocion a decimal
// entero n = 3.5;           // error semantico
```

Una variable solo existe desde su punto de declaración hasta el final de su ámbito. No se permite usarla antes de declararla ni redeclarar el mismo nombre dentro del mismo ámbito; un ámbito interior puede ocultar un nombre exterior mientras exista.

### 6.3 Tabla de operadores

| Operador | Tipos de operandos | Tipo resultado / significado |
|---|---|---|
| `+`, `-`, `*` | Dos `entero` | `entero` |
| `+`, `-`, `*` | Combinación de `entero` y `decimal` | `decimal`; el entero se promueve |
| `/` | Dos tipos numéricos | `decimal`; división entre cero es error de ejecución |
| `+` | Dos `texto` | `texto`, concatenación |
| `<`, `>`, `<=`, `>=` | Dos tipos numéricos | `logico` |
| `==`, `!=` | Dos tipos numéricos o dos valores del mismo tipo `texto`/`logico` | `logico` |
| `y`, `o` | Dos `logico` | `logico` |
| `no` | Un `logico` | `logico` |
| `-` unario | Un tipo numérico | Conserva tipo |
| Cualquier otra combinación | — | Error semántico |

No existe conversión implícita a texto. Para imprimir un monto, se puede escribir `mostrar(categoria.gastado);` como valor independiente.

### 6.4 Reglas del dominio presupuestario

- Las categorías se procesan en orden de aparición y sus nombres son únicos en el presupuesto.
- El límite debe ser numérico y estrictamente mayor que cero; puede calcularse con una expresión.
- `gasto` solo se permite dentro de una categoría. Su monto debe ser numérico y no negativo en ejecución, y su descripción debe ser `texto`.
- Cada ejecución de `gasto` suma el monto al atributo de solo lectura `categoria.gastado` y conserva la descripción en el registro de ejecución.
- `categoria.limite`, `categoria.gastado` y `categoria.nombre` tienen tipos `decimal`, `decimal` y `texto`, respectivamente.
- Una categoría está excedida cuando `gastado > limite`; igualar el límite produce `AL LIMITE`, no exceso. `disponible = limite - gastado` puede ser negativo.
- `si` y `mientras` requieren una condición `logico`. `para (cada c en presupuesto)` asigna a `c` sucesivamente cada categoría creada antes de comenzar el ciclo.
- `mostrar` emite el valor; `alerta` emite el valor precedido por `ALERTA:`. Al terminar se imprime también el resumen automático.

## 7. Ámbitos, símbolos y AST

El parser construye un árbol de sintaxis abstracta (AST) con nodos para programa, bloque, declaración, asignación, categoría, gasto, condicional, ciclos, acción, literal, variable, atributo, operación unaria y operación binaria. Los nodos conservan línea y columna de su origen. Los paréntesis determinan el árbol, pero no requieren nodos propios.

La tabla de símbolos es una pila de diccionarios. El ámbito global contiene variables del presupuesto y nombres de categorías. Cada categoría abre un ámbito para sus variables locales; cada bloque de control abre otro ámbito; el alias de un ciclo `para` vive durante el cuerpo de ese ciclo. La búsqueda comienza en el ámbito actual y continúa hacia sus padres.

Cada símbolo registra nombre, clase (`variable`, `categoria` o `alias_categoria`), tipo, dirección interna, ámbito y línea de declaración. Las variables reciben direcciones únicas; los temporales (`t1`, `t2`, ...) almacenan resultados intermedios. El AST se analiza y se compila antes de ejecutar; un error semántico detiene todo el programa antes de producir efectos.

### 7.1 Reglas semánticas por producción

| Producción | Comprobación y acción |
|---|---|
| `tipo ID = expr ;` | `expr` debe ser asignable al tipo declarado; el nombre no debe existir en el ámbito; se inserta el símbolo y se emite `ASSIGN` (con `INT_TO_DEC` si corresponde) |
| `ID = expr ;` | `ID` debe estar declarado y ser variable; tipos compatibles; se emite `ASSIGN` |
| `categoria ID limite expr bloque` | Solo nivel superior; nombre único; límite numérico y positivo; se declara categoría, se abre ámbito y se compila su cuerpo |
| `gasto expr descripcion expr ;` | Debe existir categoría activa; monto numérico, descripción texto; se emite `EXPENSE` |
| `si (expr) bloque [sino bloque]` | Condición lógica; se emiten saltos y se resuelven destinos al conocer el final de cada bloque |
| `mientras (expr) bloque` | Condición lógica; el destino del salto final regresa al inicio de la condición |
| `para (cada ID en presupuesto) bloque` | Se crea un alias de tipo categoría y una secuencia de cuádruplos de inicialización y avance |
| `ID . atributo` | El símbolo debe ser categoría; atributo permitido y tipo de atributo válido |
| `mostrar(expr)` / `alerta(expr)` | Cualquier expresión de tipo escalar; se emite `PRINT` o `ALERT` |

## 8. Cuádruplos y ejecución

La representación intermedia elegida es exclusivamente **cuádruplos**: `(operador, argumento 1, argumento 2, resultado)`. Los operandos son referencias a variables/temporales o literales directos. En los operadores unarios se usa el primer argumento; en instrucciones de salida, categoría y gasto se usan solo los campos pertinentes. Para `GOTO` y `GOTOF`, el destino de salto se almacena en `resultado`.

### 8.1 Ejemplo de expresión

Para `restante = ingreso - (total + 50) * 2;`, suponiendo que los tres valores son decimales, una secuencia posible es:

```text
0001 (ADD, total, 50.0, t1)
0002 (MUL, t1, 2.0, t2)
0003 (SUB, ingreso, t2, t3)
0004 (ASSIGN, t3, _, restante)
```

Las operaciones se emiten en postorden: primero se calculan las subexpresiones y después el operador que las combina. Las conversiones de entero a decimal aparecen como `INT_TO_DEC` cuando el tipado lo requiere.

### 8.2 Saltos y backpatching

Un salto condicional se genera inicialmente con destino desconocido. El compilador conserva su índice en la lista; al conocer la dirección de la siguiente instrucción, completa el campo `resultado` (backpatching).

```text
GOTOF condicion, _, destino_sino
  ... bloque verdadero ...
GOTO _, _, destino_fin
 destino_sino: ... bloque sino ...
 destino_fin:
```

Para `mientras`, el destino del salto de regreso es el índice de la primera instrucción que evalúa la condición. `para` usa `ITER_INIT` para crear un cursor y `ITER_NEXT` para enlazar cada categoría al alias o saltar al final. Los destinos se cuentan desde cero en la máquina virtual; la impresión de cuádruplos numera las filas desde cero para que coincidan.

### 8.3 Conjunto de operaciones implementado

| Grupo | Operadores |
|---|---|
| Movimiento y conversión | `ASSIGN`, `INT_TO_DEC` |
| Aritmética / texto | `ADD`, `SUB`, `MUL`, `DIV`, `NEG`, `CONCAT` |
| Lógica y comparación | `NOT`, `AND`, `OR`, `LT`, `GT`, `LE`, `GE`, `EQ`, `NE` |
| Salto | `GOTO`, `GOTOF` |
| Categorías y gastos | `CATEGORY`, `ENTER_CATEGORY`, `EXIT_CATEGORY`, `EXPENSE`, `GET_ATTR` |
| Iteración | `ITER_INIT`, `ITER_NEXT` |
| Salida y control | `PRINT`, `ALERT`, `HALT` |

La máquina virtual mantiene una memoria de direcciones, un registro de categorías, la categoría activa y cursores de iteración. Una división entre cero, un gasto negativo, un límite evaluado como cero/negativo o el exceso del máximo de pasos produce un error de ejecución con la línea fuente.

### 8.4 Decisión sobre tripletas

La implementación y la especificación usan cuádruplos como única forma de código intermedio. No se prometen tripletas: tener dos representaciones paralelas duplicaría trabajo de generación, depuración y explicación sin aportar una función necesaria al intérprete. Si el docente exige comparar ambas, las tripletas pueden presentarse como extensión separada, no como salida actual del prototipo.

## 9. Optimización

La opción `--optimizar` ejecuta un optimizador local sobre los cuádruplos ya generados. Implementa:

1. **Plegado de constantes:** evalúa una operación cuando sus dos operandos son literales y la reemplaza por un `ASSIGN` del resultado. Si la operación no puede plegarse sin error (por ejemplo, división por cero), la deja para la máquina virtual.
2. **Identidades algebraicas:** `x + 0`, `x - 0`, `x * 1`, `x / 1` se reemplazan por una copia; `x * 0` se reemplaza por cero.

El optimizador conserva el número y los índices de las instrucciones, por lo que los saltos resueltos siguen siendo válidos. No implementa propagación global de constantes, eliminación de código muerto ni reordenamiento; esas técnicas quedan fuera de v1.0. Para la exposición se puede comparar el listado con y sin `--optimizar` y describir la operación que fue sustituida.

## 10. Errores

Todos los errores del lenguaje incluyen tipo y ubicación. Las categorías son:

| Clase | Ejemplos |
|---|---|
| Léxico | Carácter inválido, cadena sin cierre, escape desconocido, más de dos cifras decimales |
| Sintáctico | Token inesperado, falta de `;`, llave o paréntesis, comparación encadenada |
| Semántico | Variable no declarada, redeclaración, tipo incompatible, condición no lógica, gasto fuera de categoría, atributo inválido |
| De ejecución | División entre cero, gasto negativo calculado, límite calculado no positivo, ejecución mayor a un millón de pasos |

Ejemplos:

```text
Error lexico en linea 3, columna 12: caracter no reconocido: '$'
Error sintactico en linea 4, columna 5: se esperaba ';'; se encontro '}'
Error semantico en linea 6, columna 8: variable no declarada: 'ahorro'
Error de ejecucion en linea 10, columna 1: division entre cero
```

El parser se detiene en el primer error y no intenta recuperación de errores. La máquina virtual reporta la línea asociada al cuádruplo; la columna de ejecución se presenta como 1 porque la representación intermedia conserva línea, no columna. Los errores léxicos, sintácticos y semánticos sí conservan la columna precisa.

## 11. Arquitectura e implementación en Python

La implementación no necesita generadores ni bibliotecas externas. El lexer y el parser son propios para hacer visibles las decisiones del lenguaje y su relación con autómatas y gramáticas.

```text
fuente .top
   -> lexer.py       caracteres a tokens
   -> parser.py      tokens a AST
   -> compiler.py    análisis semántico y emisión de cuádruplos
   -> optimizador.py plegado local opcional
   -> runtime.py     máquina virtual y reporte
```

| Archivo | Responsabilidad |
|---|---|
| `lexer.py` | Tokens, literales, comentarios y ubicaciones |
| `parser.py` | Descenso recursivo, precedencia y AST |
| `ast_nodes.py` | Nodos del árbol abstracto |
| `symbol_table.py` | Declaraciones y ámbitos |
| `compiler.py` | Tipado estático, reglas del dominio y cuádruplos |
| `cuadruplos.py` | Tipos de operando, estructura y formato de IR |
| `optimizador.py` | Plegado de constantes e identidades |
| `runtime.py` | Máquina virtual, efectos de presupuesto y reporte |
| `errores.py` | Errores uniformes con ubicación |
| `main.py` | CLI y orquestación de etapas |
| `ejemplos/` | Programas demostrativos y entradas incorrectas |

## 12. Uso y demostración

Desde la terminal de Visual Studio Code, en la carpeta del proyecto:

```powershell
python main.py ejemplos/completo.top
python main.py ejemplos/completo.top --tokens --tabla-simbolos --cuadruplos
python main.py ejemplos/completo.top --optimizar --cuadruplos
python main.py ejemplos/errores/sintaxis.top
python main.py ejemplos/errores/semantica.top
```

Si Windows no encuentra `python`, se instala Python 3.10+ y se marca **Add Python to PATH** en el instalador; alternativamente se ejecuta con `py` cuando el lanzador está disponible. El programa no accede a red y no requiere paquetes pip.

### Orden sugerido para exposición

1. Mostrar el archivo fuente `.top` y explicar el problema que describe.
2. Mostrar tokens y ubicar un error léxico.
3. Explicar una producción de la gramática y enseñar el AST de una expresión.
4. Mostrar una fila de la tabla de símbolos y un error de tipos.
5. Recorrer los cuádruplos de una operación y de un `si` o `mientras`.
6. Ejecutar el programa, comparar optimización y explicar el reporte.

## 13. Criterios de aceptación de v1.0

La versión se considera completa cuando:

- Un programa válido puede tokenizarse, analizarse, compilarse y ejecutarse.
- Se implementa la gramática publicada y la tabla de precedencia coincide con el parser.
- Se validan ámbitos, declaraciones, tipos y restricciones de categoría.
- Los cuádruplos generados son entendidos por la máquina virtual, incluidos los saltos y ciclos.
- La optimización opcional produce el mismo resultado observable que el código sin optimizar.
- Los ejemplos válidos muestran el reporte y los ejemplos inválidos muestran errores con tipo y ubicación.
- La documentación, el código fuente y la demostración describen las mismas reglas.

## 14. Decisiones que eliminan contradicciones del borrador

- Se establece `entero -> decimal` como promoción válida; `decimal -> entero` se rechaza. La dirección opuesta a la del borrador evita pérdida de fracción.
- Se adopta una sola representación intermedia, cuádruplos; tripletas no son parte de la implementación.
- La gramática incluye todas las construcciones de v1.0 y las ordena con una sola precedencia coherente.
- `limite`, `gastado` y `nombre` son atributos de lectura; `gasto` es la única instrucción que modifica el total acumulado.
- Los gastos son declaraciones dentro del bloque de categoría; las variables del bloque tienen ámbitos explícitos.
- El signo menos es un operador, no parte del token numérico; validaciones de monto se separan entre análisis estático y ejecución.
- La salida es una alerta en consola, no una notificación automática del sistema operativo o una conexión bancaria.
- Se limita la optimización a lo realmente implementado; no se afirma que propagación, eliminación de código muerto o optimización avanzada ya existan.
- El texto evita comparaciones no sustentadas con productos financieros comerciales.

## Glosario

- **AST:** árbol que representa la estructura sintáctica y operadores del programa.
- **Ámbito:** región donde un nombre está declarado y puede usarse.
- **Cuádruplo:** instrucción intermedia con operador, dos argumentos y resultado.
- **DSL:** lenguaje diseñado para un dominio acotado; aquí, presupuestos personales.
- **Lexer:** analizador léxico que convierte caracteres en tokens.
- **Parser:** analizador sintáctico que comprueba la gramática y construye el AST.
- **Semántica:** reglas de tipos, ámbitos y significado de las instrucciones.
- **Backpatching:** completar destinos de salto cuando se conocen durante la generación de código.
- **Máquina virtual:** programa que ejecuta la lista de cuádruplos.
