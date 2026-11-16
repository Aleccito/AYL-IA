# Validador de formatos con autómatas finitos

Proyecto de Teoría de la Computación / Lenguajes Formales. Valida cadenas de cinco formatos reales (correo, cédula panameña, IPv4, placa, teléfono) con **autómatas finitos deterministas (AFD)** y muestra **paso a paso** cómo el autómata acepta o rechaza la entrada.

## Conceptos aplicados
- **Expresión regular**: describe el lenguaje de cada formato. Se usa solo como *referencia* en las pruebas; **no decide** la validación.
- **AFD**: la decisión la toma `AFD.acepta()`. Una cadena es aceptada si, tras leerla completa, el autómata está en un estado de aceptación.
- **Clases de símbolo**: cada carácter se traduce a una clase (`DIGITO`, `LETRA`, `@`, `.`, `-`, `OTRO`, …) y la función de transición es δ(q, clase).
- La clase `AFD` (`automata.py`) es genérica y no conoce ningún formato.

## Requisitos e instalación
- Python 3.10 o superior (probado con 3.12). Solo librería estándar (`tkinter` viene con Python en Windows/macOS; en Linux puede requerir `python3-tk`).
- No hay nada que instalar.

```bash
cd validador
python main.py            # abre la interfaz
python -m unittest        # ejecuta las pruebas
```

## Estructura
```
validador/
├── automata.py      # clase AFD genérica
├── formatos.py      # regex + AFD + ejemplos de cada formato (FORMATOS)
├── simulador.py     # simular(afd, cadena) -> aceptada, traza, error
├── gui.py           # interfaz Tkinter
├── main.py          # punto de entrada
└── tests/test_formatos.py
```

## Datos de entrada
En la interfaz: **formato** (combo) y **cadena** (campo de texto). Botones: *Validar*, *Paso siguiente*, *Reiniciar*, *Ejemplo válido*, *Ejemplo inválido*.

| Formato | Regla | Válidos | Inválidos |
|---|---|---|---|
| Correo (base) | `usuario@dominio.ext`; usuario con letras, dígitos, `.`, `_`, `-`; dominio con letras, dígitos, `-` y al menos un `.` | `ana@correo.com`, `juan.perez@mail.example.pa` | `ana@`, `ana@correo`, `ana@@correo.com`, `ana@correo..com` |
| Cédula | Prefijo: provincia `1`–`13`, o `PE`, `E`, `N`; luego `-` 1–4 dígitos `-` 1–6 dígitos | `8-123-456`, `10-23-4567`, `PE-1-234`, `E-8-12345`, `N-12-345` | `0-1-1`, `14-1-1`, `X-1-1`, `8-123`, `pe-1-234` |
| IPv4 | 4 octetos 0–255 separados por `.`, sin ceros a la izquierda | `192.168.1.1`, `0.0.0.0`, `255.255.255.255` | `256.1.1.1`, `01.2.3.4`, `1.2.3`, `1.2.3.4.5` |
| Placa | 2 letras, `-` opcional, 4 dígitos | `AB1234`, `AB-1234` | `A1234`, `ABC123`, `AB12345`, `1234AB` |
| Teléfono | Fijo `NNN-NNNN` (primer dígito 2-5, 7-9) o celular `6NNN-NNNN` | `263-1234`, `6123-4567` | `163-1234`, `2631234`, `6123-456` |

> El formato de correo es una versión base; se ampliará más adelante.
> Supuestos propios: los formatos de placa y teléfono son simplificaciones de los reales.

## Procesamiento
1. Se parte del estado inicial.
2. Por cada símbolo se calcula su **clase** y se aplica δ(estado, clase).
3. Si no existe transición, se rechaza en esa posición (el motivo se muestra).
4. Al terminar la cadena, se acepta solo si el estado es de aceptación.

Notación de las tablas: `→` estado inicial, `*` estado de aceptación, `–` sin transición (rechazo).

### Correo
Regex: `[A-Za-z0-9._-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+`

| δ | - | . | @ | DIGITO | LETRA | _ |
|---|---|---|---|---|---|---|
| →q0 | u | u | – | u | u | u |
| u | u | u | a | u | u | u |
| a | d | – | – | d | d | – |
| d | d | p | – | d | d | – |
| p | e | – | – | e | e | – |
| *e | e | p | – | e | e | – |

### Cédula
Regex: `(?:1[0-3]|[1-9]|PE|E|N)-[0-9]{1,4}-[0-9]{1,6}`

Clases: `CERO`='0', `UNO`='1', `D2_3`='2','3', `D4_9`='4'…'9', `P`, `E`, `N`, `-`, `OTRO`.

| δ | - | CERO | D2_3 | D4_9 | E | N | P | UNO |
|---|---|---|---|---|---|---|---|---|
| →q0 | – | – | prov | prov | letra | letra | pe1 | p1 |
| p1 | g1 | prov | prov | – | – | – | – | prov |
| prov | g1 | – | – | – | – | – | – | – |
| pe1 | – | – | – | – | letra | – | – | – |
| letra | g1 | – | – | – | – | – | – | – |
| g1 | – | d1 | d1 | d1 | – | – | – | d1 |
| d1 | g2 | d2 | d2 | d2 | – | – | – | d2 |
| d2 | g2 | d3 | d3 | d3 | – | – | – | d3 |
| d3 | g2 | d4 | d4 | d4 | – | – | – | d4 |
| d4 | g2 | – | – | – | – | – | – | – |
| g2 | – | u1 | u1 | u1 | – | – | – | u1 |
| *u1…*u5 | – | u(k+1) | u(k+1) | u(k+1) | – | – | – | u(k+1) |
| *u6 | – | – | – | – | – | – | – | – |

### IPv4
Regex: `OCT(\.OCT){3}` con `OCT = 25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]?|0`

Clases: `C0`='0', `C1`='1', `C2`='2', `C3_4`, `C5`, `C6_9`, `.`, `OTRO`. El autómata repite 4 veces el mismo bloque de octeto (estados `S k, A k, B k, C k, E k, F k, G k`); en los octetos 1–3 un `.` desde cualquier estado completo lleva a `S(k+1)`. Tabla del octeto 1:

| δ | . | C0 | C1 | C2 | C3_4 | C5 | C6_9 |
|---|---|---|---|---|---|---|---|
| →S1 | – | F1 | A1 | C1 | B1 | B1 | B1 |
| A1 | S2 | E1 | E1 | E1 | E1 | E1 | E1 |
| B1 | S2 | F1 | F1 | F1 | F1 | F1 | F1 |
| C1 | S2 | E1 | E1 | E1 | E1 | G1 | F1 |
| E1 | S2 | F1 | F1 | F1 | F1 | F1 | F1 |
| G1 | S2 | F1 | F1 | F1 | F1 | F1 | – |
| F1 | S2 | – | – | – | – | – | – |

Aceptación: `A4, B4, C4, E4, F4, G4`.

### Placa
Regex: `[A-Za-z]{2}-?[0-9]{4}`

| δ | - | DIGITO | LETRA |
|---|---|---|---|
| →p0 | – | – | p1 |
| p1 | – | – | p2 |
| p2 | g | d1 | – |
| g | – | d1 | – |
| d1 | – | d2 | – |
| d2 | – | d3 | – |
| d3 | – | d4 | – |
| *d4 | – | – | – |

### Teléfono
Regex: `(?:[2-57-9][0-9]{2}|6[0-9]{3})-[0-9]{4}`

Clases: `SEIS`='6', `FIJO`='2'…'5','7'…'9', `D01`='0','1', `-`, `OTRO`.

| δ | - | D01 | FIJO | SEIS |
|---|---|---|---|---|
| →t0 | – | – | f1 | m1 |
| f1 | – | f2 | f2 | f2 |
| f2 | – | f3 | f3 | f3 |
| f3 | g | – | – | – |
| m1 | – | m2 | m2 | m2 |
| m2 | – | m3 | m3 | m3 |
| m3 | – | m4 | m4 | m4 |
| m4 | g | – | – | – |
| g | – | h1 | h1 | h1 |
| h1 | – | h2 | h2 | h2 |
| h2 | – | h3 | h3 | h3 |
| h3 | – | h4 | h4 | h4 |
| *h4 | – | – | – | – |

## Resultados
La salida es: **aceptada / rechazada**, la **traza** `(posición, símbolo, estado origen, estado destino)` y, si se rechaza, el **error** con posición y motivo.

Ejemplo aceptado, cédula `8-123-45`:

| Posición | Símbolo | Desde | Hacia |
|---|---|---|---|
| 1 | 8 | q0 | prov |
| 2 | - | prov | g1 |
| 3 | 1 | g1 | d1 |
| 4 | 2 | d1 | d2 |
| 5 | 3 | d2 | d3 |
| 6 | - | d3 | g2 |
| 7 | 4 | g2 | u1 |
| 8 | 5 | u1 | u2 |

Termina en `u2` (aceptación) → ✅ ACEPTADA.

Ejemplo rechazado, cédula `14-1-1`: tras `1` (q0 → p1), el símbolo `4` no tiene transición → ❌ RECHAZADA, `Posición 2: en p1 no hay transición con '4'`.

Ejemplo rechazado por fin de cadena, `8-123-`: termina en `g2` → `Fin de cadena: terminó en g2, que no es de aceptación`.

En la interfaz, el diagrama dibuja los estados (doble círculo = aceptación) y resalta el **estado actual** (amarillo mientras avanza, verde si acepta, rojo si rechaza).

### Capturas de pantalla
- [ ] `docs/captura_valida.png`: cadena válida con el recorrido completo
- [ ] `docs/captura_invalida.png`: cadena inválida con el error

## Pruebas
`python -m unittest` verifica, para cada formato y cada ejemplo, que `afd.acepta(x) == bool(re.fullmatch(regex, x))`. Incluye casos límite (cadena vacía, espacios, saltos de línea, caracteres no ASCII, dígitos de ancho completo, cadenas de 5000 caracteres) y una prueba exhaustiva de los octetos 0–999 en IPv4.

## Guion de demo
1. Elegir **Cédula**, cargar `8-123-456` y pulsar *Paso siguiente* hasta el final → ACEPTADA.
2. Escribir `14-1-1` y validar → RECHAZADA en la posición 2.
3. Repetir con *Ejemplo válido* / *Ejemplo inválido* en los otros formatos.
