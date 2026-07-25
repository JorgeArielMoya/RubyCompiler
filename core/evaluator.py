from core.lexer import TYPE_CONVERSIONS

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