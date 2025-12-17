"""
test_performance_llm.py

Performance benchmarks for LLM integration (D4).
Compares LLM resolution vs direct lookup performance.

Author: Evaluation & Documentation Lead / Runtime Engineer
"""

import time
import statistics
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_layer import resolve_phrase
from src.semantic_map import SEMANTIC_MAP, SYNONYM_MAP


class TestLLMPerformance:
    """Benchmark LLM resolution performance"""
    
    def test_direct_lookup_performance(self):
        """Benchmark direct semantic map lookup"""
        test_phrases = ["sum", "mean", "product", "max", "min"] * 100
        
        times = []
        for phrase in test_phrases:
            start = time.perf_counter()
            result = resolve_phrase(phrase)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n=== Direct Lookup Performance ===")
        print(f"Average: {avg_time:.4f} ms")
        print(f"Median: {median_time:.4f} ms")
        print(f"Min: {min_time:.4f} ms")
        print(f"Max: {max_time:.4f} ms")
        print(f"Total operations: {len(times)}")
        
        # Direct lookup should be very fast (< 1ms typically)
        assert avg_time < 1.0, f"Direct lookup too slow: {avg_time}ms"
    
    @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"),
                        reason="Requires GEMINI_API_KEY for LLM benchmarks")
    def test_llm_resolution_performance(self):
        """Benchmark LLM-based resolution performance"""
        test_phrases = [
            "tally up the numbers",
            "calculate the average",
            "find the total",
            "get the maximum value",
            "what's the smallest number"
        ] * 10  # Run each phrase 10 times
        
        times = []
        successes = 0
        
        for phrase in test_phrases:
            start = time.perf_counter()
            result = resolve_phrase(phrase)
            end = time.perf_counter()
            elapsed = (end - start) * 1000  # Convert to milliseconds
            times.append(elapsed)
            if result is not None:
                successes += 1
        
        avg_time = statistics.mean(times)
        median_time = statistics.median(times)
        max_time = max(times)
        min_time = min(times)
        success_rate = (successes / len(times)) * 100
        
        print(f"\n=== LLM Resolution Performance ===")
        print(f"Average: {avg_time:.4f} ms")
        print(f"Median: {median_time:.4f} ms")
        print(f"Min: {min_time:.4f} ms")
        print(f"Max: {max_time:.4f} ms")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Total operations: {len(times)}")
        
        # LLM calls should complete within timeout (5000ms)
        assert max_time < 6000, f"LLM call exceeded timeout: {max_time}ms"
    
    def test_synonym_lookup_performance(self):
        """Benchmark synonym map lookup performance"""
        test_phrases = ["total", "add these up", "combine", "get the largest"] * 100
        
        times = []
        for phrase in test_phrases:
            start = time.perf_counter()
            result = resolve_phrase(phrase)
            end = time.perf_counter()
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        print(f"\n=== Synonym Lookup Performance ===")
        print(f"Average: {avg_time:.4f} ms")
        
        # Synonym lookup should be fast (< 1ms)
        assert avg_time < 1.0, f"Synonym lookup too slow: {avg_time}ms"
    
    def test_performance_comparison(self):
        """Compare direct lookup vs LLM resolution"""
        direct_phrases = ["sum", "mean", "product"] * 50
        llm_phrases = ["tally up", "calculate average", "multiply all"] * 5
        
        # Direct lookup
        direct_times = []
        for phrase in direct_phrases:
            start = time.perf_counter()
            resolve_phrase(phrase)
            direct_times.append((time.perf_counter() - start) * 1000)
        
        direct_avg = statistics.mean(direct_times)
        
        # LLM lookup (if available)
        llm_avg = None
        if os.getenv("GEMINI_API_KEY"):
            llm_times = []
            for phrase in llm_phrases:
                start = time.perf_counter()
                resolve_phrase(phrase)
                llm_times.append((time.perf_counter() - start) * 1000)
            llm_avg = statistics.mean(llm_times)
        
        print(f"\n=== Performance Comparison ===")
        print(f"Direct lookup average: {direct_avg:.4f} ms")
        if llm_avg:
            print(f"LLM lookup average: {llm_avg:.4f} ms")
            speedup = llm_avg / direct_avg
            print(f"Direct lookup is {speedup:.2f}x faster")
        
        assert direct_avg < 1.0


class TestLLMFallbackRates:
    """Measure LLM fallback rates and accuracy"""
    
    def test_fallback_rate_measurement(self):
        """Measure how often LLM fallback is used"""
        test_cases = {
            "direct": ["sum", "mean", "product", "max", "min"],
            "synonym": ["total", "average", "multiply", "largest", "smallest"],
            "heuristic": ["calculate the mean", "find the average"],
            "llm_fallback": ["tally up numbers", "compute total sum", "get the biggest"]
        }
        
        results = {
            "direct": 0,
            "synonym": 0,
            "heuristic": 0,
            "llm_fallback": 0,
            "failed": 0
        }
        
        for category, phrases in test_cases.items():
            for phrase in phrases:
                result = resolve_phrase(phrase)
                if result is None:
                    results["failed"] += 1
                elif category == "direct" and result in SEMANTIC_MAP.values():
                    results["direct"] += 1
                elif category == "synonym" and phrase in SYNONYM_MAP:
                    results["synonym"] += 1
                elif category == "heuristic":
                    results["heuristic"] += 1
                elif category == "llm_fallback":
                    results["llm_fallback"] += 1
        
        total = sum(results.values())
        
        print(f"\n=== Fallback Rate Analysis ===")
        for category, count in results.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{category}: {count} ({percentage:.2f}%)")
        
        # Most should be resolved without LLM
        direct_rate = results["direct"] / total if total > 0 else 0
        assert direct_rate > 0.3, "Too few direct lookups"


class TestRuntimeBehavior:
    """Test runtime behavior with/without LLM"""
    
    def test_runtime_without_llm(self):
        """Test that system works without LLM (graceful degradation)"""
        original_key = os.environ.get("GEMINI_API_KEY")
        
        # Temporarily remove API key
        if "GEMINI_API_KEY" in os.environ:
            del os.environ["GEMINI_API_KEY"]
        
        # Direct lookups should still work
        assert resolve_phrase("sum") == "OP_SUM"
        assert resolve_phrase("mean") == "OP_MEAN"
        
        # Synonym lookups should work
        assert resolve_phrase("total") == "OP_SUM"
        
        # Heuristic should work
        assert resolve_phrase("calculate the mean") == "OP_MEAN"
        
        # LLM fallback should return None gracefully
        result = resolve_phrase("tally up the numbers")
        assert result is None or isinstance(result, dict)
        
        # Restore API key
        if original_key:
            os.environ["GEMINI_API_KEY"] = original_key
    
    def test_runtime_with_llm(self):
        """Test runtime behavior when LLM is available"""
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("Requires GEMINI_API_KEY")
        
        # Should resolve unknown phrases
        result = resolve_phrase("tally up the numbers")
        assert result is not None
        
        # Should provide reasoning if dict
        if isinstance(result, dict):
            assert "operator" in result
            assert "reasoning" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

