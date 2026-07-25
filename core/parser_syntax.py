def syntax_analysis(tokens, errors):
    stack = []
    i = 0
    while i < len(tokens):
        token_type, value, line = tokens[i]
        if value == "for":
            if i + 1 >= len(tokens) or tokens[i + 1][0] != "IDENTIFIER":
                errors.append(f"Error sintáctico en la línea {line}: se esperaba variable después de 'for'")
            elif i + 2 >= len(tokens) or tokens[i + 2][1] != "in":
                errors.append(f"Error sintáctico en la línea {line}: se esperaba 'in' después de la variable en 'for'")
            elif i + 3 >= len(tokens) or tokens[i + 3][0] not in ("NUMBER", "IDENTIFIER"):
                errors.append(f"Error sintáctico en la línea {line}: se esperaba número o variable de inicio del rango después de 'in'")
            elif i + 4 >= len(tokens) or tokens[i + 4][1] != "..":
                errors.append(f"Error sintáctico en la línea {line}: se esperaba '..' en el rango del 'for'")
            elif i + 5 >= len(tokens) or tokens[i + 5][0] not in ("NUMBER", "IDENTIFIER"):
                errors.append(f"Error sintáctico en la línea {line}: se esperaba número o variable de fin del rango después de '..'")
            stack.append(("block", value, line))
        elif value in ("if", "while"):
            stack.append(("block", value, line))
        elif value == "end":
            if not stack or stack[-1][0] != "block":
                errors.append(f"Error sintáctico en la línea {line}: 'end' sin bloque abierto")
            else:
                stack.pop()
        elif value == "(":
            stack.append(("paren", "(", line))
        elif value == ")":
            if not stack or stack[-1][0] != "paren":
                errors.append(f"Error sintáctico en la línea {line}: ')' sin '(' correspondiente")
            else:
                stack.pop()
        i += 1
    if stack:
        kind, val, line = stack.pop()
        if kind == "block":
            errors.append(f"Error sintáctico: bloque '{val}' iniciado en la línea {line} no fue cerrado")
        else:
            errors.append(f"Error sintáctico: '(' abierto en la línea {line} no fue cerrado")