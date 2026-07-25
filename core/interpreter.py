from core.lexer import lexical_analysis, BUILT_IN_FUNCTIONS
from core.parser_syntax import syntax_analysis
from core.semantic import semantic_analysis
from core.evaluator import evaluate_expression, collect_expression, collect_print_arg

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