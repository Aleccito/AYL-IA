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
├── formatos/        # un módulo por formato; FORMATOS en __init__.py
│   ├── base.py      #   Formato, construir() y alfabetos comunes
│   ├── correo.py
│   ├── cedula.py
│   ├── ipv4.py
│   ├── placa.py
│   └── telefono.py  #   cada uno: clasificador + AFD + regex + ejemplos
├── simulador.py     # simular(afd, cadena) -> aceptada, traza, error
├── gui/             # interfaz Tkinter
│   ├── tema.py      #   colores, estilos ttk e icono
│   ├── diagrama.py  #   disposición y dibujo del AFD (flechas numeradas)
│   └── app.py       #   ventana, tablas y botones
├── main.py          # punto de entrada
└── tests/test_formatos.py
```

## Datos de entrada
En la interfaz: **formato** (combo) y **cadena** (campo de texto). Botones: *Validar*, *Paso siguiente*, *Reiniciar*, *Ejemplo válido*, *Ejemplo inválido*.

| Formato | Regla | Válidos | Inválidos |
|---|---|---|---|
| Correo | Estándar RFC 5321/5322 sin límites de longitud: parte local con letras, dígitos y `` !#$%&'*+/=?^_`{|}~- `` separados por `.` (sin punto al inicio, final ni doble); dominio con etiquetas sin guion en los bordes, al menos un `.` y último nivel con alguna letra | `ana@correo.com`, `user+tag@example.com`, `name/surname@example.com`, `a@b-c.d1` | `ana@correo`, `a..b@x.com`, `.ana@x.com`, `ana@-x.com`, `ana@a.123`, `ana@[192.168.2.1]` |
| Cédula | Prefijo: provincia `1`–`13`, o `PE`, `E`, `N`; luego `-` 1–4 dígitos `-` 1–6 dígitos | `8-123-456`, `10-23-4567`, `PE-1-234`, `E-8-12345`, `N-12-345` | `0-1-1`, `14-1-1`, `X-1-1`, `8-123`, `pe-1-234` |
| IPv4 | 4 octetos 0–255 separados por `.`, sin ceros a la izquierda | `192.168.1.1`, `0.0.0.0`, `255.255.255.255` | `256.1.1.1`, `01.2.3.4`, `1.2.3`, `1.2.3.4.5` |
| Placa | 2 letras, `-` opcional, 4 dígitos | `AB1234`, `AB-1234` | `A1234`, `ABC123`, `AB12345`, `1234AB` |
| Teléfono | Panamá: `+507`, un espacio y `NNNN-NNNN` (8 dígitos) | `+507 6123-4567`, `+507 2631-2345` | `6123-4567`, `+507 61234567`, `+507 263-1234`, `+50 6123-4567` |

> Correo: no se soportan comillas, IP literal, Unicode ni los límites de 64/63 caracteres (el AFD tendría cientos de estados).
> Supuesto propio: el formato de placa es una simplificación del real.

## Procesamiento
1. Se parte del estado inicial.
2. Por cada símbolo se calcula su **clase** y se aplica δ(estado, clase).
3. Si no existe transición, se rechaza en esa posición (el motivo se muestra).
4. Al terminar la cadena, se acepta solo si el estado es de aceptación.

Notación de las tablas: `→` estado inicial, `*` estado de aceptación, `–` sin transición (rechazo).

### Correo
Regex: `[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+(?=[0-9-]*[A-Za-z])[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?`

Clases: `LETRA`, `DIGITO`, `SIM` = `!#$%&'*+/=?^_`{|}~`, `-`, `.`, `@`, `OTRO`.

Estados: `q0`/`u`/`v` leen la parte local (`v` = justo después de un punto); `a` = tras `@`; `d1`/`g1` = primera etiqueta del dominio (`g1` = terminó en guion); `p` = tras un punto del dominio; `L` = etiqueta con al menos una letra; `N` = etiqueta solo de dígitos; `gL`/`gN` = terminó en guion. Solo se acepta en `L`, o sea: dominio con punto y último nivel con al menos una letra.

| δ | LETRA | DIGITO | SIM | - | . | @ |
|---|---|---|---|---|---|---|
| →q0 | u | u | u | u | – | – |
| u | u | u | u | u | v | a |
| v | u | u | u | u | – | – |
| a | d1 | d1 | – | – | – | – |
| d1 | d1 | d1 | – | g1 | p | – |
| g1 | d1 | d1 | – | g1 | – | – |
| p | L | N | – | – | – | – |
| *L | L | L | – | gL | p | – |
| N | L | N | – | gN | p | – |
| gL | L | L | – | gL | – | – |
| gN | L | N | – | gN | – | – |

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
Regex: `\+507 [0-9]{4}-[0-9]{4}`

Clases: `MAS`='+', `C5`='5', `C0`='0', `C7`='7', `OTRO_DIG`=resto de dígitos, `ESP`=' ', `-`, `OTRO`.

| δ | - | C0 | C5 | C7 | ESP | MAS | OTRO_DIG |
|---|---|---|---|---|---|---|---|
| →t0 | – | – | – | – | – | t1 | – |
| t1 | – | – | t2 | – | – | – | – |
| t2 | – | t3 | – | – | – | – | – |
| t3 | – | – | – | t4 | – | – | – |
| t4 | – | – | – | – | t5 | – | – |
| t5 | – | a1 | a1 | a1 | – | – | a1 |
| a1, a2, a3 | – | a(k+1) | a(k+1) | a(k+1) | – | – | a(k+1) |
| a4 | g | – | – | – | – | – | – |
| g | – | b1 | b1 | b1 | – | – | b1 |
| b1, b2, b3 | – | b(k+1) | b(k+1) | b(k+1) | – | – | b(k+1) |
| *b4 | – | – | – | – | – | – | – |

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

En la tabla de traza, al rechazar una cadena se agrega una última fila en rojo con el motivo (sin transición o fin de cadena sin aceptación). **Al hacer clic en cualquier fila** (también la del fallo) el diagrama y la línea "Lectura" muestran ese paso: estado alcanzado, flecha tomada y símbolo en curso.

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
