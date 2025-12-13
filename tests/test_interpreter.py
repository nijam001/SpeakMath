
import pytest
from src import ast 
from src.interpreter import Interpreter
from src.parser import Parser
from src.lexer import lex

def run(text):
    interp = Interpreter()
    tokens = lex(text)
    node = Parser(tokens).parse()
    return interp.eval(node)

def test_eval_math():
    interp = Interpreter()
    assert interp.eval(ast.BinaryOpNode(ast.NumberNode(2), "+", ast.NumberNode(3))) == 5
    assert interp.eval(ast.BinaryOpNode(ast.NumberNode(10), "/", ast.NumberNode(2))) == 5.0

def test_run_assign_variable():
    interp = Interpreter()
    # set x to 10
    tokens = lex("set x to 10")
    node = Parser(tokens).parse()
    interp.eval(node)
    assert interp.vars["x"] == 10
    
    # sum x
    # We need to test referencing that variable
    # But Interpreter instance must allow separate eval calls safely? 
    # The default 'run' helper creates new interp each time. Let's do manual steps.
    
    tokens2 = lex("set y to x + 5") 
    node2 = Parser(tokens2).parse()
    val = interp.eval(node2)
    assert val == 15
    assert interp.vars["y"] == 15

def test_compute_stats():
    assert run("mean 1, 2, 3") == 2.0
    assert run("sum 1, 2, 3") == 6
    assert run("max 1, 5, 2") == 5

def test_map_add():
    res = run("map add 5 over [1, 2, 3]")
    assert res == [6.0, 7.0, 8.0] # Internal math might float

def test_reduce_multiply():
    res = run("reduce multiply over [1, 2, 3, 4]")
    assert res == 24 # 1*2*3*4

def test_sort():
    res = run("sort ascending [3, 1, 2]")
    assert res == [1, 2, 3]
    res2 = run("sort descending [3, 1, 2]")
    assert res2 == [3, 2, 1]
