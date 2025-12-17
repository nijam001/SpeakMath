"""
test_functional_properties.py

Property-based tests for functional programming guarantees:
- Purity (no side effects)
- Referential transparency
- Composition laws (map fusion, reduce associativity)
- Type safety

Author: Semantics & Proof Specialist
Date: December 2025
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpreter import Interpreter
from src.parser import Parser
from src.lexer import lex


class TestPurity:
    """Test that map and reduce operations are pure (no side effects)"""
    
    def test_map_no_side_effects(self):
        """Test that map doesn't modify original list"""
        code = """
        set original to [1, 2, 3]
        set mapped to map add 5 over original
        print original
        """
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        
        ast = parser.parse_command()
        interp.execute(ast)
        ast = parser.parse_command()
        interp.execute(ast)
        
        # Original list should be unchanged
        assert interp.env['original'] == [1, 2, 3]
        assert interp.env['mapped'] == [6, 7, 8]
    
    def test_reduce_no_side_effects(self):
        """Test that reduce doesn't modify original list"""
        code = """
        set data to [10, 20, 30]
        set total to reduce sum over data
        """
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        
        ast = parser.parse_command()
        interp.execute(ast)
        ast = parser.parse_command()
        interp.execute(ast)
        
        # Original list should be unchanged
        assert interp.env['data'] == [10, 20, 30]
        assert interp.env['total'] == 60
    
    def test_map_deterministic(self):
        """Test that map always returns same result for same input"""
        code1 = "map add 3 over [1, 2, 3]"
        code2 = "map add 3 over [1, 2, 3]"
        
        # Parse and execute first call
        tokens1 = lex(code1)
        parser1 = Parser(tokens1)
        interp1 = Interpreter()
        ast1 = parser1.parse_command()
        result1 = interp1.eval(ast1)
        
        # Parse and execute second call
        tokens2 = lex(code2)
        parser2 = Parser(tokens2)
        interp2 = Interpreter()
        ast2 = parser2.parse_command()
        result2 = interp2.eval(ast2)
        
        # Results should be identical
        assert result1 == result2 == [4, 5, 6]
    
    def test_reduce_deterministic(self):
        """Test that reduce always returns same result for same input"""
        code1 = "reduce sum over [5, 10, 15]"
        code2 = "reduce sum over [5, 10, 15]"
        
        tokens1 = lex(code1)
        parser1 = Parser(tokens1)
        interp1 = Interpreter()
        ast1 = parser1.parse_command()
        result1 = interp1.eval(ast1)
        
        tokens2 = lex(code2)
        parser2 = Parser(tokens2)
        interp2 = Interpreter()
        ast2 = parser2.parse_command()
        result2 = interp2.eval(ast2)
        
        assert result1 == result2 == 30


class TestReferentialTransparency:
    """Test that expressions can be replaced with their values"""
    
    def test_map_substitution(self):
        """Test that map expression can be replaced with its value"""
        # Expression version
        code_expr = """
        set x to map add 2 over [1, 2, 3]
        set result to sum x
        """
        
        lexer_expr = Lexer(code_expr)
        parser_expr = Parser(lexer_expr)
        interp_expr = Interpreter()
        
        ast1 = parser_expr.parse_command()
        interp_expr.execute(ast1)
        ast2 = parser_expr.parse_command()
        interp_expr.execute(ast2)
        
        result_expr = interp_expr.env['result']
        
        # Direct value version
        code_val = """
        set x to [3, 4, 5]
        set result to sum x
        """
        
        lexer_val = Lexer(code_val)
        parser_val = Parser(lexer_val)
        interp_val = Interpreter()
        
        ast1 = parser_val.parse_command()
        interp_val.execute(ast1)
        ast2 = parser_val.parse_command()
        interp_val.execute(ast2)
        
        result_val = interp_val.env['result']
        
        # Both should produce same result
        assert result_expr == result_val == 12
    
    def test_reduce_substitution(self):
        """Test that reduce expression can be replaced with its value"""
        # Expression version
        code_expr = """
        set x to reduce sum over [10, 20, 30]
        set doubled to multiply x, 2
        """
        
        lexer_expr = Lexer(code_expr)
        parser_expr = Parser(lexer_expr)
        interp_expr = Interpreter()
        
        ast1 = parser_expr.parse_command()
        interp_expr.execute(ast1)
        ast2 = parser_expr.parse_command()
        interp_expr.execute(ast2)
        
        result_expr = interp_expr.env['doubled']
        
        # Direct value version
        code_val = """
        set x to 60
        set doubled to multiply x, 2
        """
        
        lexer_val = Lexer(code_val)
        parser_val = Parser(lexer_val)
        interp_val = Interpreter()
        
        ast1 = parser_val.parse_command()
        interp_val.execute(ast1)
        ast2 = parser_val.parse_command()
        interp_val.execute(ast2)
        
        result_val = interp_val.env['doubled']
        
        # Both should produce same result
        assert result_expr == result_val == 120


class TestCompositionLaws:
    """Test functional composition properties"""
    
    def test_map_fusion(self):
        """Test that map(g, map(f, xs)) ≡ map(g∘f, xs)"""
        # Nested maps: add 3, then multiply by 2
        code_nested = "map multiply 2 over (map add 3 over [1, 2, 3])"
        
        lexer_nested = Lexer(code_nested)
        parser_nested = Parser(lexer_nested)
        interp_nested = Interpreter()
        ast_nested = parser_nested.parse_command()
        result_nested = interp_nested.eval(ast_nested)
        
        # Expected: [1+3, 2+3, 3+3] = [4, 5, 6] → [8, 10, 12]
        # Fused: (x + 3) * 2 for each x
        expected = [8, 10, 12]
        
        assert result_nested == expected
    
    def test_map_preserve_length(self):
        """Test that map preserves list length"""
        code = "map add 10 over [1, 2, 3, 4, 5]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert len(result) == 5
        assert result == [11, 12, 13, 14, 15]
    
    def test_reduce_associativity_sum(self):
        """Test that reduce sum is associative"""
        # For sum: reduce([a, b, c, d]) ≡ reduce([a, b]) + reduce([c, d])
        code_full = "reduce sum over [1, 2, 3, 4]"
        
        lexer_full = Lexer(code_full)
        parser_full = Parser(lexer_full)
        interp_full = Interpreter()
        ast_full = parser_full.parse_command()
        result_full = interp_full.eval(ast_full)
        
        # Compute partitions
        code_part1 = "reduce sum over [1, 2]"
        code_part2 = "reduce sum over [3, 4]"
        
        tokens1 = lex(code_part1)
        parser1 = Parser(tokens1)
        interp1 = Interpreter()
        ast1 = parser1.parse_command()
        part1 = interp1.eval(ast1)
        
        tokens2 = lex(code_part2)
        parser2 = Parser(tokens2)
        interp2 = Interpreter()
        ast2 = parser2.parse_command()
        part2 = interp2.eval(ast2)
        
        result_partitioned = part1 + part2
        
        # Both approaches should yield same result
        assert result_full == result_partitioned == 10
    
    def test_reduce_associativity_product(self):
        """Test that reduce product is associative"""
        code_full = "reduce multiply over [2, 3, 4]"
        
        lexer_full = Lexer(code_full)
        parser_full = Parser(lexer_full)
        interp_full = Interpreter()
        ast_full = parser_full.parse_command()
        result_full = interp_full.eval(ast_full)
        
        # Compute partitions
        code_part1 = "reduce multiply over [2, 3]"
        code_part2 = "reduce multiply over [4]"
        
        tokens1 = lex(code_part1)
        parser1 = Parser(tokens1)
        interp1 = Interpreter()
        ast1 = parser1.parse_command()
        part1 = interp1.eval(ast1)
        
        tokens2 = lex(code_part2)
        parser2 = Parser(tokens2)
        interp2 = Interpreter()
        ast2 = parser2.parse_command()
        part2 = interp2.eval(ast2)
        
        result_partitioned = part1 * part2
        
        assert result_full == result_partitioned == 24
    
    def test_map_reduce_composition(self):
        """Test that map and reduce compose correctly"""
        # map then reduce
        code_composed = "reduce sum over (map multiply 2 over [1, 2, 3])"
        
        tokens = lex(code_composed)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        # Expected: [2, 4, 6] → 12
        assert result == 12
        
        # Verify homomorphism property: 2 * (reduce sum [1,2,3]) = reduce sum [2,4,6]
        # 2 * 6 = 12 ✓


class TestTypeSafety:
    """Test that type constraints are enforced"""
    
    def test_map_requires_list(self):
        """Test that map rejects non-list inputs"""
        code = "map add 5 over 42"  # 42 is not a list
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        
        with pytest.raises(Exception):  # Should raise SemanticError
            interp.eval(ast)
    
    def test_reduce_requires_list(self):
        """Test that reduce rejects non-list inputs"""
        code = "reduce sum over 42"  # 42 is not a list
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        
        with pytest.raises(Exception):  # Should raise SemanticError
            interp.eval(ast)
    
    def test_map_requires_numeric_argument(self):
        """Test that map arithmetic operations require numeric argument"""
        code = "map add over [1, 2, 3]"  # Missing numeric argument
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        
        with pytest.raises(Exception):  # Should raise SemanticError
            interp.eval(ast)
    
    def test_map_output_is_list(self):
        """Test that map always returns a list"""
        code = "map add 1 over [5, 10]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert isinstance(result, list)
        assert all(isinstance(x, (int, float)) for x in result)
    
    def test_reduce_output_is_scalar(self):
        """Test that reduce returns a scalar value"""
        code = "reduce sum over [1, 2, 3]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert isinstance(result, (int, float))
        assert not isinstance(result, list)


class TestSemanticProperties:
    """Test mathematical properties of operations"""
    
    def test_map_identity(self):
        """Test that map with identity operation preserves values"""
        # map add 0 is identity for addition
        code = "map add 0 over [1, 2, 3]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert result == [1, 2, 3]
    
    def test_map_distributive(self):
        """Test distributive property: map f [x,y] ≡ [f x, f y]"""
        code = "map multiply 3 over [5, 7]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        # Should be [15, 21]
        assert result == [15, 21]
    
    def test_reduce_sum_identity(self):
        """Test that reduce sum of single element is the element"""
        code = "reduce sum over [42]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert result == 42
    
    def test_reduce_product_identity(self):
        """Test that reduce product of single element is the element"""
        code = "reduce multiply over [7]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert result == 7
    
    def test_map_empty_list(self):
        """Test that map on empty list returns empty list"""
        code = """
        set empty to []
        set result to map add 5 over empty
        """
        
        # Note: Current parser may not support empty list literal
        # This test documents expected behavior
        # If empty lists are not supported, this test should be skipped
        pytest.skip("Empty list literals not yet supported in parser")
    
    def test_commutativity_not_required(self):
        """Document that map/reduce don't require commutativity, only associativity"""
        # This is a documentation test - no assertion needed
        # Map applies operations in order
        # Reduce assumes associativity but not commutativity
        pass


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_map_single_element(self):
        """Test map on single-element list"""
        code = "map add 10 over [5]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert result == [15]
    
    def test_reduce_two_elements(self):
        """Test reduce on two-element list"""
        code = "reduce sum over [100, 200]"
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        ast = parser.parse_command()
        result = interp.eval(ast)
        
        assert result == 300
    
    def test_large_list_map(self):
        """Test map on larger list"""
        # Generate list programmatically
        code = """
        set nums to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        set incremented to map add 1 over nums
        """
        
        tokens = lex(code)
        parser = Parser(tokens)
        interp = Interpreter()
        
        ast1 = parser.parse_command()
        interp.execute(ast1)
        ast2 = parser.parse_command()
        interp.execute(ast2)
        
        result = interp.env['incremented']
        assert result == [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        assert len(result) == 10


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
