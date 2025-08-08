import re
import sys
import operator
import pprint as pretty_print

# Utility functions and data structures
pprint = lambda obj: pretty_print.PrettyPrinter(indent=4).pprint(obj)

def fail(s):
    print(s)
    sys.exit(-1)

class InterpreterObject(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

class Symbol(InterpreterObject):
    pass

class String(InterpreterObject):
    pass

class Lambda(InterpreterObject):
    def __init__(self, arguments, code):
        self.arguments = arguments
        self.code = code

    def __repr__(self):
        return "(lambda ({}) ({}))".format(self.arguments, self.code)

# Parser
def tokenize(s):
    ret = []
    in_string = False
    current_word = ''
    
    for i, char in enumerate(s):
        if char == "'":
            if in_string is False:
                in_string = True
                current_word += char
            else:
                in_string = False
                current_word += char
                ret.append(current_word)
                current_word = ''

        elif in_string is True:
            current_word += char

        elif char in ['\t', '\n', ' ']:
            if current_word and not in_string:
                ret.append(current_word)
                current_word = ''

        elif char in ['(', ')']:
            if current_word and not in_string:
                ret.append(current_word)
                current_word = ''
            ret.append(char)

        else:
            current_word += char
            if i < len(s) - 1 and s[i+1] in ['(', ')', ' ', '\n', '\t'] and not in_string:
                ret.append(current_word)
                current_word = ''
    
    if current_word:
        ret.append(current_word)

    return ret

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_string(s):
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return True
    return False

def parse(tokens):
    if not tokens:
        fail("Empty expression")
    
    itert = iter(tokens)
    token = next(itert)

    if token != '(':
        fail("Unexpected token {}".format(token))

    return do_parse(itert)

def do_parse(tokens):
    ret = []

    for token in tokens:
        if token == '(':
            ret.append(do_parse(tokens))
        elif token == ')':
            return ret
        elif is_integer(token):
            ret.append(int(token))
        elif is_float(token):
            ret.append(float(token))
        elif is_string(token):
            ret.append(String(token[1:-1]))
        else:
            ret.append(Symbol(token))
    
    fail("Missing closing parenthesis")

# Interpreter
def eval_expr(expr, environment):
    # Handle atomic values
    if isinstance(expr, int) or isinstance(expr, float):
        return expr
    elif isinstance(expr, str):
        return expr
    elif isinstance(expr, String):
        return expr.value
    elif isinstance(expr, Symbol):
        if expr.value not in environment:
            fail("Couldn't find symbol {}".format(expr.value))
        return environment[expr.value]
    elif isinstance(expr, list):
        if not expr:
            return []
        
        # Handle special forms
        if isinstance(expr[0], Symbol):
            if expr[0].value == 'lambda':
                if len(expr) < 3:
                    fail("Lambda requires arguments and body")
                arg_names = expr[1]
                code = expr[2]
                return Lambda(arg_names, code)

            elif expr[0].value == 'if':
                if len(expr) < 3:
                    fail("If requires at least condition and then clause")
                condition = expr[1]
                then_clause = expr[2]
                else_clause = None
                if len(expr) == 4:
                    else_clause = expr[3]

                if eval_expr(condition, environment) is not False:
                    return eval_expr(then_clause, environment)
                elif else_clause is not None:
                    return eval_expr(else_clause, environment)
                else:
                    return None

            elif expr[0].value == 'define':
                if len(expr) != 3:
                    fail("Define requires name and value")
                name = expr[1].value
                value = eval_expr(expr[2], environment)
                environment[name] = value
                return value

            elif expr[0].value == 'begin':
                result = None
                for ex in expr[1:]:
                    result = eval_expr(ex, environment)
                return result

            elif expr[0].value == 'quote':
                if len(expr) != 2:
                    fail("Quote requires exactly one argument")
                return expr[1]

            else:
                # Function call
                fn = eval_expr(expr[0], environment)
                args = [eval_expr(arg, environment) for arg in expr[1:]]
                return apply_fn(fn, args, environment)
        else:
            # Function call where function is not a symbol
            fn = eval_expr(expr[0], environment)
            args = [eval_expr(arg, environment) for arg in expr[1:]]
            return apply_fn(fn, args, environment)
    
    return expr

def apply_fn(fn, args, environment):
    # Built-in function
    if callable(fn):
        return fn(*args)
    
    # User-defined lambda
    if isinstance(fn, Lambda):
        new_env = dict(environment)
        if len(args) != len(fn.arguments):
            fail("Mismatched number of arguments to lambda: expected {}, got {}".format(
                len(fn.arguments), len(args)))
        
        # Bind arguments to parameters
        for i in range(len(fn.arguments)):
            param_name = fn.arguments[i].value if isinstance(fn.arguments[i], Symbol) else fn.arguments[i]
            new_env[param_name] = args[i]
        
        return eval_expr(fn.code, new_env)
    
    fail("Cannot apply non-function: {}".format(fn))

# Base environment with built-in functions
base_environment = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,  # Use truediv for Python 3 compatibility
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    '=': operator.eq,
    '!=': operator.ne,
    'nil': None,
    'null?': lambda x: x is None,
    'print': lambda x: print(x),
    'list': lambda *args: list(args),
    'car': lambda lst: lst[0] if lst else None,
    'cdr': lambda lst: lst[1:] if len(lst) > 1 else [],
    'cons': lambda x, lst: [x] + (lst if isinstance(lst, list) else [lst]),
    'length': len,
    'append': lambda *lsts: [item for lst in lsts for item in lst],
}

def repl():
    """Read-Eval-Print Loop"""
    env = dict(base_environment)
    print("Lisp Interpreter - Enter expressions (Ctrl+C to exit)")
    
    while True:
        try:
            user_input = input("lisp> ")
            if user_input.strip():
                try:
                    tokens = tokenize(user_input)
                    if tokens:
                        parsed = parse(tokens)
                        result = eval_expr(parsed, env)
                        if result is not None:
                            print(result)
                except Exception as e:
                    print("Error:", e)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break

def run_file(filename):
    """Run a Lisp program from a file"""
    try:
        with open(filename, 'r') as fd:
            contents = fd.read()
            tokens = tokenize(contents)
            if tokens:
                parsed = parse(tokens)
                eval_expr(parsed, base_environment)
    except FileNotFoundError:
        print("File not found:", filename)
    except Exception as e:
        print("Error:", e)

def main():
    if len(sys.argv) == 1:
        # No arguments - start REPL
        repl()
    elif len(sys.argv) == 2:
        # One argument - run file
        run_file(sys.argv[1])
    else:
        print("Usage: python {} [file]".format(sys.argv[0]))
        print("  No arguments: Start interactive REPL")
        print("  With file: Execute Lisp program from file")
        sys.exit(-1)

if __name__ == '__main__':
    main()