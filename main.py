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

def evaluate_expression(tokens, variables):
    values = []
    for tok_type, tok_val, _ in tokens:
        if tok_type == "NUMBER":
            values.append(float(tok_val) if "." in tok_val else int(tok_val))
        elif tok_type == "STRING":
            values.append(tok_val.strip('"'))
        elif tok_type == "IDENTIFIER":
            if tok_val in TYPE_CONVERSIONS:
                values.append(tok_val)
            else:
                values.append(variables.get(tok_val, 0))
        elif tok_type == "OPERATOR":
            values.append(tok_val)
        elif tok_type == "PAREN":
            values.append(tok_val)

    if (len(values) >= 4 and values[0] in TYPE_CONVERSIONS and values[1] == "("):
        arg = values[2]
        func = values[0]
        try:
            if func == "Integer":
                return int(str(arg).replace('"', ''))
            elif func == "Float":
                return float(str(arg).replace('"', ''))
            elif func == "String":
                return str(arg)
        except:
            return 0

    if len(values) == 1:
        return values[0]

    expr_parts = []
    for v in values:
        if isinstance(v, str) and v not in ("+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">=", "(", ")"):
            expr_parts.append(repr(v))
        else:
            expr_parts.append(str(v))

    expr_str = " ".join(expr_parts)
    try:
        result = eval(expr_str)
        if isinstance(result, float) and result == int(result):
            result = int(result)
        return result
    except:
        return 0

def collect_expression(tokens, start):
    if start >= len(tokens):
        return [], start
    current_line = tokens[start][2]
    expr_tokens = []
    i = start
    while i < len(tokens) and tokens[i][2] == current_line:
        tok_type, tok_val, _ = tokens[i]
        if tok_type == "KEYWORD" and tok_val in ("if", "elsif", "else", "end", "while", "for", "in"):
            break
        expr_tokens.append(tokens[i])
        i += 1
    return expr_tokens, i

def collect_print_arg(tokens, i, variables):
    if i >= len(tokens):
        return "", i

    if tokens[i][1] == "(":
        depth = 0
        j = i
        arg_tokens = []
        while j < len(tokens):
            if tokens[j][1] == "(":
                depth += 1
                if depth > 1:
                    arg_tokens.append(tokens[j])
            elif tokens[j][1] == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
                else:
                    arg_tokens.append(tokens[j])
            else:
                arg_tokens.append(tokens[j])
            j += 1
        val = evaluate_expression(arg_tokens, variables)
        return val, j

    current_line = tokens[i][2]
    arg_tokens = []
    j = i
    while j < len(tokens) and tokens[j][2] == current_line:
        arg_tokens.append(tokens[j])
        j += 1
    val = evaluate_expression(arg_tokens, variables)
    return val, j

def execute_block(tokens, start, variables, output_lines):
    i = start
    while i < len(tokens):
        tok_type, value, line = tokens[i]
 
        if tok_type == "IDENTIFIER" and value in BUILT_IN_FUNCTIONS:
            func = value
            i += 1
            val, i = collect_print_arg(tokens, i, variables)
            if isinstance(val, float) and val == int(val):
                val = int(val)
            if func == "print":
                output_lines.append(("print", str(val)))
            else:
                output_lines.append(("puts", str(val)))
            continue
 
        if tok_type == "IDENTIFIER" and i + 1 < len(tokens) and tokens[i + 1][1] == "=":
            var_name = value
            expr_tokens, i = collect_expression(tokens, i + 2)
            variables[var_name] = evaluate_expression(expr_tokens, variables)
            continue
 
        if tok_type == "KEYWORD" and value == "if":
            cond_tokens, i = collect_expression(tokens, i + 1)
            condition = evaluate_expression(cond_tokens, variables)
            executed = False
            if bool(condition):
                i = execute_block(tokens, i, variables, output_lines)
                executed = True
            else:
                i = skip_block(tokens, i)
 
            while i < len(tokens):
                kw = tokens[i][1]
                if kw == "elsif":
                    cond_tokens, i = collect_expression(tokens, i + 1)
                    branch_cond = evaluate_expression(cond_tokens, variables)
                    if not executed and bool(branch_cond):
                        i = execute_block(tokens, i, variables, output_lines)
                        executed = True
                    else:
                        i = skip_block(tokens, i)
                elif kw == "else":
                    i += 1
                    if not executed:
                        i = execute_block(tokens, i, variables, output_lines)
                        executed = True
                    else:
                        i = skip_block(tokens, i)
                elif kw == "end":
                    i += 1
                    break
                else:
                    break
            continue
 
        if tok_type == "KEYWORD" and value in ("elsif", "else", "end"):
            return i
 
        if tok_type == "KEYWORD" and value == "while":
            cond_tokens, body_start = collect_expression(tokens, i + 1)
            MAX_ITER = 100_000
            iter_count = 0
            while True:
                condition = evaluate_expression(cond_tokens, variables)
                if not bool(condition):
                    break
                iter_count += 1
                if iter_count > MAX_ITER:
                    output_lines.append(("puts", "(bucle while interrumpido: demasiadas iteraciones)"))
                    break
                execute_block(tokens, body_start, variables, output_lines)
            i = skip_to_end(tokens, body_start)
            continue
 
        if tok_type == "KEYWORD" and value == "for":
            rango_valido = (
                i + 5 < len(tokens)
                and tokens[i + 1][0] == "IDENTIFIER"
                and tokens[i + 2][1] == "in"
                and tokens[i + 3][0] in ("NUMBER", "IDENTIFIER")
                and tokens[i + 4][1] == ".."
                and tokens[i + 5][0] in ("NUMBER", "IDENTIFIER")
            )
            if rango_valido:
                var = tokens[i + 1][1]
                tok_start = tokens[i + 3]
                tok_end   = tokens[i + 5]
                start_val = int(variables.get(tok_start[1], tok_start[1]) if tok_start[0] == "IDENTIFIER" else tok_start[1])
                end_val   = int(variables.get(tok_end[1],   tok_end[1])   if tok_end[0]   == "IDENTIFIER" else tok_end[1])
                body_start = i + 6
                for n in range(start_val, end_val + 1):
                    variables[var] = n
                    execute_block(tokens, body_start, variables, output_lines)
                i = skip_to_end(tokens, body_start)
            else:
                i = skip_to_end(tokens, i + 1)
            continue
        i += 1
    return i

def skip_block(tokens, start):
    depth = 0
    i = start
    while i < len(tokens):
        kw = tokens[i][1]
        if kw in ("if", "while", "for"):
            depth += 1
        elif kw == "end":
            if depth == 0:
                return i
            depth -= 1
        elif kw in ("elsif", "else") and depth == 0:
            return i
        i += 1
    return i

def skip_to_end(tokens, start):
    depth = 0
    i = start
    while i < len(tokens):
        kw = tokens[i][1]
        if kw in ("if", "while", "for"):
            depth += 1
        elif kw == "end":
            if depth == 0:
                return i + 1
            depth -= 1
        i += 1
    return i

def run_interpreter(code):
    errors = []
    tokens = lexical_analysis(code, errors)
    syntax_analysis(tokens, errors)
    semantic_analysis(tokens, errors)
    output_lines = []
    if not errors:
        variables = {}
        execute_block(tokens, 0, variables, output_lines)
    return output_lines, errors, tokens