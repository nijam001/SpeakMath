"""
functional_examples.py

Example programs demonstrating functional programming features in SpeakMath.

Author: Evaluation & Documentation Lead / Runtime Engineer
"""

from src.main import run_command


def example_1_basic_map():
    """Example 1: Basic map operation"""
    print("\n=== Example 1: Basic Map ===")
    print("Command: map add 5 over [1, 2, 3, 4, 5]")
    result, _ = run_command("map add 5 over [1, 2, 3, 4, 5]")
    print(f"Result: {result}")
    print("Explanation: Adds 5 to each element in the list")


def example_2_basic_reduce():
    """Example 2: Basic reduce operation"""
    print("\n=== Example 2: Basic Reduce ===")
    print("Command: reduce sum over [1, 2, 3, 4, 5]")
    result, _ = run_command("reduce sum over [1, 2, 3, 4, 5]")
    print(f"Result: {result}")
    print("Explanation: Sums all elements in the list")


def example_3_map_multiply():
    """Example 3: Map with multiplication"""
    print("\n=== Example 3: Map Multiply ===")
    print("Command: map multiply 3 over [2, 4, 6, 8]")
    result, _ = run_command("map multiply 3 over [2, 4, 6, 8]")
    print(f"Result: {result}")
    print("Explanation: Multiplies each element by 3")


def example_4_reduce_product():
    """Example 4: Reduce with product"""
    print("\n=== Example 4: Reduce Product ===")
    print("Command: reduce multiply over [2, 3, 4]")
    result, _ = run_command("reduce multiply over [2, 3, 4]")
    print(f"Result: {result}")
    print("Explanation: Multiplies all elements together (2 * 3 * 4 = 24)")


def example_5_function_composition():
    """Example 5: Function composition"""
    print("\n=== Example 5: Function Composition ===")
    print("Command: map multiply 2 over [1, 2, 3, 4] then reduce sum over _")
    result, _ = run_command("map multiply 2 over [1, 2, 3, 4] then reduce sum over _")
    print(f"Result: {result}")
    print("Explanation: First multiplies each element by 2, then sums the results")
    print("Step 1: [1, 2, 3, 4] → [2, 4, 6, 8]")
    print("Step 2: [2, 4, 6, 8] → 20")


def example_6_chained_operations():
    """Example 6: Chained functional operations"""
    print("\n=== Example 6: Chained Operations ===")
    interp = None
    
    # Step 1: Create initial list
    print("Step 1: set data to [10, 20, 30, 40]")
    _, interp = run_command("set data to [10, 20, 30, 40]", interp)
    
    # Step 2: Map operation
    print("Step 2: map add 5 over data")
    result1, interp = run_command("map add 5 over data", interp)
    print(f"  Result: {result1}")
    
    # Step 3: Reduce operation
    print("Step 3: reduce sum over data")
    result2, interp = run_command("reduce sum over data", interp)
    print(f"  Result: {result2}")
    
    print("Explanation: Demonstrates chaining operations on the same data")


def example_7_practical_calculation():
    """Example 7: Practical calculation using functional approach"""
    print("\n=== Example 7: Practical Calculation ===")
    print("Scenario: Calculate total cost after applying 10% discount to each item")
    
    prices = [100, 200, 150, 300]
    print(f"Original prices: {prices}")
    
    # Apply discount (multiply by 0.9)
    discounted, _ = run_command(f"map multiply 0.9 over [{', '.join(str(p) for p in prices)}]")
    print(f"After 10% discount: {discounted}")
    
    # Calculate total
    total, _ = run_command(f"reduce sum over [{', '.join(str(d) for d in discounted)}]")
    print(f"Total cost: {total}")


def example_8_data_processing():
    """Example 8: Data processing pipeline"""
    print("\n=== Example 8: Data Processing Pipeline ===")
    print("Scenario: Process test scores - double bonus points, then find average")
    
    scores = [85, 90, 75, 88, 92]
    print(f"Original scores: {scores}")
    
    # Double bonus points
    doubled, _ = run_command(f"map multiply 2 over [{', '.join(str(s) for s in scores)}]")
    print(f"After doubling: {doubled}")
    
    # Find average
    avg, _ = run_command(f"mean [{', '.join(str(d) for d in doubled)}]")
    print(f"Average: {avg}")


def example_9_composition_benefits():
    """Example 9: Benefits of function composition"""
    print("\n=== Example 9: Composition Benefits ===")
    print("Demonstrates how composition makes code more readable and maintainable")
    
    # Without composition (manual steps)
    print("\nWithout composition (manual):")
    interp = None
    _, interp = run_command("set nums to [1, 2, 3, 4, 5]", interp)
    mapped, interp = run_command("map add 10 over nums", interp)
    interp.vars["mapped"] = mapped
    result1, _ = run_command("reduce sum over mapped", interp)
    print(f"  Result: {result1}")
    
    # With composition (single expression)
    print("\nWith composition (single expression):")
    result2, _ = run_command("map add 10 over [1, 2, 3, 4, 5] then reduce sum over _")
    print(f"  Result: {result2}")
    
    print("\nBenefits:")
    print("  - More concise code")
    print("  - No intermediate variables needed")
    print("  - Clearer intent")
    print("  - Easier to reason about")


def example_10_functional_properties():
    """Example 10: Demonstrating functional properties"""
    print("\n=== Example 10: Functional Properties ===")
    
    # Purity: Same input always produces same output
    print("\n1. Purity (No side effects):")
    result1, _ = run_command("map add 5 over [1, 2, 3]")
    result2, _ = run_command("map add 5 over [1, 2, 3]")
    print(f"  First call: {result1}")
    print(f"  Second call: {result2}")
    print(f"  Results identical: {result1 == result2}")
    
    # Referential transparency
    print("\n2. Referential Transparency:")
    print("  Expression can be replaced with its value")
    interp = None
    _, interp = run_command("set x to map add 2 over [1, 2, 3]", interp)
    result_a, interp = run_command("sum x", interp)
    print(f"  Using variable: {result_a}")
    
    result_b, _ = run_command("sum [3, 4, 5]")  # Direct value
    print(f"  Using direct value: {result_b}")
    print(f"  Results equivalent: {result_a == result_b}")


def run_all_examples():
    """Run all functional programming examples"""
    print("=" * 60)
    print("SpeakMath Functional Programming Examples")
    print("=" * 60)
    
    examples = [
        example_1_basic_map,
        example_2_basic_reduce,
        example_3_map_multiply,
        example_4_reduce_product,
        example_5_function_composition,
        example_6_chained_operations,
        example_7_practical_calculation,
        example_8_data_processing,
        example_9_composition_benefits,
        example_10_functional_properties,
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {example_func.__name__}: {e}")
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()

