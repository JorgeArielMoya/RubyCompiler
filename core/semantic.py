from core.lexer import BUILT_IN_FUNCTIONS, TYPE_CONVERSIONS

def validate_type_conversion(func_name, argument, line, errors):
    try:
        if func_name == "Integer":
            int(argument)
        elif func_name == "Float":
            float(argument)
        elif func_name == "String":
            str(argument)
    except ValueError:
        errors.append(f"Error semántico en la línea {line}: no se puede convertir '{argument}' a {func_name}")

def semantic_analysis(tokens, errors):
    variables = set()
    i = 0
    while i < len(tokens):
        token_type, value, line = tokens[i]
        if (i + 1 < len(tokens) and tokens[i][1] == "<" and tokens[i + 1][1] == ">"):
            errors.append(f"Error sintáctico en la línea {line}: operador inválido '<>'")
        if token_type == "KEYWORD":
            if value == "for":
                if i + 1 < len(tokens) and tokens[i + 1][0] == "IDENTIFIER":
                    variables.add(tokens[i + 1][1])
            i += 1
            continue
        if token_type == "IDENTIFIER":
            if (i + 2 < len(tokens) and tokens[i + 1][0] == "DOT" and tokens[i + 2][0] == "NUMBER"):
                errors.append(f"Error sintáctico en la línea {line}: uso inválido de '.' en '{value}.{tokens[i+2][1]}'")
            if value in BUILT_IN_FUNCTIONS or value in TYPE_CONVERSIONS:
                i += 1
                continue
            if i + 1 < len(tokens) and tokens[i + 1][1] == "=":
                next_is_missing = (i + 2 >= len(tokens))
                next_is_bad = (
                    not next_is_missing
                    and tokens[i + 2][0] in ("KEYWORD", "OPERATOR")
                    and tokens[i + 2][1] != "("
                )
                next_diff_line = (
                    not next_is_missing
                    and tokens[i + 2][2] != line
                )
                same_line = (not next_is_missing and tokens[i + 2][2] == line)
                if next_is_missing or next_diff_line or (next_is_bad and same_line):
                    errors.append(
                        f"Error semántico en la línea {line}: "
                        f"asignación incompleta, falta valor para '{value}'"
                    )
                variables.add(value)
                if (i + 2 < len(tokens) and tokens[i + 2][1] in TYPE_CONVERSIONS):
                    func_name = tokens[i + 2][1]
                    if (i + 5 < len(tokens) and tokens[i + 3][1] == "(" and tokens[i + 5][1] == ")"):
                        arg_token = tokens[i + 4]
                        argument = arg_token[1]
                        if arg_token[0] == "STRING":
                            argument = argument.strip('"')
                        validate_type_conversion(func_name, argument, line, errors)
                i += 1
            else:
                if value not in variables:
                    errors.append(f"Error semántico en la línea {line}: variable '{value}' usada sin inicializar")
        i += 1