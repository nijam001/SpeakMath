# test_grammar_first.py
"""
Test cases to verify that functional constructs (map/reduce) 
remain grammar-first and do not rely on LLM unnecessarily.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer import lex
from parser import Parser
import ast

def test_map_without_llm():
    """Test that 'map' keyword is always handled by grammar"""
    input_text = "map add 2 over [1, 2, 3]"
    tokens = lex(input_text)
    parser = Parser(tokens)
    result = parser.parse()
    
    # Should be MapNode
    assert isinstance(result, ast.MapNode), f"Expected MapNode, got {type(result)}"
    
    # Should NOT be LLM-resolved (add is in SEMANTIC_MAP)
    assert not result.is_llm_resolved, "map add should not use LLM"
    
    print("✅ test_map_without_llm passed")

def test_reduce_without_llm():
    """Test that 'reduce' keyword is always handled by grammar"""
    input_text = "reduce sum over [1, 2, 3, 4]"
    tokens = lex(input_text)
    parser = Parser(tokens)
    result = parser.parse()
    
    # Should be ReduceNode
    assert isinstance(result, ast.ReduceNode), f"Expected ReduceNode, got {type(result)}"
    
    # Should NOT be LLM-resolved (sum is in SEMANTIC_MAP)
    assert not result.is_llm_resolved, "reduce sum should not use LLM"
    
    print("✅ test_reduce_without_llm passed")

def test_map_with_novel_op():
    """Test that map can use LLM for novel operations within"""
    input_text = "map increment 5 over [10, 20, 30]"
    tokens = lex(input_text)
    parser = Parser(tokens)
    result = parser.parse()
    
    # Should be MapNode
    assert isinstance(result, ast.MapNode), f"Expected MapNode, got {type(result)}"
    
    # Structure should be grammar-parsed, but op might be LLM-resolved
    # The important thing is MAP token itself is from grammar
    assert result.arg == 5.0, f"Expected arg=5, got {result.arg}"
    
    print("✅ test_map_with_novel_op passed")

def test_functional_keywords_are_tokens():
    """Verify MAP and REDUCE are lexer tokens, not identifiers"""
    input_text = "map sum over data"
    tokens = lex(input_text)
    
    # First token should be MAP, not IDENTIFIER
    assert tokens[0].type == "MAP", f"Expected MAP token, got {tokens[0].type}"
    
    input_text2 = "reduce product over values"
    tokens2 = lex(input_text2)
    
    # First token should be REDUCE
    assert tokens2[0].type == "REDUCE", f"Expected REDUCE token, got {tokens2[0].type}"
    
    print("✅ test_functional_keywords_are_tokens passed")

def test_known_operations_skip_llm():
    """Test that known operations don't trigger LLM"""
    test_cases = [
        ("sum [1,2,3]", ast.ComputeNode),
        ("mean [10, 20, 30]", ast.ComputeNode),
        ("max [5, 10, 15]", ast.ComputeNode),
        ("product [2, 3, 4]", ast.ComputeNode),
    ]
    
    for input_text, expected_type in test_cases:
        tokens = lex(input_text)
        parser = Parser(tokens)
        result = parser.parse()
        
        assert isinstance(result, expected_type), f"For '{input_text}': expected {expected_type}, got {type(result)}"
        assert not result.is_llm_resolved, f"For '{input_text}': should not use LLM"
    
    print("✅ test_known_operations_skip_llm passed")

if __name__ == "__main__":
    print("Running Grammar-First Tests...\n")
    
    try:
        test_map_without_llm()
        test_reduce_without_llm()
        test_map_with_novel_op()
        test_functional_keywords_are_tokens()
        test_known_operations_skip_llm()
        
        print("\n" + "="*50)
        print("✅ All Grammar-First tests passed!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
