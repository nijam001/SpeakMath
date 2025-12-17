# LLM Fallback System Design

## Overview

This document describes the design of the LLM fallback system for SpeakMath, which supplements the grammar-based parser when unknown or unsupported operations are encountered.

---

## 1. Grammar Failure Points

### 1.1 Unknown Verb (Lexical Failure)

**Scenario:** A word/phrase not in the lexer's token specification.

**Examples:**

- "tally up these numbers" → `tally` not in TOKEN_SPEC
- "compute median of [1,2,3]" → `median` not in TOKEN_SPEC
- "average out the values" → `average out` is a multi-word verb

**Current Behavior:**

- Lexer marks as `IDENTIFIER` or skips as `UNKNOWN`
- Parser attempts to build phrase but may fail with "Unknown command"

**Fallback Trigger:** When parser builds a phrase that doesn't match SEMANTIC_MAP

---

### 1.2 Unsupported Syntax (Syntactic Failure)

**Scenario:** Valid tokens but invalid grammar structure.

**Examples:**

- "calculate 5 plus 3" → `calculate` as verb with arithmetic expression (not supported pattern)
- "show me all numbers greater than 5" → filtering operation (not in grammar)
- "reverse the list" → unary operation not defined in grammar

**Current Behavior:**

- Parser fails with `ParseError` due to unexpected token sequence
- No structured error information returned

**Fallback Trigger:** When token sequence doesn't match any production rule

---

### 1.3 Unknown Operator (Semantic Failure)

**Scenario:** Valid syntax but operation has no semantic mapping.

**Examples:**

- "mode [1,1,2,3]" → `mode` is recognized as IDENTIFIER but no OP_MODE defined
- "variance of data" → `variance` not mapped to any operation
- "median of [1,2,3,4,5]" → `median` not in SEMANTIC_MAP

**Current Behavior:**

- Parser may accept the syntax but llm_layer.resolve_phrase() is called
- If LLM returns UNKNOWN, parser raises error

**Fallback Trigger:** When SEMANTIC_MAP lookup fails and LLM is queried

---

## 2. Fallback Classification

### 2.1 Lexical Fallback

**Definition:** Unknown keyword not recognized by lexer as a known token type.

**Detection:**

- Token type is `IDENTIFIER` or `UNKNOWN`
- Not in predefined keyword list (SUM, MEAN, PRODUCT, etc.)

**Resolution Strategy:**

1. Build multi-word phrase from consecutive identifiers
2. Query LLM with phrase + context
3. LLM returns canonical operator or UNKNOWN
4. If UNKNOWN, reject with structured error

**Example Flow:**

```
Input: "tally the numbers [1,2,3]"
Lexer: [IDENTIFIER(tally), IDENTIFIER(the), IDENTIFIER(numbers), LBRACK, ...]
Parser: Builds phrase "tally the numbers"
LLM: Returns {"operator": "OP_SUM", "reasoning": "tally implies sum"}
Result: ComputeNode(OP_SUM, [1,2,3])
```

---

### 2.2 Semantic Fallback

**Definition:** Valid syntax with known token types, but operator meaning is unknown.

**Detection:**

- Parser successfully identifies command structure
- Operator token is recognized (e.g., MEAN, IDENTIFIER)
- SEMANTIC_MAP[operator] returns None

**Resolution Strategy:**

1. Parser extracts operator phrase
2. Query LLM with phrase + valid operator list
3. LLM maps to canonical operator
4. Continue parsing with resolved operator

**Example Flow:**

```
Input: "median [1,2,3,4,5]"
Lexer: [IDENTIFIER(median), LBRACK, ...]
Parser: Recognizes compute pattern, extracts "median"
SEMANTIC_MAP: No match found
LLM: Returns {"operator": "UNKNOWN", "reasoning": "median is a statistical operation not currently supported"}
Result: ParseError with structured info
```

---

## 3. LLM Intervention Rules

### Rule 1: Never Override Grammar

**Principle:** The grammar is the source of truth for syntax.

**Implementation:**

- LLM is ONLY called after grammar parsing fails OR semantic mapping fails
- LLM cannot change token types or parse tree structure
- LLM only provides semantic meaning for unknown operators

**Example:**

```
❌ WRONG: "sum 1 2 3" → LLM interprets as "sum([1,2,3])" (changes syntax)
✅ RIGHT: "sum 1, 2, 3" → Parser handles syntax, LLM not needed
```

---

### Rule 2: Only Supplement Missing Meaning

**Principle:** LLM fills semantic gaps, not syntactic ones.

**Implementation:**

- LLM is consulted only for operator/verb resolution
- LLM does NOT generate code or AST nodes
- LLM returns canonical operator name from predefined set

**Example:**

```
❌ WRONG: LLM generates AST node for "create a list of primes"
✅ RIGHT: LLM maps "tally" → OP_SUM, parser builds AST
```

---

### Rule 3: Functional Constructs Remain Grammar-First

**Principle:** Map/reduce/compose are core language features, not LLM-resolved.

**Implementation:**

- Keywords `map`, `reduce` are always lexed as MAP, REDUCE tokens
- Parser handles map/reduce syntax directly
- LLM may help resolve operation WITHIN map/reduce (e.g., "map increment over list")

**Example:**

```
Input: "map increment 2 over [1,2,3]"
Lexer: [MAP, IDENTIFIER(increment), NUMBER(2), OVER_ON, LBRACK, ...]
Parser: Recognizes MAP pattern, calls LLM for "increment"
LLM: Returns {"operator": "OP_MAP_ADD", "reasoning": "increment means add"}
Result: MapNode(OP_MAP_ADD, 2, [1,2,3])
```

---

## 4. Structured Failure Objects

### 4.1 Failure Object Schema

```python
{
    "error_type": "lexical_failure" | "semantic_failure" | "syntax_error",
    "token": str,              # The problematic token/phrase
    "position": int,           # Character position in input
    "message": str,            # Human-readable error
    "suggestion": str | None,  # Optional suggestion from LLM
    "context": str             # Surrounding tokens for debugging
}
```

### 4.2 Error Types

#### Lexical Failure

```python
{
    "error_type": "lexical_failure",
    "token": "tally",
    "position": 0,
    "message": "Unknown keyword 'tally'",
    "suggestion": "Did you mean 'sum'? (AI suggests: OP_SUM)",
    "context": "tally the numbers [1,2,3]"
}
```

#### Semantic Failure

```python
{
    "error_type": "semantic_failure",
    "token": "median",
    "position": 0,
    "message": "Unknown operation 'median'",
    "suggestion": "median is not currently supported. Try: mean, max, min",
    "context": "median [1,2,3,4,5]"
}
```

#### Syntax Error

```python
{
    "error_type": "syntax_error",
    "token": "IDENTIFIER",
    "position": 15,
    "message": "Expected NUMBER, got IDENTIFIER",
    "suggestion": None,
    "context": "sum [1, 2, x]"
}
```

### 4.3 Parser Modifications

The parser will return a `ParseResult` object:

```python
class ParseResult:
    def __init__(self, success: bool, ast_node=None, error=None):
        self.success = success
        self.ast_node = ast_node  # AST if success=True
        self.error = error        # Failure object if success=False
```

---

## 5. Updated AST Design

### 5.1 New Node Type: LLMResolvedNode

```python
class LLMResolvedNode(ASTNode):
    """
    Represents an operation that was resolved via LLM fallback.
    Maintains metadata about AI resolution for debugging/logging.
    """
    def __init__(self, resolved_op, target, original_phrase, reasoning):
        self.resolved_op = resolved_op      # Canonical op (e.g., OP_SUM)
        self.target = target                # Target expression
        self.original_phrase = original_phrase  # User's original phrase
        self.reasoning = reasoning          # LLM's reasoning
        self.is_llm_resolved = True         # Flag for interpreter
```

### 5.2 Extended ComputeNode

```python
class ComputeNode(ASTNode):
    def __init__(self, op, target, is_llm_resolved=False, llm_metadata=None):
        self.op = op
        self.target = target
        self.is_llm_resolved = is_llm_resolved
        self.llm_metadata = llm_metadata or {}
        # llm_metadata = {"original_phrase": str, "reasoning": str}
```

### 5.3 AST Example

```
Input: "tally the values [1,2,3]"

AST:
ComputeNode(
    op="OP_SUM",
    target=ListNode([1,2,3]),
    is_llm_resolved=True,
    llm_metadata={
        "original_phrase": "tally the values",
        "reasoning": "tally implies summation"
    }
)
```

---

## 6. System Flow Diagram

```
┌─────────────┐
│ User Input  │
│ "tally [1,2]│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│     LEXER       │
│  Token Stream   │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────────┐
│         PARSER                  │
│  ┌──────────────────┐          │
│  │ Grammar Matching │          │
│  └────┬─────────────┘          │
│       │                         │
│       ├─ Known Token? ──Yes──► │ Build AST (Grammar-First)
│       │                         │
│       └─ No/Unknown ──►         │
│          ┌──────────────┐       │
│          │ Build Phrase │       │
│          └──────┬───────┘       │
└─────────────────┼───────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │   LLM RESOLVER    │
        │                   │
        │ 1. Check SEMANTIC │
        │    _MAP first     │
        │ 2. Query LLM API  │
        │ 3. Return:        │
        │    - Canonical Op │
        │    - UNKNOWN      │
        │    - Error        │
        └─────────┬─────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │  Operator Found?    │
        └──┬──────────────┬───┘
           │              │
          Yes            No
           │              │
           ▼              ▼
    ┌───────────┐   ┌──────────────┐
    │ Build AST │   │ Return Error │
    │ with LLM  │   │   Object     │
    │ metadata  │   └──────────────┘
    └─────┬─────┘
          │
          ▼
    ┌─────────────┐
    │ INTERPRETER │
    │             │
    │ Execute AST │
    │ (Check if   │
    │ LLM-resolved│
    │ for logging)│
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │   OUTPUT    │
    └─────────────┘
```

---

## 7. Implementation Checklist

### Phase 1: Structured Failures

- [x] Define `ParseResult` class
- [x] Define failure object schema
- [ ] Modify `Parser.parse()` to return `ParseResult`
- [ ] Update error handling to build structured failures

### Phase 2: LLM Resolver Layer

- [x] Current `llm_layer.py` already implements resolution
- [ ] Add failure object generation to `resolve_phrase()`
- [ ] Add retry logic for LLM API failures
- [ ] Cache LLM responses to reduce API calls

### Phase 3: AST Updates

- [ ] Add `LLMResolvedNode` class to `ast.py`
- [ ] Update `ComputeNode` with metadata fields
- [ ] Update `Interpreter` to handle LLM-resolved nodes

### Phase 4: Grammar-First Enforcement

- [x] Ensure MAP/REDUCE remain lexer keywords
- [ ] Add unit tests verifying functional constructs bypass LLM
- [ ] Document LLM intervention boundaries

### Phase 5: Testing & Documentation

- [ ] Add test cases for lexical fallback
- [ ] Add test cases for semantic fallback
- [ ] Add test cases for grammar-first enforcement
- [ ] Update user guide with fallback behavior

---

## 8. Example Scenarios

### Scenario 1: Lexical Fallback Success

```
Input: "tally up [1, 2, 3]"

1. Lexer: [IDENTIFIER(tally), IDENTIFIER(up), LBRACK, ...]
2. Parser: Builds phrase "tally up"
3. SEMANTIC_MAP: No match
4. LLM: {"operator": "OP_SUM", "reasoning": "tally up means sum"}
5. AST: ComputeNode(OP_SUM, [1,2,3], is_llm_resolved=True)
6. Interpreter: sum([1,2,3]) = 6
7. Output: 6 (with debug log: "AI-resolved 'tally up' → SUM")
```

### Scenario 2: Semantic Fallback Failure

```
Input: "median [1, 2, 3, 4, 5]"

1. Lexer: [IDENTIFIER(median), LBRACK, ...]
2. Parser: Builds phrase "median"
3. SEMANTIC_MAP: No match
4. LLM: {"operator": "UNKNOWN", "reasoning": "median not supported"}
5. Parser: Returns ParseResult(success=False, error={...})
6. Error Object:
   {
     "error_type": "semantic_failure",
     "token": "median",
     "message": "Unknown operation 'median'",
     "suggestion": "Try: mean, max, min"
   }
7. Output: Error message to user
```

### Scenario 3: Grammar-First (No LLM)

```
Input: "map add 2 over [1, 2, 3]"

1. Lexer: [MAP, IDENTIFIER(add), NUMBER(2), OVER_ON, LBRACK, ...]
2. Parser: Recognizes MAP token → parse_map()
3. parse_map(): Extracts op="add", arg=2, target=[1,2,3]
4. SEMANTIC_MAP: "add" → OP_SUM (no LLM needed)
5. AST: MapNode(OP_SUM, 2, [1,2,3], is_llm_resolved=False)
6. Interpreter: [x+2 for x in [1,2,3]] = [3,4,5]
7. Output: [3, 4, 5]
```

---

## 9. Benefits of This Design

1. **Clear Separation of Concerns**

   - Grammar handles syntax
   - LLM handles semantics only when needed

2. **Debuggability**

   - Structured error objects provide context
   - LLM metadata tracks AI decisions

3. **Graceful Degradation**

   - System works without LLM (uses SEMANTIC_MAP)
   - LLM failures don't crash the parser

4. **Extensibility**

   - Easy to add new operators to SEMANTIC_MAP
   - LLM can handle novel phrases without code changes

5. **User Transparency**
   - Users see when LLM is used via debug logs
   - Error messages explain why input failed

---

## 10. Future Enhancements

1. **Confidence Scoring**

   - LLM returns confidence score with operator
   - Low confidence triggers user confirmation

2. **Learning System**

   - Cache successful LLM resolutions
   - Auto-update SEMANTIC_MAP from cache

3. **Multi-Language Support**

   - LLM can handle non-English phrases
   - Grammar remains language-agnostic

4. **Interactive Disambiguation**
   - When LLM uncertain, prompt user to choose
   - "Did you mean: sum, average, or product?"
