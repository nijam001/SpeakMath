
import pytest
from src.lexer import lex, Token

def test_lex_simple_command():
    tokens = lex("sum 1, 2")
    # expected: SUM, SKIP(ignored), NUMBER, COMMA, SKIP, NUMBER, EOF
    # My lexer might strip skips. Let's check.
    # lexer loop: if kind == "SKIP": continue
    # So: SUM, (space skipped), NUMBER, COMMA, (space skipped), NUMBER, EOF
    
    types = [t.type for t in tokens]
    assert types == ["SUM", "NUMBER", "COMMA", "NUMBER", "EOF"]
    assert tokens[0].value == "sum"
    assert tokens[1].value == "1"

def test_lex_lists():
    tokens = lex("set x to [1, 2]")
    types = [t.type for t in tokens]
    # SET, IDENTIFIER, TO, LBRACK, NUMBER, COMMA, NUMBER, RBRACK, EOF
    assert types == ["SET", "IDENTIFIER", "TO", "LBRACK", "NUMBER", "COMMA", "NUMBER", "RBRACK", "EOF"]

def test_lex_keywords():
    tokens = lex("mean average product max min")
    types = [t.type for t in tokens]
    assert types == ["MEAN", "MEAN", "PRODUCT", "MAX", "MIN", "EOF"]

def test_lex_numbers():
    tokens = lex("123 45.67")
    assert tokens[0].type == "NUMBER"
    assert tokens[0].value == "123"
    assert tokens[1].type == "NUMBER"
    assert tokens[1].value == "45.67"

def test_lex_unknown():
    # '?' is not in spec, likely matches UNKNOWN
    tokens = lex("?")
    # The lexer loop continues on UNKNOWN unless it matches specific punctuation?
    # Spec: ("UNKNOWN", r"."), loop: if kind == "UNKNOWN": continue
    # So it should be skipped or ignored?
    # Wait, the code says: if kind == "UNKNOWN": continue. 
    # But it captures comma/brackets earlier.
    # So '?' matches UNKNOWN and is ignored.
    assert len(tokens) == 1 # Just EOF
    assert tokens[0].type == "EOF"
