## Key Components

1. **Tokenizer**: Parses Lisp source code into tokens, handling strings, symbols, numbers, and parentheses
2. **Parser**: Converts tokens into an Abstract Syntax Tree (AST) using recursive descent parsing
3. **Evaluator**: Implements the core evaluation logic with `eval_expr` and `apply_fn` functions
4. **Built-in Environment**: Provides arithmetic, comparison, and list manipulation functions

## Features

- **Basic data types**: integers, floats, strings, symbols, and lists
- **Special forms**: `lambda`, `if`, `define`, `begin`, `quote`
- **Function calls**: Both built-in Python functions and user-defined lambda functions
- **Variable scoping**: Proper lexical scoping for lambda functions
- **Interactive REPL**: Run interactively or execute files
- **Error handling**: Better error messages and exception handling

## Example Usage

You can use it in two ways:

1. **Interactive REPL**: Run `python lisp.py` to start an interactive session
2. **File execution**: Run `python lisp.py program.lisp` to execute a file

## Sample Lisp Code

```lisp
; Define a variable
(define x 42)

; Define a function
(define square (lambda (n) (* n n)))

; Use the function
(square 5)  ; Returns 25

; Conditional
(if (> x 40) 'large 'small)  ; Returns 'large'

; List operations
(define lst (list 1 2 3 4))
(car lst)  ; Returns 1
(cdr lst)  ; Returns (2 3 4)
```

The interpreter implements the metacircular evaluator pattern where the evaluation of Lisp expressions is handled recursively, making it a clean and elegant implementation of a basic Lisp system!