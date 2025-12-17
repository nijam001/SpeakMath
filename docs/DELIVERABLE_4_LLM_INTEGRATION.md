# LLM Integration Strategy: "The Reasoning Engine"

## 1. The "Hybrid Resolution" Architecture
We don't just send everything to the AI. That would be slow and expensive. Instead, we use a **Layered Approach**:

1.  **Layer 1: Exact Match (O(1))**
    *   Checks `SEMANTIC_MAP` for known keywords (`sum`, `mean`).
    *   *Latency:* < 1ms
2.  **Layer 2: Synonym Match**
    *   Checks `SYNONYM_MAP` for common phrases (`tally up`, `average of`).
    *   *Latency:* < 1ms
3.  **Layer 3: LLM Fallback (Gemini 2.0 Flash)**
    *   Only triggered for truly novel phrases.
    *   *Latency:* ~500ms - 1s

## 2. Prompt Engineering
We use a **Structured JSON Prompt** to ensure reliable execution. The interpreter doesn't just want an answer; it wants an *instruction*.

**System Prompt:**
> "You are a semantic mapper for SpeakMath. Map the user's phrase to one of these valid operators: ['OP_SUM', 'OP_MEAN', ...]"

**Output Format:**
```json
{
  "operator": "OP_SUM",
  "reasoning": "The user used 'tally up', which implies summation of values."
}
```

## 3. The "Explainability" Feature
A key differentiator of SpeakMath is that it doesn't just do the math; it explains **why** it chose a specific operation.

*   **User Input**: `"find the biggest number"`
*   **LLM Response**: `"OP_MAX"`
*   **Reasoning**: `"Biggest implies finding the maximum value in a set."`
*   **UI Display**: 
    ```
    <-- Operator Found: OP_MAX
    <-- AI Reasoning: Biggest implies finding the maximum value in a set.
    ```

## 4. Why Gemini 2.0 Flash?
*   **Speed**: Essential for a REPL experience.
*   **JSON Mode**: Native support ensures the parser never crashes on "chatty" responses (e.g., "Sure! Here is the answer...").
*   **Reasoning Capabilities**: Capable of understanding complex intent (e.g., "distribute the cost" -> `OP_MAP` / `OP_DIVIDE`).

## 5. Future Improvements
*   **Context Awareness**: Feeding previous history to the LLM for multi-turn reasoning.
*   **Few-Shot Learning**: Adding dynamic examples to the prompt based on user errors.
