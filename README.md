# Ruby Interpreter & IDE in Python 💎🐍

Un intérprete y analizador de código Ruby desarrollado completamente en **Python**, que incluye un entorno visual (IDE) integrado para la ejecución y validación de sintaxis.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3** (Lenguaje principal de desarrollo y lógica del compilador)
* **Tkinter / PyQt** (Framework de interfaz gráfica para el entorno IDE)
* **Arquitectura de Compiladores** (Lexer, Parser, Análisis Semántico y Evaluador basados en AST)

---

## ✅ Características Soportadas

- 📌 Tipos de datos
- 🔤 Manejo de cadenas (Strings)
- ➕ Operaciones básicas (aritméticas y lógicas)
- 🔀 Estructuras condicionales (`if`, `elsif`, `else`)
- 🔁 Bucle `for`
- 🔄 Bucle `while`

---

## 📁 Estructura del Proyecto

```text
├── core/
│   ├── evaluator.py      # Evaluación y ejecución de expresiones
│   ├── interpreter.py    # Coordinador general del flujo de interpretación
│   ├── lexer.py          # Análisis léxico (tokens)
│   ├── parser_syntax.py  # Análisis sintáctico (AST)
│   └── semantic.py       # Análisis semántico y validaciones
├── ui/
│   └── ide_window.py     # Interfaz gráfica del usuario (IDE)
├── config.py             # Configuraciones globales
├── .gitignore            # Archivos excluidos de Git
├── main.py               # Punto de entrada principal de la aplicación
└── README.md