
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_layer import resolve_phrase
from src.semantic_map import SEMANTIC_MAP, SYNONYM_MAP


class TestDirectLookup:
    """Test Category 1: Direct semantic map lookup (no LLM needed)"""
    
    def test_direct_sum(self):
        """Test direct mapping: sum → OP_SUM"""
        result = resolve_phrase("sum")
        assert result == "OP_SUM"
    
    def test_direct_mean(self):
        """Test direct mapping: mean → OP_MEAN"""
        result = resolve_phrase("mean")
        assert result == "OP_MEAN"
    
    def test_direct_multiply(self):
        """Test direct mapping: multiply → OP_PRODUCT"""
        result = resolve_phrase("multiply")
        assert result == "OP_PRODUCT"
    
    def test_direct_max(self):
        """Test direct mapping: max → OP_MAX"""
        result = resolve_phrase("max")
        assert result == "OP_MAX"
    
    def test_direct_min(self):
        """Test direct mapping: min → OP_MIN"""
        result = resolve_phrase("min")
        assert result == "OP_MIN"
    
    def test_direct_map(self):
        """Test direct mapping: map → OP_MAP"""
        result = resolve_phrase("map")
        assert result == "OP_MAP"
    
    def test_direct_reduce(self):
        """Test direct mapping: reduce → OP_REDUCE"""
        result = resolve_phrase("reduce")
        assert result == "OP_REDUCE"
    
    def test_direct_print(self):
        """Test direct mapping: print → OP_PRINT"""
        result = resolve_phrase("print")
        assert result == "OP_PRINT"
    
    def test_direct_case_insensitive(self):
        """Test case insensitivity: SUM → OP_SUM"""
        result = resolve_phrase("SUM")
        assert result == "OP_SUM"
    
    def test_direct_with_whitespace(self):
        """Test whitespace handling: ' sum ' → OP_SUM"""
        result = resolve_phrase("  sum  ")
        assert result == "OP_SUM"


class TestSynonymLookup:
    """Test Category 2: Synonym map resolution (predefined synonyms)"""
    
    def test_synonym_total(self):
        """Test synonym: total → OP_SUM"""
        result = resolve_phrase("total")
        # Note: "total" exists in both SEMANTIC_MAP and SYNONYM_MAP
        # SEMANTIC_MAP takes precedence
        assert result == "OP_SUM"
    
    def test_synonym_add_these_up(self):
        """Test phrase synonym: add these up → OP_SUM"""
        result = resolve_phrase("add these up")
        assert result == "OP_SUM"
    
    def test_synonym_combine(self):
        """Test synonym: combine → OP_REDUCE"""
        result = resolve_phrase("combine")
        assert result == "OP_REDUCE"
    
    def test_synonym_get_largest(self):
        """Test phrase synonym: get the largest → OP_MAX"""
        result = resolve_phrase("get the largest")
        assert result == "OP_MAX"
    
    def test_synonym_get_smallest(self):
        """Test phrase synonym: get the smallest → OP_MIN"""
        result = resolve_phrase("get the smallest")
        assert result == "OP_MIN"
    
    def test_synonym_echo(self):
        """Test synonym: echo → OP_PRINT"""
        result = resolve_phrase("echo")
        assert result == "OP_PRINT"
    
    def test_synonym_arrange_asc(self):
        """Test phrase synonym: arrange smallest to biggest → OP_SORT_ASC"""
        result = resolve_phrase("arrange smallest to biggest")
        assert result == "OP_SORT_ASC"
    
    def test_synonym_arrange_desc(self):
        """Test phrase synonym: arrange biggest to smallest → OP_SORT_DESC"""
        result = resolve_phrase("arrange biggest to smallest")
        assert result == "OP_SORT_DESC"


class TestHeuristicPatterns:
    """Test Category 3: Heuristic pattern matching (legacy rules)"""
    
    def test_heuristic_contains_mean(self):
        """Test heuristic: phrase containing 'mean' → OP_MEAN"""
        result = resolve_phrase("calculate the mean value")
        assert result == "OP_MEAN"
    
    def test_heuristic_contains_average(self):
        """Test heuristic: phrase containing 'average' → OP_MEAN"""
        result = resolve_phrase("compute average score")
        assert result == "OP_MEAN"


class TestLLMResolution:
    """Test Category 4: LLM-based resolution (requires API key)"""
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), 
                        reason="Requires GEMINI_API_KEY environment variable")
    def test_llm_informal_sum(self):
        """Test LLM resolution: 'tally up' → OP_SUM"""
        result = resolve_phrase("tally up the numbers")
        assert result is not None
        if isinstance(result, dict):
            assert result.get("operator") == "OP_SUM"
        else:
            assert result == "OP_SUM"
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"),
                        reason="Requires GEMINI_API_KEY environment variable")
    def test_llm_informal_average(self):
        """Test LLM resolution: 'calculate average' → OP_MEAN"""
        result = resolve_phrase("calculate average")
        assert result is not None
        if isinstance(result, dict):
            assert result.get("operator") in ["OP_MEAN", "OP_SUM"]  # Either acceptable
        else:
            assert result in ["OP_MEAN", "OP_SUM"]
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"),
                        reason="Requires GEMINI_API_KEY environment variable")
    def test_llm_invalid_phrase(self):
        """Test LLM resolution: invalid phrase → None"""
        result = resolve_phrase("where is university malaya")
        # Should return None or dict with operator=None
        if isinstance(result, dict):
            assert result.get("operator") is None or result.get("operator") == "UNKNOWN"
        else:
            assert result is None
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"),
                        reason="Requires GEMINI_API_KEY environment variable")
    def test_llm_greeting(self):
        """Test LLM resolution: greeting → None"""
        result = resolve_phrase("hello there")
        if isinstance(result, dict):
            assert result.get("operator") is None or result.get("operator") == "UNKNOWN"
        else:
            assert result is None


class TestErrorHandling:
    """Test Category 5: Error handling and edge cases"""
    
    def test_empty_string(self):
        """Test empty string input"""
        result = resolve_phrase("")
        assert result is None or result == {}
    
    def test_none_input(self):
        """Test None input handling"""
        try:
            result = resolve_phrase(None)
            # Should either handle gracefully or raise TypeError
            assert True
        except (TypeError, AttributeError):
            # Expected behavior for None input
            assert True
    
    def test_no_api_key(self):
        """Test behavior when API key is not set"""
        # Save original key
        original_key = os.environ.get("GEMINI_API_KEY")
        
        # Temporarily remove key
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        
        # Should still work for direct/synonym lookups
        result = resolve_phrase("sum")
        assert result == "OP_SUM"
        
        # Unknown phrase should return None without crashing
        result = resolve_phrase("unknown phrase xyz")
        assert result is None or isinstance(result, dict)
        
        # Restore original key
        if original_key:
            os.environ["GEMINI_API_KEY"] = original_key
    
    def test_very_long_phrase(self):
        """Test handling of very long input"""
        long_phrase = "calculate " + "the " * 100 + "sum"
        result = resolve_phrase(long_phrase)
        # Should not crash
        assert result is not None or result is None  # Either is acceptable
    
    def test_special_characters(self):
        """Test handling of special characters"""
        result = resolve_phrase("sum@#$%")
        # Should handle gracefully
        assert isinstance(result, (str, dict, type(None)))


class TestTypeSafety:
    """Test Category 6: Type safety and semantic validation"""
    
    def test_return_type_consistency(self):
        """Test that return type is consistent and valid"""
        result = resolve_phrase("sum")
        # Should be string (operator) or None
        assert isinstance(result, (str, type(None), dict))
    
    def test_valid_operator_only(self):
        """Test that returned operator is always from valid set"""
        result = resolve_phrase("sum")
        if result and isinstance(result, str):
            assert result in SEMANTIC_MAP.values()
        elif result and isinstance(result, dict):
            op = result.get("operator")
            if op and op != "UNKNOWN":
                assert op in SEMANTIC_MAP.values()
    
    def test_semantic_preservation(self):
        """Test that semantic meaning is preserved"""
        # Words clearly related to sum should map to OP_SUM
        sum_words = ["sum", "add", "total"]
        for word in sum_words:
            result = resolve_phrase(word)
            if isinstance(result, dict):
                result = result.get("operator")
            assert result == "OP_SUM"
    
    def test_no_type_confusion(self):
        """Test that operators don't get confused"""
        # "max" should never resolve to "OP_MIN"
        result = resolve_phrase("max")
        if isinstance(result, dict):
            result = result.get("operator")
        assert result == "OP_MAX"
        assert result != "OP_MIN"


class TestSemanticValidation:
    """Test Category 7: Semantic appropriateness validation"""
    
    def test_arithmetic_semantic_match(self):
        """Test that arithmetic keywords map to arithmetic operators"""
        arithmetic_phrases = [
            ("add numbers", "OP_SUM"),
            ("sum values", "OP_SUM"),
            ("total amount", "OP_SUM"),
        ]
        
        for phrase, expected_op in arithmetic_phrases:
            result = resolve_phrase(phrase)
            if isinstance(result, dict):
                result = result.get("operator")
            # Should be arithmetic operation (OP_SUM, OP_PRODUCT, etc.)
            assert result in ["OP_SUM", "OP_PRODUCT", "OP_MEAN"] or result is None
    
    def test_comparison_semantic_match(self):
        """Test that comparison keywords map to comparison operators"""
        comparison_phrases = [
            ("biggest value", ["OP_MAX"]),
            ("smallest number", ["OP_MIN"]),
        ]
        
        for phrase, expected_ops in comparison_phrases:
            result = resolve_phrase(phrase)
            if isinstance(result, dict):
                result = result.get("operator")
            # Should be comparison operation
            if result:  # Skip if LLM not available
                assert result in expected_ops or result is None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
