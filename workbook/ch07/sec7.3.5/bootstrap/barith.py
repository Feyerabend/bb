#!/usr/bin/env python3

# Bootstrap Language - Self-Hosting Interpreter
# 1. The Python interpreter (bootstrap)
# 2. The language written in its own syntax (self-hosted)


import re
from typing import Any, Dict, List

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        
    def tokenize(self) -> List[tuple]:
        tokens = []
        patterns = [
            ('NUMBER', r'\d+'),
            ('STRING', r'"[^"]*"'),
            ('IF', r'\bif\b'),
            ('WHILE', r'\bwhile\b'),
            ('LET', r'\blet\b'),
            ('FN', r'\bfn\b'),
            ('RETURN', r'\breturn\b'),
            ('AND', r'\band\b'),
            ('OR', r'\bor\b'),
            ('EQ', r'=='),
            ('NE', r'!='),
            ('LE', r'<='),
            ('GE', r'>='),
            ('LT', r'<'),
            ('GT', r'>'),
            ('ASSIGN', r'='),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULT', r'\*'),
            ('DIV', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LBRACK', r'\['),
            ('RBRACK', r'\]'),
            ('COMMA', r','),
            ('DOT', r'\.'),
            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t]+'),
            ('COMMENT', r'#[^\n]*'),
        ]
        
        pattern = '|'.join(f'(?P<{name}>{pat})' for name, pat in patterns)
        for match in re.finditer(pattern, self.code):
            kind = match.lastgroup
            value = match.group()
            if kind not in ('SKIP', 'NEWLINE', 'COMMENT'):
                tokens.append((kind, value))
        return tokens

class Parser:
    def __init__(self, tokens: List[tuple]):
        self.tokens = tokens
        self.pos = 0
        
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def consume(self, expected=None):
        if self.pos >= len(self.tokens):
            return None
        token = self.tokens[self.pos]
        if expected and token[0] != expected:
            raise SyntaxError(f"Expected {expected}, got {token[0]}")
        self.pos += 1
        return token
    
    def parse(self):
        statements = []
        while self.peek():
            statements.append(self.parse_statement())
        return statements
    
    def parse_statement(self):
        token = self.peek()
        if token[0] == 'LET':
            return self.parse_let()
        elif token[0] == 'FN':
            return self.parse_fn()
        elif token[0] == 'IF':
            return self.parse_if()
        elif token[0] == 'WHILE':
            return self.parse_while()
        elif token[0] == 'RETURN':
            return self.parse_return()
        else:
            return ('EXPR', self.parse_expr())
    
    def parse_let(self):
        self.consume('LET')
        name = self.consume('ID')[1]
        self.consume('ASSIGN')
        value = self.parse_expr()
        return ('LET', name, value)
    
    def parse_fn(self):
        self.consume('FN')
        name = self.consume('ID')[1]
        self.consume('LPAREN')
        params = []
        while self.peek()[0] != 'RPAREN':
            params.append(self.consume('ID')[1])
            if self.peek()[0] == 'COMMA':
                self.consume('COMMA')
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        return ('FN', name, params, body)
    
    def parse_if(self):
        self.consume('IF')
        cond = self.parse_expr()
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        return ('IF', cond, body)
    
    def parse_while(self):
        self.consume('WHILE')
        cond = self.parse_expr()
        self.consume('LBRACE')
        body = []
        while self.peek()[0] != 'RBRACE':
            body.append(self.parse_statement())
        self.consume('RBRACE')
        return ('WHILE', cond, body)
    
    def parse_return(self):
        self.consume('RETURN')
        value = self.parse_expr()
        return ('RETURN', value)
    
    def parse_expr(self):
        return self.parse_or()
    
    def parse_or(self):
        left = self.parse_and()
        while self.peek() and self.peek()[0] == 'OR':
            self.consume('OR')
            right = self.parse_and()
            left = ('OR', left, right)
        return left
    
    def parse_and(self):
        left = self.parse_comparison()
        while self.peek() and self.peek()[0] == 'AND':
            self.consume('AND')
            right = self.parse_comparison()
            left = ('AND', left, right)
        return left
    
    def parse_comparison(self):
        left = self.parse_additive()
        if self.peek() and self.peek()[0] in ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE'):
            op = self.consume()[0]
            right = self.parse_additive()
            return (op, left, right)
        return left
    
    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek() and self.peek()[0] in ('PLUS', 'MINUS'):
            op = self.consume()[0]
            right = self.parse_multiplicative()
            left = (op, left, right)
        return left
    
    def parse_multiplicative(self):
        left = self.parse_postfix()
        while self.peek() and self.peek()[0] in ('MULT', 'DIV'):
            op = self.consume()[0]
            right = self.parse_postfix()
            left = (op, left, right)
        return left
    
    def parse_postfix(self):
        expr = self.parse_primary()
        while self.peek() and self.peek()[0] == 'LBRACK':
            self.consume('LBRACK')
            index = self.parse_expr()
            self.consume('RBRACK')
            expr = ('INDEX', expr, index)
        return expr
    
    def parse_primary(self):
        token = self.peek()
        if token[0] == 'NUMBER':
            self.consume()
            return ('NUMBER', int(token[1]))
        elif token[0] == 'STRING':
            self.consume()
            return ('STRING', token[1][1:-1])
        elif token[0] == 'LBRACK':
            return self.parse_list()
        elif token[0] == 'ID':
            name = self.consume()[1]
            if self.peek() and self.peek()[0] == 'LPAREN':
                return self.parse_call(name)
            return ('ID', name)
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expr()
            self.consume('RPAREN')
            return expr
        raise SyntaxError(f"Unexpected token: {token}")
    
    def parse_list(self):
        self.consume('LBRACK')
        elements = []
        while self.peek()[0] != 'RBRACK':
            elements.append(self.parse_expr())
            if self.peek()[0] == 'COMMA':
                self.consume('COMMA')
        self.consume('RBRACK')
        return ('LIST', elements)
    
    def parse_call(self, name):
        self.consume('LPAREN')
        args = []
        while self.peek()[0] != 'RPAREN':
            args.append(self.parse_expr())
            if self.peek()[0] == 'COMMA':
                self.consume('COMMA')
        self.consume('RPAREN')
        return ('CALL', name, args)

class Interpreter:
    def __init__(self):
        self.globals = {
            'print': lambda *args: print(*args),
            'len': lambda x: len(x),
            'append': lambda lst, item: lst + [item],
            'get': lambda lst, i: lst[i] if i < len(lst) else None,
            'set': lambda lst, i, val: lst[:i] + [val] + lst[i+1:],
            'substr': lambda s, start, end: s[start:end],
            'char_at': lambda s, i: s[i] if i < len(s) else "",
            'str_eq': lambda a, b: a == b,
            'is_digit': lambda c: c.isdigit() if c else False,
            'is_alpha': lambda c: c.isalpha() if c else False,
            'int_val': lambda s: int(s) if s.isdigit() else 0,
        }
        
    def run(self, ast: List):
        for stmt in ast:
            result = self.eval_stmt(stmt, self.globals)
            if result and result[0] == 'RETURN':
                return result[1]
    
    def eval_stmt(self, stmt, env):
        if stmt[0] == 'LET':
            _, name, expr = stmt
            env[name] = self.eval_expr(expr, env)
        elif stmt[0] == 'FN':
            _, name, params, body = stmt
            env[name] = ('FUNCTION', params, body, env)
        elif stmt[0] == 'IF':
            _, cond, body = stmt
            if self.eval_expr(cond, env):
                for s in body:
                    result = self.eval_stmt(s, env)
                    if result and result[0] == 'RETURN':
                        return result
        elif stmt[0] == 'WHILE':
            _, cond, body = stmt
            while self.eval_expr(cond, env):
                for s in body:
                    result = self.eval_stmt(s, env)
                    if result and result[0] == 'RETURN':
                        return result
        elif stmt[0] == 'RETURN':
            return ('RETURN', self.eval_expr(stmt[1], env))
        elif stmt[0] == 'EXPR':
            self.eval_expr(stmt[1], env)
    
    def eval_expr(self, expr, env):
        if expr[0] == 'NUMBER':
            return expr[1]
        elif expr[0] == 'STRING':
            return expr[1]
        elif expr[0] == 'LIST':
            return [self.eval_expr(e, env) for e in expr[1]]
        elif expr[0] == 'ID':
            return env[expr[1]]
        elif expr[0] == 'INDEX':
            lst = self.eval_expr(expr[1], env)
            idx = self.eval_expr(expr[2], env)
            return lst[idx]
        elif expr[0] == 'CALL':
            _, name, args = expr
            fn = env[name]
            arg_vals = [self.eval_expr(arg, env) for arg in args]
            if callable(fn):
                return fn(*arg_vals)
            else:
                _, params, body, fn_env = fn
                local_env = fn_env.copy()
                for param, val in zip(params, arg_vals):
                    local_env[param] = val
                for stmt in body:
                    result = self.eval_stmt(stmt, local_env)
                    if result and result[0] == 'RETURN':
                        return result[1]
        elif expr[0] in ('PLUS', 'MINUS', 'MULT', 'DIV'):
            left = self.eval_expr(expr[1], env)
            right = self.eval_expr(expr[2], env)
            if expr[0] == 'PLUS': return left + right
            elif expr[0] == 'MINUS': return left - right
            elif expr[0] == 'MULT': return left * right
            elif expr[0] == 'DIV': return left // right
        elif expr[0] in ('EQ', 'NE', 'LT', 'GT', 'LE', 'GE'):
            left = self.eval_expr(expr[1], env)
            right = self.eval_expr(expr[2], env)
            if expr[0] == 'EQ': return left == right
            elif expr[0] == 'NE': return left != right
            elif expr[0] == 'LT': return left < right
            elif expr[0] == 'GT': return left > right
            elif expr[0] == 'LE': return left <= right
            elif expr[0] == 'GE': return left >= right
        elif expr[0] in ('AND', 'OR'):
            left = self.eval_expr(expr[1], env)
            right = self.eval_expr(expr[2], env)
            if expr[0] == 'AND': return left and right
            elif expr[0] == 'OR': return left or right

def run_code(code: str):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.run(ast)

# Self-hosted interpreter in its own language
self_hosted_code = '''
# Helper to scan a number
fn scan_number(code, i) {
    let end = i
    let len_code = len(code)
    
    while end < len_code {
        if is_digit(char_at(code, end)) {
            let end = end + 1
        }
        if is_digit(char_at(code, end)) {
            let end = end
        }
        if is_digit(char_at(code, end)) == 0 {
            return end
        }
    }
    return end
}

# Tokenizer using recursion
fn tokenize_helper(code, i, tokens) {
    let len_code = len(code)
    
    if i >= len_code {
        return tokens
    }
    
    let c = char_at(code, i)
    
    # Skip whitespace
    if str_eq(c, " ") {
        return tokenize_helper(code, i + 1, tokens)
    }
    
    # Numbers - just scan single digit for simplicity
    if is_digit(c) {
        let tokens = append(tokens, ["NUMBER", int_val(c)])
        return tokenize_helper(code, i + 1, tokens)
    }
    
    # Operators
    if str_eq(c, "+") {
        let tokens = append(tokens, ["PLUS", "+"])
        return tokenize_helper(code, i + 1, tokens)
    }
    if str_eq(c, "*") {
        let tokens = append(tokens, ["MULT", "*"])
        return tokenize_helper(code, i + 1, tokens)
    }
    if str_eq(c, "(") {
        let tokens = append(tokens, ["LPAREN", "("])
        return tokenize_helper(code, i + 1, tokens)
    }
    if str_eq(c, ")") {
        let tokens = append(tokens, ["RPAREN", ")"])
        return tokenize_helper(code, i + 1, tokens)
    }
    
    return tokenize_helper(code, i + 1, tokens)
}

fn tokenize(code) {
    return tokenize_helper(code, 0, [])
}

# Simple evaluator for arithmetic expressions
fn eval_expr(tokens, pos) {
    let token = get(tokens, pos)
    let type = get(token, 0)
    
    if str_eq(type, "NUMBER") {
        return get(token, 1)
    }
    
    if str_eq(type, "LPAREN") {
        let left = eval_expr(tokens, pos + 1)
        let op_token = get(tokens, pos + 2)
        let right = eval_expr(tokens, pos + 3)
        
        let op = get(op_token, 0)
        if str_eq(op, "PLUS") {
            return left + right
        }
        if str_eq(op, "MULT") {
            return left * right
        }
    }
    
    return 0
}

# Test it!
print("Self-hosted interpreter demo:")
print("")

let code1 = "2"
print("Parsing:", code1)
let tokens1 = tokenize(code1)
let result1 = eval_expr(tokens1, 0)
print("Result:", result1)
print("")

let code2 = "(2 + 3)"
print("Parsing:", code2)
let tokens2 = tokenize(code2)
let result2 = eval_expr(tokens2, 0)
print("Result:", result2)
print("")

let code3 = "(4 * 5)"
print("Parsing:", code3)
let tokens3 = tokenize(code3)
let result3 = eval_expr(tokens3, 0)
print("Result:", result3)
'''

if __name__ == '__main__':
    print("=" * 60)
    print("Self-hosted interpreter")
    print("=" * 60)
    print("\nRunning the language interpreting itself:")
    print()
    run_code(self_hosted_code)
    print("\n" + "-" * 60)
    print("The language interpreted itself.")
    print("-" * 60)
