# SpeakMath single-file version

# semantic_map

# semantic_map.py
SEMANTIC_MAP = {
    # canonical single-word mappings
    "sum": "OP_SUM",
    "add": "OP_SUM",
    "total": "OP_SUM",
    "mean": "OP_MEAN",
    "average": "OP_MEAN",
    "find the mean": "OP_MEAN",
    "product": "OP_PRODUCT",
    "multiply": "OP_PRODUCT",
    "max": "OP_MAX",
    "min": "OP_MIN",
    "sort ascending": "OP_SORT_ASC",
    "sort descending": "OP_SORT_DESC",
    "sort": "OP_SORT_ASC",
    "map": "OP_MAP",
    "reduce": "OP_REDUCE",
    "print": "OP_PRINT",
    "set": "OP_ASSIGN",
    "if": "OP_IF",
}

# synonyms / phrases that may need LLM or rule-based normalization
SYNONYM_MAP = {
    "total": "OP_SUM",
    "add these up": "OP_SUM",
    "combine": "OP_REDUCE",
    "collapse list": "OP_REDUCE",
    "double each value": "OP_MAP",  # implies map multiply 2
    "increment each by 2": "OP_MAP", # implies map add 2
    "arrange smallest to biggest": "OP_SORT_ASC",
    "arrange biggest to smallest": "OP_SORT_DESC",
    "get the largest": "OP_MAX",
    "get the smallest": "OP_MIN",
    "echo": "OP_PRINT",
    "show output": "OP_PRINT",
}


# llm_layer

# llm_layer.py (stubbed LLM resolver)
# llm_layer.py (stubbed LLM resolver)
# from .semantic_map import SYNONYM_MAP, SEMANTIC_MAP

def resolve_phrase(phrase: str) -> str:
    """
    Resolve a verb phrase to a canonical operator token.
    First check direct mapping, then synonym map; otherwise return None
    indicating LLM should be consulted (stubbed).
    """
    key = phrase.lower().strip()
    if key in SEMANTIC_MAP:
        return SEMANTIC_MAP[key]
    if key in SYNONYM_MAP:
        return SYNONYM_MAP[key]
    # simple heuristics for patterns:
    if key.startswith("find the mean") or "mean" in key:
        return "OP_MEAN"
    if "average" in key:
        return "OP_MEAN"
    # No match: return None to indicate LLM fallback in real system
    return None


# lexer

# lexer.py
import re
from typing import List
# from .semantic_map import SEMANTIC_MAP

TOKEN_SPEC = [
    ("NUMBER",       r"\d+(\.\d+)?"),
    ("COMMA",        r","),
    ("LBRACK",       r"\["),
    ("RBRACK",       r"\]"),
    ("LPAREN",       r"\("),
    ("RPAREN",       r"\)"),
    ("OPERATOR",     r"(==|!=|>=|<=|>|<)"),
    ("ADDOP",        r"(\+|\-)"),
    ("MULOP",        r"(\*|/)"),
    ("SET",          r"\bset\b"),
    ("TO",           r"\bto\b"),
    ("IF",           r"\bif\b"),
    ("THEN",         r"\bthen\b"),
    ("MAP",          r"\bmap\b"),
    ("REDUCE",       r"\breduce\b"),
    ("SUM",          r"\bsum\b"),
    ("MEAN",         r"\b(mean|average|find the mean)\b"),
    ("PRODUCT",      r"\b(product|multiply)\b"),
    ("MAX",          r"\bmax\b"),
    ("MIN",          r"\bmin\b"),
    ("SORT_ASC",     r"\bsort\s+ascending\b"),
    ("SORT_DESC",    r"\bsort\s+descending\b"),
    ("PRINT",        r"\bprint\b"),
    ("OVER_ON",      r"\b(over|on)\b"),
    ("IDENTIFIER",   r"[A-Za-z_][A-Za-z0-9_]*"),
    ("SKIP",         r"[ \t\r\n]+"),
    ("UNKNOWN",      r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{n}>{p})" for n,p in TOKEN_SPEC), re.IGNORECASE)

class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def lex(text: str):
    tokens = []
    for mo in MASTER_RE.finditer(text):
        kind = mo.lastgroup
        val = mo.group().strip()
        pos = mo.start()
        if kind == "SKIP":
            continue
        if kind == "UNKNOWN":
            # ignore stray punctuation usually, but include comma/brackets handled above
            continue
        tokens.append(Token(kind, val, pos))
    tokens.append(Token("EOF","",len(text)))
    return tokens


# ast

# ast.py
class ASTNode:
    pass

class CommandNode(ASTNode):
    def __init__(self, cmd):
        self.cmd = cmd
    def __repr__(self):
        return f"CommandNode({self.cmd})"

class ComputeNode(ASTNode):
    def __init__(self, op, target):
        self.op = op  # canonical op, e.g., OP_SUM
        self.target = target
    def __repr__(self):
        return f"ComputeNode({self.op}, {self.target})"

class AssignNode(ASTNode):
    def __init__(self, varname, expr):
        self.varname = varname
        self.expr = expr
    def __repr__(self):
        return f"AssignNode({self.varname}, {self.expr})"

class IfNode(ASTNode):
    def __init__(self, left, comp, right, action):
        self.left = left
        self.comp = comp
        self.right = right
        self.action = action
    def __repr__(self):
        return f"IfNode({self.left} {self.comp} {self.right} then {self.action})"

class PrintNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"PrintNode({self.expr})"

class ListNode(ASTNode):
    def __init__(self, values):
        self.values = values
    def __repr__(self):
        return f"ListNode({self.values})"

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"NumberNode({self.value})"

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"VariableNode({self.name})"

class BinaryOpNode(ASTNode):
    def __init__(self,left,op,right):
        self.left=left; self.op=op; self.right=right
    def __repr__(self):
        return f"BinaryOpNode({self.left} {self.op} {self.right})"

class MapNode(ASTNode):
    def __init__(self, op, arg, target):
        self.op = op  # canonical or operation name
        self.arg = arg
        self.target = target
    def __repr__(self):
        return f"MapNode({self.op}, {self.arg}, {self.target})"

class ReduceNode(ASTNode):
    def __init__(self, op, target):
        self.op = op
        self.target = target
    def __repr__(self):
        return f"ReduceNode({self.op}, {self.target})"

class SequenceNode(ASTNode):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def __repr__(self):
        return f"SequenceNode({self.first} then {self.second})"


# parser

# Emulate ast module for single-file version
class ast:
    ASTNode = ASTNode
    CommandNode = CommandNode
    ComputeNode = ComputeNode
    AssignNode = AssignNode
    IfNode = IfNode
    PrintNode = PrintNode
    ListNode = ListNode
    NumberNode = NumberNode
    VariableNode = VariableNode
    BinaryOpNode = BinaryOpNode
    MapNode = MapNode
    ReduceNode = ReduceNode
    SequenceNode = SequenceNode

# parser.py
from typing import List
# from .lexer import Token, lex
# from . import ast
# from .llm_layer import resolve_phrase
# from .semantic_map import SEMANTIC_MAP

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos]

    def eat(self, ttype):
        c = self.cur()
        if c.type == ttype:
            self.pos += 1
            return c
        raise ParseError(f"Expected {ttype} got {c.type} ({c.value}) at {c.pos}")

    def look(self, offset=0):
        i = self.pos + offset
        if i < len(self.tokens):
            return self.tokens[i]
        return Token("EOF","",len(self.tokens))

    def parse(self):
        node = self.parse_command()
        if self.cur().type != "EOF":
            raise ParseError("Trailing tokens after command: "+str(self.cur()))
        return node

    def parse_command(self):
        c = self.cur()
        if c.type == "SET":
            return self.parse_assign()
        if c.type == "IF":
            return self.parse_if()
        if c.type == "PRINT":
            self.eat("PRINT")
            expr = self.parse_expression_or_target()
            return ast.PrintNode(expr)
        if c.type == "MAP":
            return self.parse_map()
        if c.type == "REDUCE":
            return self.parse_reduce()
        # compute keywords
        if c.type in ("SUM","MEAN","PRODUCT","MAX","MIN","SORT_ASC","SORT_DESC"):
            token = self.eat(c.type)
            phrase = token.value.lower()
            op = resolve_phrase(phrase) or SEMANTIC_MAP.get(phrase, None)
            if not op:
                raise ParseError("Unknown verb: "+phrase)
            target = self.parse_expression_or_target()
            return ast.ComputeNode(op, target)
        # identifier as verb?
        if c.type == "IDENTIFIER":
            # try treating identifier as verb phrase
            phrase = c.value.lower()
            op = resolve_phrase(phrase) or SEMANTIC_MAP.get(phrase)
            if op:
                self.eat("IDENTIFIER")
                target = self.parse_expression_or_target()
                return ast.ComputeNode(op, target)
        raise ParseError("Unknown command start: "+str(c))

    def parse_assign(self):
        self.eat("SET")
        var = self.eat("IDENTIFIER").value
        self.eat("TO")
        expr = self.parse_expression()
        return ast.AssignNode(var, expr)

    def parse_if(self):
        self.eat("IF")
        left = self.parse_expression()
        comp = self.eat("OPERATOR").value
        right = self.parse_expression()
        self.eat("THEN")
        action = self.parse_command()
        return ast.IfNode(left, comp, right, action)

    def parse_map(self):
        self.eat("MAP")
        # next token should be operation (identifier or keywords)
        op_tok = self.cur()
        if op_tok.type in ("IDENTIFIER","SUM","PRODUCT"):
            op_phrase = self.eat(op_tok.type).value.lower()
        else:
            raise ParseError("Expected operation after map")
        # optional numeric arg
        arg = None
        if self.cur().type == "NUMBER":
            arg = float(self.eat("NUMBER").value)
        if self.cur().type == "OVER_ON":
            self.eat("OVER_ON")
        target = self.parse_expression_or_target()
        # normalize op to canonical via resolve_phrase
        op = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_MAP")
        return ast.MapNode(op, arg, target)

    def parse_reduce(self):
        self.eat("REDUCE")
        op_tok = self.cur()
        if op_tok.type in ("IDENTIFIER","SUM","PRODUCT"):
            op_phrase = self.eat(op_tok.type).value.lower()
        else:
            raise ParseError("Expected operation after reduce")
        if self.cur().type == "OVER_ON":
            self.eat("OVER_ON")
        target = self.parse_expression_or_target()
        op = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_REDUCE")
        return ast.ReduceNode(op, target)

    def parse_expression_or_target(self):
        c = self.cur()
        if c.type == "LBRACK":
            return self.parse_list_bracket()
        if c.type == "NUMBER":
            if self.look(1).type == "COMMA":
                return self.parse_list_shorthand()
            return self.parse_expression()
        if c.type == "IDENTIFIER":
            return ast.VariableNode(self.eat("IDENTIFIER").value)
        if c.type == "LPAREN":
            return self.parse_expression()
        return self.parse_expression()

    def parse_list_bracket(self):
        self.eat("LBRACK")
        vals = []
        if self.cur().type != "RBRACK":
            vals.append(self.parse_number_literal())
            while self.cur().type == "COMMA":
                self.eat("COMMA"); vals.append(self.parse_number_literal())
        self.eat("RBRACK")
        return ast.ListNode(vals)

    def parse_list_shorthand(self):
        vals = [self.parse_number_literal()]
        while self.cur().type == "COMMA":
            self.eat("COMMA"); vals.append(self.parse_number_literal())
        return ast.ListNode(vals)

    def parse_number_literal(self):
        tok = self.eat("NUMBER")
        if "." in tok.value:
            return ast.NumberNode(float(tok.value))
        return ast.NumberNode(int(tok.value))

    def parse_expression(self):
        node = self.parse_term()
        while self.cur().type == "ADDOP":
            op = self.eat("ADDOP").value
            right = self.parse_term()
            node = ast.BinaryOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.cur().type == "MULOP":
            op = self.eat("MULOP").value
            right = self.parse_factor()
            node = ast.BinaryOpNode(node, op, right)
        return node

    def parse_factor(self):
        c = self.cur()
        if c.type == "NUMBER":
            return self.parse_number_literal()
        if c.type == "IDENTIFIER":
            return ast.VariableNode(self.eat("IDENTIFIER").value)
        if c.type == "LPAREN":
            self.eat("LPAREN"); node = self.parse_expression(); self.eat("RPAREN"); return node
        if c.type == "LBRACK":
            return self.parse_list_bracket()
        raise ParseError("Unexpected token in factor: "+str(c))


# interpreter

# interpreter.py
# from . import ast
# from .semantic_map import SEMANTIC_MAP
from typing import Any

class SemanticError(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.vars = {}

    def eval(self, node: ast.ASTNode) -> Any:
        if isinstance(node, ast.NumberNode):
            return node.value
        if isinstance(node, ast.VariableNode):
            if node.name not in self.vars:
                raise SemanticError(f"Undefined variable: {node.name}")
            return self.vars[node.name]
        if isinstance(node, ast.ListNode):
            return [self.eval(v) for v in node.values]
        if isinstance(node, ast.BinaryOpNode):
            l = self.eval(node.left); r = self.eval(node.right)
            if node.op == "+": return l + r
            if node.op == "-": return l - r
            if node.op == "*": return l * r
            if node.op == "/": return l / r
            raise SemanticError("Unknown binary op: "+str(node.op))
        if isinstance(node, ast.AssignNode):
            val = self.eval(node.expr)
            self.vars[node.varname] = val
            return val
        if isinstance(node, ast.PrintNode):
            val = self.eval(node.expr)
            print(val)
            return val
        if isinstance(node, ast.ComputeNode):
            return self.execute_compute(node.op, node.target)
        if isinstance(node, ast.MapNode):
            return self.execute_map(node)
        if isinstance(node, ast.ReduceNode):
            return self.execute_reduce(node)
        if isinstance(node, ast.IfNode):
            l = self.eval(node.left); r = self.eval(node.right)
            if self.compare(l, r, node.comp):
                return self.eval(node.action)
            return None
        if isinstance(node, ast.SequenceNode):
            first_out = self.eval(node.first)
            # when second expects input, if it is a ComputeNode with target variable, pass list
            # we'll support composition where second uses result of first as its implicit input
            # For simplicity: if second is ComputeNode and its target is VariableNode named "_" then replace it
            if isinstance(node.second, ast.ComputeNode) and isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                node.second.target = ast.ListNode([ast.NumberNode(x) for x in first_out])
                return self.eval(node.second)
            # otherwise just evaluate second normally, allowing side-effects
            return self.eval(node.second)
        raise SemanticError("Unhandled AST node: "+str(node))

    def compare(self, l, r, comp):
        if comp == ">": return l > r
        if comp == "<": return l < r
        if comp == "==": return l == r
        if comp == "!=": return l != r
        if comp == ">=": return l >= r
        if comp == "<=": return l <= r
        raise SemanticError("Unknown comparator: "+str(comp))

    def ensure_numeric_list(self, lst):
        if not isinstance(lst, list):
            raise SemanticError("Expected list for operation")
        if len(lst) == 0:
            raise SemanticError("List must be non-empty")
        for x in lst:
            if not isinstance(x, (int, float)):
                raise SemanticError("List must be numeric")
        return True

    def execute_compute(self, op, target):
        # target can be AST node
        tval = self.eval(target) if hasattr(target, '__class__') else target
        # if target is a scalar, wrap?
        if isinstance(tval, (int,float)):
            return tval
        if op == "OP_SUM":
            self.ensure_numeric_list(tval); return sum(tval)
        if op == "OP_MEAN":
            self.ensure_numeric_list(tval); return sum(tval)/len(tval)
        if op == "OP_PRODUCT":
            self.ensure_numeric_list(tval)
            prod=1
            for x in tval: prod*=x
            return prod
        if op == "OP_MAX":
            self.ensure_numeric_list(tval); return max(tval)
        if op == "OP_MIN":
            self.ensure_numeric_list(tval); return min(tval)
        if op == "OP_SORT_ASC":
            if not isinstance(tval, list): raise SemanticError("Sort target must be list")
            return sorted(tval)
        if op == "OP_SORT_DESC":
            if not isinstance(tval, list): raise SemanticError("Sort target must be list")
            return sorted(tval, reverse=True)
        raise SemanticError("Unknown compute op: "+str(op))

    def execute_map(self, node: ast.MapNode):
        tval = self.eval(node.target)
        self.ensure_numeric_list(tval)
        op = node.op
        arg = node.arg if node.arg is not None else None
        out = []
        if op == "OP_MAP" or op == "map" or op == "OP_MAP_ADD" or op == "OP_SUM":
            # default map must have arg for arithmetic add/mul; we'll support basic ops through op string
            for x in tval:
                if arg is None: raise SemanticError("Map requires numeric argument for arithmetic")
                out.append(x + arg)
            return out
        # if op maps to OP_MAP with inner meaning like OP_MAP_MULTIPLY
        if op in ("multiply","product","op_product","OP_PRODUCT"):
            if arg is None: raise SemanticError("Map multiply requires argument")
            for x in tval: out.append(x * arg)
            return out
        # support simple verbs "add" and "multiply"
        if op == "add":
            if arg is None: raise SemanticError("Map add requires argument")
            for x in tval: out.append(x + arg)
            return out
        if op == "multiply":
            if arg is None: raise SemanticError("Map multiply requires argument")
            for x in tval: out.append(x * arg)
            return out
        raise SemanticError("Unknown map op: "+str(op))

    def execute_reduce(self, node: ast.ReduceNode):
        tval = self.eval(node.target)
        self.ensure_numeric_list(tval)
        op = node.op
        if op in ("OP_REDUCE","reduce","op_reduce"):
            # default: sum
            return sum(tval)
        if op in ("add","sum","OP_SUM"):
            return sum(tval)
        if op in ("multiply","product","OP_PRODUCT"):
            prod=1
            for x in tval: prod*=x
            return prod
        raise SemanticError("Unknown reduce op: "+str(op))


# simple demo

# main.py - demo CLI for speakmath package
# Imports removed for single-file version

def run_command(text, interp=None):
    if interp is None:
        interp = Interpreter()
    toks = lex(text)
    parser = Parser(toks)
    ast = parser.parse()
    return interp.eval(ast), interp

def demo():
    interp = Interpreter()
    examples = [
        "set x to 5",
        "set nums to [1,2,3,4]",
        "print nums",
        "sum nums",
        "mean nums",
        "product nums",
        "map add 2 over nums",
        "reduce multiply over nums",
        "if 5 > 3 then print 99",
    ]
    print('--- Demo run ---')
    for ex in examples:
        print('> ', ex)
        try:
            out, interp = run_command(ex, interp)
            if out is not None:
                print('=>', out)
        except Exception as e:
            print('ERROR:', e)
    print('--- End demo ---')

def repl():
    print("SpeakMath Interactive REPL")
    print("Type 'exit' or 'quit' to leave.")
    interp = Interpreter()
    while True:
        try:
            text = input(">> ")
            if text.lower() in ("exit", "quit"):
                break
            if not text.strip():
                continue
            out, interp = run_command(text, interp)
            if out is not None:
                print("=>", out)
        except Exception as e:
            print("ERROR:", e)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo()
    else:
        repl()


