"""
test_performance_functional.py

Performance benchmarks for functional operations (D5).
Benchmarks map/reduce execution and compares with imperative approaches.

Author: Evaluation & Documentation Lead / Runtime Engineer
"""

import time
import statistics
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.interpreter import Interpreter
from src.parser import Parser
from src.lexer import lex


def run_command(text, interp=None):
    """Helper to run a command"""
    if interp is None:
        interp = Interpreter()
    tokens = lex(text)
    parser = Parser(tokens)
    ast = parser.parse()
    return interp.eval(ast), interp


class TestMapPerformance:
    """Benchmark map operation performance"""
    
    def test_map_small_list(self):
        """Benchmark map on small list"""
        sizes = [10, 100, 1000]
        
        print(f"\n=== Map Performance (Small Lists) ===")
        for size in sizes:
            # Create list
            test_list = list(range(1, size + 1))
            list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
            
            # Benchmark map
            times = []
            for _ in range(10):
                start = time.perf_counter()
                result, _ = run_command(f"map add 5 over {list_str}")
                times.append((time.perf_counter() - start) * 1000)
            
            avg_time = statistics.mean(times)
            print(f"Size {size:5} | Average: {avg_time:.4f} ms")
    
    def test_map_large_list(self):
        """Benchmark map on large list"""
        size = 10000
        test_list = list(range(1, size + 1))
        list_str = "[" + ", ".join(str(x) for x in test_list[:100]) + "]"  # Limit for parsing
        
        times = []
        for _ in range(5):
            start = time.perf_counter()
            result, _ = run_command(f"map add 10 over {list_str}")
            times.append((time.perf_counter() - start) * 1000)
        
        avg_time = statistics.mean(times)
        print(f"\n=== Map Performance (Large List) ===")
        print(f"Size {len(test_list[:100])} | Average: {avg_time:.4f} ms")
    
    def test_map_operations_comparison(self):
        """Compare different map operations"""
        test_list = list(range(1, 101))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        operations = [
            ("add", 5),
            ("multiply", 2),
        ]
        
        print(f"\n=== Map Operations Comparison ===")
        for op_name, arg in operations:
            times = []
            for _ in range(10):
                start = time.perf_counter()
                result, _ = run_command(f"map {op_name} {arg} over {list_str}")
                times.append((time.perf_counter() - start) * 1000)
            
            avg_time = statistics.mean(times)
            print(f"{op_name:10} {arg:3} | Average: {avg_time:.4f} ms")


class TestReducePerformance:
    """Benchmark reduce operation performance"""
    
    def test_reduce_small_list(self):
        """Benchmark reduce on small list"""
        sizes = [10, 100, 1000]
        
        print(f"\n=== Reduce Performance (Small Lists) ===")
        for size in sizes:
            test_list = list(range(1, size + 1))
            list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
            
            times = []
            for _ in range(10):
                start = time.perf_counter()
                result, _ = run_command(f"reduce sum over {list_str}")
                times.append((time.perf_counter() - start) * 1000)
            
            avg_time = statistics.mean(times)
            print(f"Size {size:5} | Average: {avg_time:.4f} ms")
    
    def test_reduce_operations_comparison(self):
        """Compare different reduce operations"""
        test_list = list(range(1, 101))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        operations = ["sum", "multiply"]
        
        print(f"\n=== Reduce Operations Comparison ===")
        for op in operations:
            times = []
            for _ in range(10):
                start = time.perf_counter()
                result, _ = run_command(f"reduce {op} over {list_str}")
                times.append((time.perf_counter() - start) * 1000)
            
            avg_time = statistics.mean(times)
            print(f"{op:10} | Average: {avg_time:.4f} ms")


class TestCompositionPerformance:
    """Benchmark function composition performance"""
    
    def test_composition_performance(self):
        """Benchmark function composition"""
        test_list = list(range(1, 51))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        # Test composition: map then reduce
        times = []
        for _ in range(10):
            start = time.perf_counter()
            result, _ = run_command(f"map multiply 2 over {list_str} then reduce sum over _")
            times.append((time.perf_counter() - start) * 1000)
        
        avg_time = statistics.mean(times)
        
        print(f"\n=== Composition Performance ===")
        print(f"Map then Reduce | Average: {avg_time:.4f} ms")
    
    def test_nested_vs_composition(self):
        """Compare nested operations vs composition"""
        test_list = list(range(1, 51))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        # Nested approach
        nested_times = []
        for _ in range(10):
            start = time.perf_counter()
            # Simulate nested: reduce sum over (map multiply 2 over list)
            result1, interp = run_command(f"map multiply 2 over {list_str}")
            interp.vars["_temp"] = result1
            result2, _ = run_command(f"reduce sum over _temp", interp)
            nested_times.append((time.perf_counter() - start) * 1000)
        
        # Composition approach
        comp_times = []
        for _ in range(10):
            start = time.perf_counter()
            result, _ = run_command(f"map multiply 2 over {list_str} then reduce sum over _")
            comp_times.append((time.perf_counter() - start) * 1000)
        
        nested_avg = statistics.mean(nested_times)
        comp_avg = statistics.mean(comp_times)
        
        print(f"\n=== Nested vs Composition ===")
        print(f"Nested approach: {nested_avg:.4f} ms")
        print(f"Composition: {comp_avg:.4f} ms")
        print(f"Difference: {abs(nested_avg - comp_avg):.4f} ms")


class TestFunctionalVsImperative:
    """Compare functional vs imperative approaches"""
    
    def test_map_vs_loop(self):
        """Compare map vs imperative loop"""
        test_list = list(range(1, 101))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        # Functional (map)
        func_times = []
        for _ in range(10):
            start = time.perf_counter()
            result, _ = run_command(f"map add 5 over {list_str}")
            func_times.append((time.perf_counter() - start) * 1000)
        
        # Imperative (Python loop for comparison)
        imp_times = []
        for _ in range(10):
            start = time.perf_counter()
            result = [x + 5 for x in test_list]
            imp_times.append((time.perf_counter() - start) * 1000)
        
        func_avg = statistics.mean(func_times)
        imp_avg = statistics.mean(imp_times)
        
        print(f"\n=== Functional vs Imperative (Map) ===")
        print(f"Functional (map): {func_avg:.4f} ms")
        print(f"Imperative (loop): {imp_avg:.4f} ms")
        print(f"Overhead: {func_avg - imp_avg:.4f} ms")
    
    def test_reduce_vs_loop(self):
        """Compare reduce vs imperative loop"""
        test_list = list(range(1, 101))
        list_str = "[" + ", ".join(str(x) for x in test_list) + "]"
        
        # Functional (reduce)
        func_times = []
        for _ in range(10):
            start = time.perf_counter()
            result, _ = run_command(f"reduce sum over {list_str}")
            func_times.append((time.perf_counter() - start) * 1000)
        
        # Imperative (Python loop)
        imp_times = []
        for _ in range(10):
            start = time.perf_counter()
            total = 0
            for x in test_list:
                total += x
            imp_times.append((time.perf_counter() - start) * 1000)
        
        func_avg = statistics.mean(func_times)
        imp_avg = statistics.mean(imp_times)
        
        print(f"\n=== Functional vs Imperative (Reduce) ===")
        print(f"Functional (reduce): {func_avg:.4f} ms")
        print(f"Imperative (loop): {imp_avg:.4f} ms")
        print(f"Overhead: {func_avg - imp_avg:.4f} ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

