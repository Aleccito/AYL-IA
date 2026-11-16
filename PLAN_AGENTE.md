# Plan de desarrollo: Validador de formatos con autómatas finitos (Python)

## Contexto
Proyecto académico de Teoría de la Computación / Lenguajes Formales. Implementa el reconocimiento de lenguajes regulares usando **expresiones regulares** y **autómatas finitos deterministas (AFD)**. El software valida formatos reales (correo, cédula, IP, placa, teléfono) y muestra **paso a paso** cómo el autómata acepta o rechaza la cadena.

## Requisitos obligatorios
1. **Funcionamiento verificable**: introducir datos, procesarlos y mostrar resultados comprobables.
2. **Interfaz**: gráfica (Tkinter) para interactuar con el sistema.
3. **README.md** final con datos de entrada, procesamiento esperado y resultados.

## Reglas para el agente
- Lenguaje: **Python 3.10+**. Solo librería estándar (`re`, `tkinter`, `unittest`); `pytest` opcional.
- Código simple y legible (proyecto educativo). Comentarios solo donde aporten.
- Clase `AFD` **genérica**: no debe contener lógica de ningún formato concreto.
- **No** validar solo con `re.fullmatch()`: la regex es la referencia para pruebas; la decisión la toma el AFD.
- Completar y verificar cada paso antes de pasar al siguiente.

## Estructura objetivo
```
validador/
├── automata.py          # clase AFD genérica
├── formatos.py          # regex + AFD de cada formato
├── simulador.py         # recorrido paso a paso (traza)
├── gui.py               # interfaz Tkinter
├── main.py              # punto de entrada
├── tests/
│   └── test_formatos.py
└── README.md
```

---

## Paso 1. Alcance y estructura
- Formatos: **correo, cédula panameña, IPv4, placa, teléfono** (mínimo 4).
- Crear la estructura de carpetas anterior.
- **Verificación**: la estructura existe y `python main.py` arranca sin errores (aunque esté vacío).

## Paso 2. Expresiones regulares
- Definir una regex por formato en `formatos.py`.
- Preparar 5–10 casos válidos y 5–10 inválidos por formato.
- **Verificación**: `re.fullmatch()` da el resultado esperado en todos los casos.

## Paso 3. Diseño de los AFD
- Por formato: estados, estado inicial, estados de aceptación y transiciones.
- Usar **clases de símbolo** para reducir la tabla: `DIGITO`, `LETRA`, `@`, `.`, `-`, `OTRO`.
- Documentar cada AFD (tabla de transiciones) para reutilizarlo en el README.
- **Verificación**: cada AFD reconoce el mismo lenguaje que su regex (revisado a mano con los casos del paso 2).

## Paso 4. Clase `AFD` (`automata.py`)
- Atributos: `estados`, `alfabeto`, `transiciones` (dict `(estado, clase) -> estado`), `inicial`, `aceptacion`, `clasificador` (función símbolo → clase).
- Métodos: `transicion(estado, simbolo)` y `acepta(cadena) -> bool`.
- **Verificación**: prueba unitaria con un AFD de juguete (p. ej. binarios que terminan en `1`).

## Paso 5. Simulador paso a paso (`simulador.py`)
- `simular(afd, cadena)` devuelve:
  - `aceptada: bool`
  - `traza: list[(posicion, simbolo, estado_origen, estado_destino)]`
  - `error: (posicion, mensaje) | None`. Ejemplo: `"Posición 5: en q2 no hay transición con '@'"`.
  - También se rechaza si la cadena termina en un estado que no es de aceptación (explicarlo en `error`).
- **Verificación**: la traza de una cadena conocida coincide con la esperada a mano.

## Paso 6. Registro de formatos (`formatos.py`)
- Cada formato tiene `nombre`, `regex`, `afd`, `ejemplos_validos` y `ejemplos_invalidos`.
- Exponer `FORMATOS: dict[str, Formato]`.
- **Verificación**: es posible iterar `FORMATOS` y simular cualquier formato.

## Paso 7. Pruebas automáticas (`tests/test_formatos.py`)
- Por cada formato y cada ejemplo: `afd.acepta(x) == bool(re.fullmatch(regex, x))`.
- Incluir casos límite: cadena vacía, espacios, caracteres no ASCII, cadenas muy largas.
- **Verificación**: `python -m unittest` (o `pytest`) pasa al 100 %.

## Paso 8. Interfaz Tkinter (`gui.py`)
- Combo para elegir formato, campo de texto y botón **Validar**.
- Resultado visible: ✅ ACEPTADA / ❌ RECHAZADA y el mensaje de error.
- Tabla (`ttk.Treeview`) con la traza: posición | símbolo | desde | hacia.
- Canvas con el diagrama del AFD (círculos para los estados, doble círculo para los de aceptación, flechas con su etiqueta) y **el estado actual resaltado**.
- Botones **Paso siguiente** y **Reiniciar** para la animación paso a paso.
- Botón para cargar un ejemplo válido o inválido.
- **Verificación**: probar en la interfaz al menos un caso válido y uno inválido por formato.

## Paso 9. README.md final
Debe contener:
- **Descripción** y conceptos aplicados (expresiones regulares, AFD, reconocimiento de lenguajes).
- **Datos de entrada**: formato seleccionado y cadena; tabla de ejemplos válidos e inválidos por formato.
- **Procesamiento**: clasificación de cada símbolo, aplicación de la transición δ(q, clase), aceptación si termina en un estado final; regex y tabla o diagrama del AFD por formato.
- **Resultados**: aceptada o rechazada, traza de estados, posición y motivo del error.
- **Requisitos e instalación**: Python 3.10+, `python main.py`, `python -m unittest`.
- **Capturas de pantalla** (dejar marcadores si aún no existen).
- **Verificación**: siguiendo el README desde cero, cualquier persona puede ejecutar el programa y las pruebas.

## Paso 10. Verificación final y demo
- Ejecutar todas las pruebas y revisar los casos límite.
- Checklist:
  - [ ] Entrada → procesamiento → resultado comprobable (pasos 5 y 7)
  - [ ] Interfaz gráfica funcional (paso 8)
  - [ ] README con entradas, procesamiento y resultados (paso 9)
- Guion de demo: una cadena válida (recorrido completo) y una inválida (mostrar dónde falla).

## Definición de terminado
Las pruebas pasan, la interfaz valida y anima todos los formatos, y el README permite a un tercero ejecutar y entender el sistema sin ayuda.
