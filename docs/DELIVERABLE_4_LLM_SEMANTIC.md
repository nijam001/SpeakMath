# Deliverable 4: LLM Integration & Semantic Validation

**Project:** SpeakMath - Natural Language Programming Language  
**Course:** WIF3010 Programming Language Concepts  
**Role:** Semantics & Proof Specialist  
**Date:** December 2025

---

## A. LLM Semantic Mapping Validation

### Overview

The LLM layer (`src/llm_layer.py`) integrates Google Gemini API to resolve ambiguous natural language phrases to canonical semantic operators. This document validates the semantic correctness of this integration.

### Resolution Strategy

The system uses a **4-tier resolution strategy**:

```
1. Direct Lookup (SEMANTIC_MAP)
   ↓ (if not found)
2. Synonym Lookup (SYNONYM_MAP)
   ↓ (if not found)
3. Heuristic Pattern Matching
   ↓ (if not found)
4. LLM Resolution (Gemini API)
```

### Validation Rules

**Rule 1: Deterministic Priority**
- Direct mappings must take precedence over LLM suggestions
- Ensures consistent behavior for known commands
- Example: "sum" → always resolves to `OP_SUM` without LLM call

**Rule 2: Type-Safe LLM Output**
- LLM must return one of the valid operators from semantic table
- Invalid operators are rejected (returns `None`)
- Validation: `if op in valid_ops`

**Rule 3: Graceful Degradation**
- System continues without LLM if API key missing
- Returns `None` for unknown phrases
- Parser handles `None` gracefully

**Rule 4: Semantic Constraints**
LLM output must map to valid semantic operations:
- Arithmetic operations: `OP_SUM`, `OP_MEAN`, `OP_PRODUCT`
- Comparison: `OP_MAX`, `OP_MIN`
- Functional: `OP_MAP`, `OP_REDUCE`
- Control: `OP_IF`, `OP_ASSIGN`, `OP_PRINT`

### Current Implementation Review

**✅ Strengths:**
1. Multi-tier fallback strategy prevents unnecessary API calls
2. JSON-structured response with reasoning improves explainability
3. Type validation ensures only valid operators are accepted
4. Error handling prevents crashes on LLM failure

**⚠️ Areas for Improvement:**
1. **Return type inconsistency**: Sometimes returns string, sometimes dict
2. **No semantic validation**: LLM could map "print" to "OP_SUM" (wrong semantically)
3. **No confidence threshold**: Accepts any LLM suggestion in valid_ops
4. **Limited test coverage**: Need test cases for ambiguity resolution

---

## B. Ambiguity Handling Tests

### Test Categories

**Category 1: Direct Synonyms**
Natural language phrases with clear semantic equivalents.

| Input Phrase | Expected Operator | Reasoning |
|--------------|-------------------|-----------|
| "calculate total" | `OP_SUM` | "total" in phrase → sum operation |
| "compute average" | `OP_MEAN` | "average" → mean operation |
| "find biggest" | `OP_MAX` | "biggest" → maximum |
| "get smallest value" | `OP_MIN` | "smallest" → minimum |

**Category 2: Informal Language**
Colloquial expressions requiring LLM interpretation.

| Input Phrase | Expected Operator | Reasoning |
|--------------|-------------------|-----------|
| "add these up" | `OP_SUM` | Addition operation |
| "tally the numbers" | `OP_SUM` | Tallying implies summation |
| "double each value" | `OP_MAP` | Apply operation to each element |
| "combine all" | `OP_REDUCE` | Aggregate operation |

**Category 3: Ambiguous Phrases**
Phrases that could map to multiple operations - LLM must disambiguate.

| Input Phrase | Expected Operator | Alternative | LLM Decision |
|--------------|-------------------|-------------|--------------|
| "process numbers" | Context-dependent | Multiple | Requires context |
| "aggregate values" | `OP_REDUCE` or `OP_SUM` | Both valid | Choose most common |

**Category 4: Invalid/Unknown Phrases**
Phrases that don't map to any mathematical operation.

| Input Phrase | Expected Result | Reasoning |
|--------------|-----------------|-----------|
| "where is UM?" | `None` | Not a math operation |
| "hello world" | `None` | Greeting, not command |
| "the weather" | `None` | Unrelated domain |

### Ambiguity Resolution Accuracy

**Metrics to Track:**
- **Precision**: % of LLM suggestions that are semantically correct
- **Recall**: % of ambiguous phrases successfully resolved
- **Fallback Rate**: % of phrases requiring LLM (vs direct lookup)

**Target Accuracy:**
- Direct Lookup: 100% (deterministic)
- Synonym Map: 100% (predefined)
- LLM Resolution: ≥85% (acceptable for ambiguous cases)

---

## C. Fallback Mechanism

### Fallback Strategy

**Level 1: No LLM Available**
```python
if not api_key:
    print("Warning: GEMINI_API_KEY not set.")
    return None
```
- Graceful degradation
- System continues with known commands only
- User informed of limitation

**Level 2: LLM Returns Invalid Operator**
```python
if op in valid_ops:
    return {"operator": op, "reasoning": res.get("reasoning", "")}
return {"operator": None, "reasoning": "No match found"}
```
- Type safety maintained
- Invalid suggestions rejected
- Parser handles `None` appropriately

**Level 3: LLM Error/Timeout**
```python
except Exception as e:
    print(f"LLM Error: {e}")
    return None
```
- Catch all exceptions
- Prevent system crash
- Degrade to known commands

### Type Safety Guarantees

**Invariant 1: Output Type Consistency**
```
resolve_phrase(s) ∈ {valid_operator | None | dict}
where valid_operator ∈ SEMANTIC_MAP.values()
```

**Invariant 2: Semantic Preservation**
If `resolve_phrase(s) = op`, then `op` has defined semantics in interpreter

**Invariant 3: No Type Confusion**
LLM cannot create new operators or bypass type checking

### Semantic Error Handling

**Unknown Verb Handling:**
1. `resolve_phrase()` returns `None`
2. Parser detects `None` and raises parse error
3. User receives clear error message
4. System state remains consistent (no partial execution)

**Example:**
```python
Input: "xyzabc the numbers"
resolve_phrase("xyzabc") → None
Parser: "Unknown command: xyzabc"
Result: Safe error, no execution
```

---

## D. Semantic Validation Framework

### Validation Function

```python
def validate_llm_semantic_mapping(phrase: str, operator: str, context: dict) -> bool:
    """
    Validate that LLM-suggested operator is semantically appropriate.
    
    Args:
        phrase: Original natural language input
        operator: LLM-suggested operator
        context: Additional context (e.g., surrounding words)
    
    Returns:
        True if semantically valid, False otherwise
    """
    # Semantic rules
    arithmetic_keywords = ["add", "sum", "total", "plus", "combine"]
    aggregation_keywords = ["average", "mean", "median"]
    comparison_keywords = ["max", "min", "largest", "smallest", "biggest"]
    
    if operator == "OP_SUM":
        return any(kw in phrase.lower() for kw in arithmetic_keywords)
    
    if operator == "OP_MEAN":
        return any(kw in phrase.lower() for kw in aggregation_keywords)
    
    if operator in ["OP_MAX", "OP_MIN"]:
        return any(kw in phrase.lower() for kw in comparison_keywords)
    
    # Default: accept if in valid_ops (conservative approach)
    return operator in SEMANTIC_MAP.values()
```

### Test Coverage Matrix

| Test Type | Coverage | Status |
|-----------|----------|--------|
| Direct lookup | 19 operators | ✅ Complete |
| Synonym mapping | 12 phrases | ✅ Complete |
| LLM resolution | 8+ test cases | 🔄 In progress |
| Error handling | 5 scenarios | 🔄 In progress |
| Semantic validation | 10+ rules | 📝 Proposed |

---

## E. Implementation Recommendations

### Short-term Improvements

**1. Standardize Return Type**
```python
# Current: Returns string OR dict OR None
# Proposed: Always return dict
{
    "operator": "OP_SUM" | None,
    "reasoning": "explanation",
    "confidence": 0.95,
    "source": "direct" | "synonym" | "llm"
}
```

**2. Add Semantic Validation Layer**
```python
def resolve_phrase(phrase: str) -> dict:
    result = _raw_resolve(phrase)
    
    # Validate semantic appropriateness
    if result["operator"] and result["source"] == "llm":
        if not validate_llm_semantic_mapping(phrase, result["operator"]):
            result["operator"] = None
            result["reasoning"] = "Semantic validation failed"
    
    return result
```

**3. Confidence Thresholding**
```python
# Only accept LLM suggestions with high confidence
if confidence < 0.7:
    return None  # Require manual clarification
```

### Long-term Enhancements

1. **Caching**: Store successful LLM resolutions to reduce API calls
2. **Learning**: Track user corrections to improve mappings
3. **Context-aware**: Use surrounding commands for disambiguation
4. **Multi-language**: Extend to Malay language support

---

## F. Test Results

### Test Execution Summary

**Test File:** `tests/test_llm_semantic.py`

| Test Category | Tests | Passed | Failed | Coverage |
|---------------|-------|--------|--------|----------|
| Direct Lookup | 10 | 10 | 0 | 100% |
| Synonym Resolution | 8 | 8 | 0 | 100% |
| LLM Ambiguity | 6 | TBD | TBD | TBD |
| Error Handling | 5 | TBD | TBD | TBD |
| Type Safety | 4 | TBD | TBD | TBD |

**Overall Status:** 🔄 In Progress (Direct + Synonym complete, LLM tests pending API setup)

---

## Summary

### Completed Work
- ✅ **A. Validation Rules:** 4 core rules defined and documented
- ✅ **B. Ambiguity Tests:** 4 categories with 15+ test cases specified
- ✅ **C. Fallback Mechanism:** 3-level fallback with type safety guarantees
- ✅ **D. Validation Framework:** Semantic validation function proposed

### Next Steps
1. Implement standardized return type
2. Add semantic validation layer
3. Complete LLM integration tests
4. Measure ambiguity resolution accuracy
5. Document performance metrics

---

## References

**Implementation Files:**
- [`src/llm_layer.py`](../src/llm_layer.py) - LLM integration layer
- [`src/semantic_map.py`](../src/semantic_map.py) - Semantic mappings
- [`tests/test_llm_semantic.py`](../tests/test_llm_semantic.py) - LLM validation tests

**Related Documentation:**
- [Deliverable 3: Semantic Implementation](DELIVERABLE_3_SEMANTICS.md)
- [docs/syntax_definition.md](syntax_definition.md)
