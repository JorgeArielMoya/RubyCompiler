import re

TOKENS = [
    ("RANGE", r"\.\."),
    ("NUMBER", r"\d+\.\d+|\d+"),
    ("STRING", r"\".*?\""),
    ("KEYWORD", r"\b(if|elsif|else|end|while|for|in)\b"),
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("OPERATOR", r"==|!=|<=|>=|[+\-*/=<>!]"),
    ("DOT", r"\."),
    ("PAREN", r"[()]"),
    ("WHITESPACE", r"[ \t]+"),
]

BUILT_IN_FUNCTIONS = {"print", "puts"}
TYPE_CONVERSIONS = {"Integer", "Float", "String"}

def lexical_analysis(code, errors):
    tokens = []
    lines = code.split("\n")
    for line_num, line in enumerate(lines, start=1):
        pos = 0
        while pos < len(line):
            match = None
            for token_type, pattern in TOKENS:
                regex = re.compile(pattern)
                match = regex.match(line, pos)
                if match:
                    if token_type != "WHITESPACE":
                        tokens.append((token_type, match.group(), line_num))
                    pos = match.end()
                    break
            if not match:
                errors.append(f"Error léxico en la línea {line_num}: símbolo inválido '{line[pos]}'")
                pos += 1
    return tokens