
import pytest
from src import ast 
from src.parser import Parser
from src.lexer import lex, Token

# Helper to parse a string
def parse(text):
    tokens = lex(text)
    return Parser(tokens).parse()

def test_parse_sum():
    node = parse("sum 1, 2, 3")
    assert isinstance(node, ast.ComputeNode)
    assert node.op == "OP_SUM"
    assert isinstance(node.target, ast.ListNode)
    assert len(node.target.values) == 3

def test_parse_set():
    node = parse("set x to 10")
    assert isinstance(node, ast.AssignNode)
    assert node.varname == "x"
    assert isinstance(node.expr, ast.NumberNode)
    assert node.expr.value == 10

def test_parse_expression_precedence():
    # 2 + 3 * 4 should be 2 + (3 * 4) = 14
    node = parse("set z to 2 + 3 * 4")
    expr = node.expr
    # Top level should be Add (2, Mul(3,4))
    assert isinstance(expr, ast.BinaryOpNode)
    assert expr.op == "+"
    assert isinstance(expr.left, ast.NumberNode)
    assert expr.left.value == 2
    assert isinstance(expr.right, ast.BinaryOpNode)
    assert expr.right.op == "*"

def test_parse_list_bracket():
    node = parse("sum [1, 2, 3]")
    assert isinstance(node.target, ast.ListNode)

def test_parse_map_simple():
    # map add 2 over [1,2]
    node = parse("map add 2 over [1,2]")
    assert isinstance(node, ast.MapNode)
    assert node.op == "OP_SUM" # "add" maps to OP_SUM in map context logic?
    # Logic in parser: resolve_phrase("add") -> OP_SUM. 
    # Parser: op = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_MAP")
    assert node.arg == 2.0
    assert isinstance(node.target, ast.ListNode)

def test_parse_error():
    with pytest.raises(Exception):
        parse("set 1 to 2") # Syntax error, expected Identifier
