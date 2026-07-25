EXAMPLES = {
    "Tipos de datos": 'entero = Integer("10")\ndecimal = Float("3.14")\ntexto = String("hola")\nputs entero\nputs decimal\nputs texto',
    "Cadenas": 'nombre = "Jorge"\napellido = "Moya"\ncompleto = nombre + " " + apellido\nputs completo',
    "Operaciones básicas": 'a = 10\nb = 3\nsuma = a + b\nresta = a - b\nmultiplicacion = a * b\ndivision = a / b\nputs suma\nputs resta\nputs multiplicacion\nputs division',
    "Condicionales": 'nota = 85\nif nota >= 90\n  puts "A"\nelsif nota >= 80\n  puts "B"\nelsif nota >= 70\n  puts "C"\nelse\n  puts("Reprobado")\nend',
    "Bucle For": 'for i in 1..5\n  puts i\nend',
    "Bucle While": 'i = 1\nwhile i <= 5\n  puts i\n  i = i + 1\nend'
}

TOKEN_COLORS = {
    "KEYWORD":    "#c792ea",
    "IDENTIFIER": "#82aaff",
    "NUMBER":     "#f78c6c",
    "STRING":     "#c3e88d",
    "OPERATOR":   "#89ddff",
    "RANGE":      "#ffcb6b",
    "DOT":        "#89ddff",
    "PAREN":      "#ffcb6b",
}

KEYWORD_COLORS = {
    "if": "#c792ea", "elsif": "#c792ea", "else": "#c792ea",
    "end": "#c792ea", "while": "#c792ea", "for": "#c792ea", "in": "#c792ea",
}

BG         = "#1e1e2e"
BG2        = "#181825"
BG3        = "#313244"
ACCENT     = "#cba6f7"
ACCENT2    = "#89dceb"
TEXT       = "#cdd6f4"
TEXT2      = "#a6adc8"
TEXT3      = "#585b70"
RED        = "#f38ba8"
GREEN      = "#a6e3a1"
YELLOW     = "#f9e2af"

MONO_FONT  = ("Consolas", 13)
MONO_FONT2 = ("Consolas", 11)
UI_FONT    = ("Segoe UI", 11)
UI_FONT_B  = ("Segoe UI", 11, "bold")