"""
test_accuracy_llm.py

Accuracy measurement for LLM ambiguity resolution (D4).
Measures precision, recall, and accuracy of LLM operator resolution.

Author: Evaluation & Documentation Lead / Runtime Engineer
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_layer import resolve_phrase
from src.semantic_map import SEMANTIC_MAP


class TestAmbiguityResolutionAccuracy:
    """Measure accuracy of LLM ambiguity resolution"""
    
    # Ground truth test cases: (phrase, expected_operator)
    GROUND_TRUTH = [
        # Direct mappings (should be 100% accurate)
        ("sum", "OP_SUM"),
        ("mean", "OP_MEAN"),
        ("product", "OP_PRODUCT"),
        ("max", "OP_MAX"),
        ("min", "OP_MIN"),
        
        # Synonym mappings
        ("total", "OP_SUM"),
        ("average", "OP_MEAN"),
        ("multiply", "OP_PRODUCT"),
        ("largest", "OP_MAX"),
        ("smallest", "OP_MIN"),
        
        # Natural language phrases (LLM should handle)
        ("tally up", "OP_SUM"),
        ("add these up", "OP_SUM"),
        ("calculate average", "OP_MEAN"),
        ("find the mean", "OP_MEAN"),
        ("multiply all", "OP_PRODUCT"),
        ("get maximum", "OP_MAX"),
        ("get minimum", "OP_MIN"),
    ]
    
    def test_precision_and_recall(self):
        """Calculate precision and recall for operator resolution"""
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        results = []
        
        for phrase, expected_op in self.GROUND_TRUTH:
            result = resolve_phrase(phrase)
            
            # Extract operator from result
            actual_op = None
            if isinstance(result, str):
                actual_op = result
            elif isinstance(result, dict):
                actual_op = result.get("operator")
            
            # Classify result
            if actual_op == expected_op:
                true_positives += 1
                results.append((phrase, expected_op, actual_op, "CORRECT"))
            elif actual_op is not None and actual_op != expected_op:
                false_positives += 1
                results.append((phrase, expected_op, actual_op, "WRONG"))
            else:
                false_negatives += 1
                results.append((phrase, expected_op, actual_op, "MISSING"))
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        accuracy = true_positives / len(self.GROUND_TRUTH)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n=== Accuracy Metrics ===")
        print(f"Total test cases: {len(self.GROUND_TRUTH)}")
        print(f"True Positives: {true_positives}")
        print(f"False Positives: {false_positives}")
        print(f"False Negatives: {false_negatives}")
        print(f"\nPrecision: {precision:.4f} ({precision*100:.2f}%)")
        print(f"Recall: {recall:.4f} ({recall*100:.2f}%)")
        print(f"Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"F1 Score: {f1_score:.4f}")
        
        print(f"\n=== Detailed Results ===")
        for phrase, expected, actual, status in results:
            print(f"{status:8} | Expected: {expected:15} | Got: {str(actual):15} | Phrase: {phrase}")
        
        # Should have high accuracy for known phrases
        assert accuracy > 0.8, f"Accuracy too low: {accuracy}"
    
    def test_operator_specific_accuracy(self):
        """Measure accuracy per operator type"""
        operator_results = {}
        
        for phrase, expected_op in self.GROUND_TRUTH:
            if expected_op not in operator_results:
                operator_results[expected_op] = {"correct": 0, "total": 0}
            
            result = resolve_phrase(phrase)
            actual_op = None
            if isinstance(result, str):
                actual_op = result
            elif isinstance(result, dict):
                actual_op = result.get("operator")
            
            operator_results[expected_op]["total"] += 1
            if actual_op == expected_op:
                operator_results[expected_op]["correct"] += 1
        
        print(f"\n=== Per-Operator Accuracy ===")
        for op, stats in operator_results.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            print(f"{op:15} | {stats['correct']}/{stats['total']} = {accuracy:.2%}")
    
    def test_unknown_phrase_handling(self):
        """Test accuracy of rejecting non-mathematical phrases"""
        invalid_phrases = [
            "where is university malaya",
            "hello there",
            "what time is it",
            "how are you",
            "tell me a joke"
        ]
        
        correct_rejections = 0
        
        for phrase in invalid_phrases:
            result = resolve_phrase(phrase)
            # Should return None or UNKNOWN
            if result is None:
                correct_rejections += 1
            elif isinstance(result, dict) and result.get("operator") in (None, "UNKNOWN"):
                correct_rejections += 1
        
        rejection_rate = correct_rejections / len(invalid_phrases)
        
        print(f"\n=== Invalid Phrase Rejection ===")
        print(f"Correct rejections: {correct_rejections}/{len(invalid_phrases)}")
        print(f"Rejection rate: {rejection_rate:.2%}")
        
        # Should reject most invalid phrases
        assert rejection_rate > 0.5, f"Too many false positives: {rejection_rate}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

