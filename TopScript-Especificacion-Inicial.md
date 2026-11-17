# TopScript
## Especificación inicial del lenguaje y plan de desarrollo

**Proyecto de Lenguajes y Autómatas II**  
**Ingeniería en Sistemas Computacionales — Instituto Tecnológico de Oaxaca**  
**Versión de trabajo: 1.0**

## 1. Resumen

TopScript será un lenguaje de dominio específico (DSL) para describir un presupuesto personal por categorías y registrar gastos. El usuario escribirá un archivo `.top`; un intérprete construido en Python leerá ese archivo, comprobará su sintaxis y sus reglas, sumará los gastos y mostrará un reporte. Si el gasto de una categoría supera su límite, el intérprete emitirá una alerta.

El proyecto tiene dos lenguajes distintos: **Python** es el lenguaje de implementación y **TopScript** es el lenguaje que diseñará el equipo. La primera entrega funcional será un intérprete de consola. Una interfaz web puede añadirse después como una forma más cómoda de escribir y ejecutar archivos TopScript, pero no reemplaza el diseño ni el procesamiento del lenguaje.

## 2. Problema que se busca atender

Una persona puede definir cuánto quiere gastar en distintas categorías, pero llevar el registro manualmente dificulta saber cuánto ha gastado y detectar a tiempo cuándo supera un límite. TopScript propone expresar el presupuesto y sus gastos en un archivo sencillo que un programa pueda procesar y resumir automáticamente.

El proyecto es académico y demostrativo. En su primera versión no se conectará a cuentas bancarias ni enviará notificaciones externas; mostrará resultados y alertas en la consola.

## 3. Objetivos

### Objetivo general

Diseñar e implementar un lenguaje pequeño que permita declarar categorías de presupuesto, registrar gastos y obtener un reporte automático de los límites y totales.

### Objetivos específicos

- Definir los tokens, la gramática y las reglas semánticas de TopScript.
- Implementar en Python un analizador léxico que convierta el texto fuente en tokens con ubicación de línea y columna.
- Implementar un analizador sintáctico que verifique la estructura del programa.
- Validar reglas del dominio, como límites positivos y gastos declarados dentro de una categoría.
- Ejecutar un programa válido, acumular gastos por categoría y mostrar alertas cuando se excedan los límites.
- Informar errores léxicos, sintácticos y semánticos de forma comprensible.

## 4. Alcance de la primera versión

La primera versión incluirá:

- Un presupuesto por archivo.
- Categorías con nombre y límite monetario.
- Uno o más gastos dentro de cada categoría, con cantidad y descripción.
- Suma de gastos por categoría.
- Reporte de límite, total gastado y saldo de cada categoría.
- Alerta cuando el total gastado sea mayor que el límite.
- Errores con número de línea y explicación breve.
- Montos en pesos mexicanos (MXN), escritos con punto decimal y hasta dos cifras decimales.

Quedan para una versión futura: interfaz web, conexión bancaria, usuarios y cuentas, persistencia en base de datos, ciclos, condicionales, variables generales, funciones, optimización de código y generación de tripletas. No son necesarios para demostrar que existe un lenguaje que se analiza y ejecuta.

## 5. Sintaxis propuesta

Un archivo TopScript contiene la palabra `presupuesto`, un nombre entre comillas y un bloque. Dentro se declaran categorías. Cada categoría tiene un límite y contiene gastos.

```topscript
presupuesto "Octubre" {
  categoria comida limite 1000.00 {
    gasto 450.50 descripcion "Supermercado";
    gasto 120.00 descripcion "Comida corrida";
  }

  categoria transporte limite 600.00 {
    gasto 80.00 descripcion "Autobus";
  }
}
```

Las palabras clave se escriben en minúsculas y sin acentos. Los nombres de categoría distinguen mayúsculas de minúsculas. Los montos son positivos o cero; los límites deben ser mayores que cero. Cada gasto termina en punto y coma.

## 6. Resultado esperado del ejemplo

Al ejecutar el ejemplo, TopScript debe mostrar un reporte equivalente a:

```text
Presupuesto: Octubre

comida       Limite: $1000.00   Gastado: $570.50   Disponible: $429.50
transporte   Limite: $600.00    Gastado: $80.00    Disponible: $520.00

Estado: dentro de los limites en todas las categorias.
```

Si los gastos de una categoría exceden el límite, se muestra una alerta para esa categoría. Por ejemplo, si comida suma $1050.00, el reporte debe indicar que excedió su límite por $50.00. El exceso se calcula como `gastado - limite`; el disponible se calcula como `limite - gastado` y puede ser negativo cuando hay exceso.

## 7. Gramática de la versión 1.0

La siguiente gramática EBNF describe únicamente las construcciones incluidas en el alcance inicial:

```ebnf
programa       = "presupuesto", CADENA, "{", categoria, { categoria }, "}" ;
categoria      = "categoria", IDENTIFICADOR, "limite", MONTO,
                 "{", gasto, { gasto }, "}" ;
gasto          = "gasto", MONTO, "descripcion", CADENA, ";" ;

CADENA         = comilla_doble, { caracter_sin_comilla }, comilla_doble ;
IDENTIFICADOR  = letra_o_guion_bajo, { letra_digito_o_guion_bajo } ;
MONTO          = digitos, [ ".", digito, [ digito ] ] ;
```

Los espacios, tabulaciones y saltos de línea separan tokens y no cambian el significado. Los comentarios comienzan con `//` y terminan al final de la línea. Los comentarios pueden aparecer entre instrucciones.

En esta versión no hay expresiones aritméticas escritas por el usuario: cada gasto y límite es un monto literal. Esto mantiene la primera gramática pequeña y permite concentrarse en el análisis del lenguaje. El programa sí realiza internamente las sumas necesarias.

## 8. Componentes léxicos

| Token | Forma / ejemplo | Descripción |
|---|---|---|
| PRESUPUESTO | `presupuesto` | Inicio del programa |
| CATEGORIA | `categoria` | Inicio de una categoría |
| LIMITE | `limite` | Introduce el monto máximo |
| GASTO | `gasto` | Introduce un gasto |
| DESCRIPCION | `descripcion` | Introduce la descripción del gasto |
| IDENTIFICADOR | `comida`, `_ocio2` | Nombre de categoría |
| MONTO | `450`, `450.5`, `450.50` | Cantidad no negativa, con máximo dos decimales |
| CADENA | `"Octubre"` | Texto entre comillas dobles |
| LLAVE_IZQ / LLAVE_DER | `{` / `}` | Delimitan bloques |
| PUNTO_COMA | `;` | Termina un gasto |
| COMENTARIO | `// gastos de octubre` | Ignorado hasta el fin de línea |

Las palabras reservadas no pueden usarse como identificadores. Se recomienda que el lexer conserve línea y columna de cada token para que los errores indiquen dónde ocurrió el problema.

## 9. Reglas semánticas

La sintaxis define la forma; las reglas semánticas definen qué significa y qué datos son válidos.

1. Cada archivo contiene exactamente un programa y un nombre de presupuesto no vacío.
2. El programa debe declarar al menos una categoría.
3. Cada categoría tiene un nombre único dentro del presupuesto.
4. El límite de cada categoría debe ser mayor que cero.
5. Cada gasto pertenece a la categoría dentro de cuyo bloque aparece.
6. Los montos de gasto no pueden ser negativos y pueden ser cero.
7. Cada categoría debe incluir al menos un gasto en esta versión inicial.
8. Los montos se procesan como valores decimales exactos de centavos; no se deben sumar usando punto flotante binario sin control de redondeo. En Python se recomienda `Decimal`.
9. `gastado` es la suma de los montos de todos los gastos de la categoría.
10. Si `gastado > limite`, la categoría está excedida. Si `gastado == limite`, está en el límite y no excedida.
11. El orden de las categorías y de los gastos se conserva en el reporte.

No se necesitan conversiones entre entero y decimal, tabla de variables ni reglas de tipos para esta versión, porque no hay expresiones ni variables definidas por el usuario. Esto elimina la contradicción de la propuesta anterior sobre conversiones.

## 10. Arquitectura del intérprete

El procesamiento seguirá este flujo:

```text
archivo .top
    -> analizador léxico (texto a tokens)
    -> analizador sintáctico (tokens a estructura del programa)
    -> validación semántica (reglas del presupuesto)
    -> intérprete (sumas y comparación de límites)
    -> reporte y alertas en consola
```

Módulos sugeridos:

- `lexer.py`: reconoce palabras clave, montos, cadenas, identificadores, símbolos y comentarios.
- `parser.py`: valida la gramática y construye una estructura de datos del programa.
- `modelos.py`: representa presupuesto, categoría y gasto.
- `semantica.py`: valida nombres y montos.
- `interprete.py`: suma gastos, calcula disponibles y determina excesos.
- `errores.py`: define o formatea errores con línea y columna.
- `main.py`: recibe el nombre del archivo `.top`, conecta las etapas y muestra el resultado.
- `ejemplos/`: contiene archivos `.top` de demostración.

Para que el equipo entienda y pueda explicar cada etapa, se recomienda comenzar con un lexer propio y un parser de descenso recursivo en Python. Si la asignatura exige una herramienta generadora, pueden implementar la misma gramática con PLY; la definición de TopScript no debe cambiar por elegir una u otra técnica.

## 11. Errores que debe detectar el prototipo

- Carácter no reconocido, como `$` dentro del código fuente.
- Falta de una llave de cierre.
- Falta de punto y coma después de un gasto.
- Palabra clave o monto en una posición no permitida.
- Nombre de categoría duplicado.
- Límite igual a cero o negativo.
- Gasto negativo.
- Categoría sin gastos.
- Archivo vacío o sin bloque de presupuesto.

Ejemplo de mensaje claro:

```text
Error sintactico en linea 4, columna 5: se esperaba ';' al final del gasto.
```

## 12. Plan de trabajo recomendado

### Paso 1 — Cerrar la especificación

Acordar que el alcance v1 será el descrito aquí. Revisar que el equipo y el docente acepten el alcance del proyecto y si requieren PLY, descenso recursivo, código intermedio u otros temas específicos.

### Paso 2 — Preparar ejemplos

Guardar el ejemplo válido de la sección 5 como `ejemplos/octubre.top`. Crear ejemplos pequeños inválidos para cada tipo de error de la sección 11. Definir de antemano qué salida se espera.

### Paso 3 — Implementar el lexer

Leer caracteres, producir tokens y conservar ubicación. Primero comprobar visualmente la lista de tokens del ejemplo.

### Paso 4 — Implementar el parser

Consumir los tokens según la gramática. Si el archivo es válido, producir una estructura de presupuesto; si no, reportar el primer error con su ubicación.

### Paso 5 — Validar semántica

Comprobar nombres únicos y restricciones de montos. No ejecutar programas que no pasen la validación.

### Paso 6 — Interpretar y reportar

Calcular totales, saldos y excesos. Mostrar un reporte ordenado y legible.

### Paso 7 — Preparar demostración

Ejecutar un presupuesto dentro del límite y otro que lo exceda. Mostrar también un error sintáctico y explicar cómo viaja el programa por las etapas del intérprete.

## 13. Criterio de terminado de la versión inicial

La versión inicial está lista cuando el equipo puede ejecutar un archivo `.top` válido desde Python, obtener un reporte correcto para cada categoría y recibir errores comprensibles para entradas inválidas. En la exposición, cada integrante debe poder explicar el propósito del lexer, parser, validación semántica e intérprete.

## 14. Decisiones corregidas respecto al borrador

- Se distingue explícitamente TopScript (lenguaje diseñado) de Python (lenguaje de implementación).
- Se reduce el alcance a una DSL de presupuestos ejecutable; la página web queda como interfaz futura.
- Se posponen ciclos, condicionales, variables, árboles de expresiones, conversiones, optimizaciones, tripletas y cuádruplos hasta que exista una primera versión funcional.
- Se elimina la contradicción entre las reglas de conversión numérica: no aplican porque v1 no incluye expresiones ni variables.
- Se define de forma consistente dónde se permite un gasto y cómo se suma.
- Se aclara qué significa exceder el límite y qué salida se espera.
- Se evitan afirmaciones no demostradas sobre las limitaciones de todas las aplicaciones financieras existentes; el valor del proyecto se centra en diseñar y procesar un lenguaje específico.
