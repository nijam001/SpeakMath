# SpeakMath: LLM Integration Code Flow

This document details the control flow for Natural Language commands in SpeakMath.

## High-Level Architecture

```mermaid
graph LR
    User["User Input"] --> Main["Main Loop (REPL)"]
    Main --> Lexer
    Lexer --> Parser
    Parser --> Interpreter
    Interpreter --> Output["Result"]
```

## Detailed Flow: Natural Language Processing

When the user enters a phrase like `"tally up the score [10, 20]"`, the system follows this path:

```mermaid
sequenceDiagram
    participant U as User
    participant P as Parser
    participant R as Resolver (llm_layer)
    participant S as Semantic Map
    participant G as Google Gemini API
    participant I as Interpreter

    U->>P: tally up the score [10, 20]
    activate P
    
    Note over P: 1. Identify 'tally up...' as<br/>Unknown Phrase
    
    P->>R: resolve_phrase('tally up the score')
    activate R
    
    R->>S: Check Local Map?
    alt Found in Semantic Map
        S-->>R: Return OP_SUM (Optimized)
    else Not Found
        R->>G: Send Prompt (Map 'tally up' to known ops)
        activate G
        G-->>R: JSON { operator: OP_SUM, reasoning: ... }
        deactivate G
    end
    
    R-->>P: Return { op: OP_SUM, source: AI/Optimized }
    deactivate R
    
    Note over P: 2. Create AST Node<br/>ComputeNode(OP_SUM, ...)
    
    P->>I: eval(ComputeNode)
    deactivate P
    activate I
    
    I->>I: Execute OP_SUM (Python sum())
    I-->>U: Return 30
    deactivate I
```

## Key Components

### 1. The Parser (`parser.py`)
- **Role**: The "Brain" that decides when to switch from strict grammar to AI mode.
- **Logic**: 
    - Reads token by token.
    - If it sees a "Safe Word" (like *find*, *calculate*, *the*), it keeps reading to form a full sentence.
    - Calls `resolve_phrase()` to understand the sentence.

### 2. The Resolver (`llm_layer.py`)
- **Role**: The bridge between code and AI.
- **Optimization**: First checks a `semantic_map.py` (Hash Map) for instant results.
- **Fallback**: If not found, calls Gemini to "guess" the intent based on the list of known operations (`OP_SUM`, `OP_MEAN`, etc.).

### 3. The Interpreter (`interpreter.py`)
- **Role**: Pure logic execution.
- **Design**: It doesn't know about English or AI. It only knows `OP_SUM`. This keeps the core logic safe and deterministic.
