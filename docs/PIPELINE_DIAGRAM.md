# SpeakMath Pipeline Architecture

## System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SpeakMath Pipeline Architecture                            │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
    │  INPUT  │ ───► │  LEXER  │ ───► │ PARSER  │ ───► │   AST   │ ───► │INTERP.  │
    │         │      │         │      │         │      │         │      │         │
    │ User    │      │ Tokens  │      │ Syntax  │      │ Tree    │      │ Execute │
    │ Command │      │         │      │ Analysis│      │ Nodes   │      │         │
    └─────────┘      └─────────┘      └────┬────┘      └─────────┘      └────┬────┘
                                          │                                  │
                                          │ (if ambiguous)                   │
                                          ▼                                  ▼
                                    ┌───────────┐                      ┌─────────┐
                                    │    LLM    │                      │ OUTPUT  │
                                    │ Fallback  │                      │         │
                                    │ (Gemini)  │                      │ Result  │
                                    └───────────┘                      └─────────┘
```

---

## Component Details

### 1️⃣ INPUT
- **Source**: User command (CLI, REPL, or Streamlit UI)
- **Format**: Natural language or structured syntax
- **Examples**:
  - `sum [1, 2, 3]`
  - `find the average of [10, 20, 30]`
  - `map add 5 over nums`

### 2️⃣ LEXER (`src/lexer.py`)
- **Function**: Tokenizes input string into tokens
- **Token Types**:
  | Token | Pattern | Example |
  |-------|---------|---------|
  | `NUMBER` | `\d+(\.\d+)?` | `42`, `3.14` |
  | `IDENTIFIER` | `[A-Za-z_]\w*` | `nums`, `x` |
  | `SUM` | `\bsum\b` | `sum` |
  | `MEAN` | `\b(mean\|average)\b` | `mean` |
  | `MAP` | `\bmap\b` | `map` |
  | `REDUCE` | `\breduce\b` | `reduce` |
  | `OPERATOR` | `==\|!=\|>=\|<=\|>\|<` | `>`, `==` |

### 3️⃣ PARSER (`src/parser.py`)
- **Function**: Builds Abstract Syntax Tree from tokens
- **Features**:
  - Recursive descent parsing
  - Operator precedence handling
  - Semantic map phrase resolution
  - LLM fallback for ambiguous phrases
- **AST Node Types**:
  - `NumberNode`, `VariableNode`, `ListNode`
  - `BinaryOpNode`, `AssignNode`, `PrintNode`
  - `ComputeNode`, `MapNode`, `ReduceNode`, `FilterNode`
  - `IfNode`, `SequenceNode`

### 4️⃣ LLM FALLBACK (`src/llm_layer.py`)
- **Trigger**: When semantic map cannot resolve phrase
- **API**: Google Gemini (gemini-1.5-flash)
- **Process**:
  1. Extract natural language phrase
  2. Send to LLM with operator options
  3. Parse JSON response
  4. Map to internal operator
- **Example Resolution**:
  - "tally up" → `OP_SUM`
  - "biggest number" → `OP_MAX`

### 5️⃣ AST (Abstract Syntax Tree)
- **Structure**: Tree of typed nodes
- **Visualization**: Available in Streamlit UI
- **Example**:
  ```
  ComputeNode(op=OP_SUM)
      └── ListNode
          ├── NumberNode(10)
          ├── NumberNode(20)
          └── NumberNode(30)
  ```

### 6️⃣ INTERPRETER (`src/interpreter.py`)
- **Function**: Evaluates AST and produces result
- **Features**:
  - Variable environment management
  - Dispatch table for node types
  - Functional operations (map, reduce, filter)
  - Function composition support
- **Operations**:
  | Operation | Description |
  |-----------|-------------|
  | `OP_SUM` | Sum all elements |
  | `OP_MEAN` | Calculate average |
  | `OP_PRODUCT` | Multiply all elements |
  | `OP_MAX/MIN` | Find max/min value |
  | `OP_SORT_ASC/DESC` | Sort list |

### 7️⃣ OUTPUT
- **Format**: Computed result value
- **Types**: Number, List, or None
- **Display**: CLI output, REPL, or Streamlit UI

---

## Example Execution Trace

### Command: `"sum [10, 20, 30]"`

| Stage | Input | Output |
|-------|-------|--------|
| **Input** | `"sum [10, 20, 30]"` | - |
| **Lexer** | String | `[SUM(sum), LBRACK([), NUMBER(10), COMMA(,), NUMBER(20), COMMA(,), NUMBER(30), RBRACK(]), EOF()]` |
| **Parser** | Tokens | `ComputeNode(op=OP_SUM, target=ListNode([10, 20, 30]))` |
| **Interpreter** | AST | `sum([10, 20, 30]) = 60` |
| **Output** | - | `60` |

---

## Functional Programming Pipeline

### Command: `"map add 5 over [1, 2, 3] then reduce sum over _"`

```
[1, 2, 3]  ──►  map add 5  ──►  [6, 7, 8]  ──►  reduce sum  ──►  21
                  │                               │
                  └── Each element + 5            └── Sum all elements
```

---

## Architecture Diagram (ASCII Art for Poster)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                        🧮 SPEAKMATH SYSTEM ARCHITECTURE                        ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   ┌──────────────┐                                                            ║
║   │   USER       │                                                            ║
║   │   INPUT      │──────────────────────────────────────────┐                 ║
║   └──────────────┘                                          │                 ║
║         │                                                   │                 ║
║         ▼                                                   ▼                 ║
║   ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────────┐   ║
║   │   LEXER      │───►│   PARSER     │───►│         INTERPRETER          │   ║
║   │              │    │              │    │                              │   ║
║   │ • Tokenize   │    │ • Build AST  │    │ • Evaluate AST               │   ║
║   │ • Keywords   │    │ • Resolve    │    │ • Execute Operations         │   ║
║   │ • Numbers    │    │   Phrases    │    │ • Manage Variables           │   ║
║   └──────────────┘    └──────┬───────┘    └──────────────┬───────────────┘   ║
║                              │                           │                    ║
║                              │ (ambiguous?)              │                    ║
║                              ▼                           ▼                    ║
║                       ┌──────────────┐           ┌──────────────┐            ║
║                       │  SEMANTIC    │           │   OUTPUT     │            ║
║                       │    MAP       │           │              │            ║
║                       └──────┬───────┘           │  • Result    │            ║
║                              │                   │  • Display   │            ║
║                              │ (not found?)      └──────────────┘            ║
║                              ▼                                               ║
║                       ┌──────────────┐                                       ║
║                       │     LLM      │                                       ║
║                       │   FALLBACK   │                                       ║
║                       │              │                                       ║
║                       │ • Gemini API │                                       ║
║                       │ • NL → Op    │                                       ║
║                       └──────────────┘                                       ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Files Reference

| Component | File | Lines |
|-----------|------|-------|
| Lexer | `src/lexer.py` | ~60 |
| Parser | `src/parser.py` | ~540 |
| Interpreter | `src/interpreter.py` | ~240 |
| LLM Layer | `src/llm_layer.py` | ~150 |
| AST Nodes | `src/ast.py` | ~80 |
| Semantic Map | `src/semantic_map.py` | ~50 |
| Streamlit UI | `streamlit_app.py` | ~260 |

---

*SpeakMath - Deliverable 7 Pipeline Architecture*
*Programmer/Integrator Documentation*

