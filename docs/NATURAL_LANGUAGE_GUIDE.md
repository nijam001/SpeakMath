# Natural Language Commands Guide

**SpeakMath** allows you to use natural language phrases instead of strict syntax. The system uses AI (Google Gemini) to understand your intent and map it to the correct mathematical operation.

## How It Works

SpeakMath uses a **4-tier resolution strategy**:

1. **Direct Lookup** - Known keywords like "sum", "mean"
2. **Synonym Lookup** - Predefined synonyms like "total" → sum
3. **Heuristic Matching** - Pattern matching for common phrases
4. **LLM Resolution** - AI-powered understanding for complex phrases

## Natural Language Examples

### Summation Operations

Instead of typing `sum [1, 2, 3]`, you can say:

- ✅ **"tally up these numbers [1, 2, 3]"**
- ✅ **"add these up [5, 10, 15]"**
- ✅ **"calculate the total of [2, 4, 6]"**
- ✅ **"sum up [1, 2, 3]"**

**System Response:**
```
<--  Operator Found: OP_SUM
<--  AI Reasoning: Tally up implies addition.
=> 6
```

### Average/Mean Operations

Instead of typing `mean [10, 20, 30]`, you can say:

- ✅ **"find the average of [10, 20, 30]"**
- ✅ **"calculate the mean value [10, 20, 30]"**
- ✅ **"what's the average of these numbers [10, 20, 30]"**
- ✅ **"compute average [10, 20, 30]"**

**System Response:**
```
<--  Operator Found: OP_MEAN
<--  AI Reasoning: Average and mean are equivalent statistical operations.
=> 20.0
```

### Maximum/Minimum Operations

- ✅ **"get the largest number from [5, 2, 9, 1]"** → `max`
- ✅ **"find the biggest value in [10, 5, 20]"** → `max`
- ✅ **"what's the smallest number in [3, 7, 2]"** → `min`
- ✅ **"get the minimum of [8, 4, 6]"** → `min`

### Sorting Operations

- ✅ **"arrange from smallest to biggest [3, 1, 2]"** → `sort ascending`
- ✅ **"arrange from biggest to smallest [3, 1, 2]"** → `sort descending`
- ✅ **"sort these numbers ascending [5, 2, 8]"** → `sort ascending`

### Product/Multiplication

- ✅ **"multiply all these numbers [2, 3, 4]"** → `product`
- ✅ **"calculate the product of [5, 6]"** → `product`

## Best Practices

### ✅ DO:
- Use clear, mathematical language
- Include the data in your command: `"tally up [1, 2, 3]"`
- Be specific about the operation you want

### ❌ DON'T:
- Ask non-mathematical questions: `"where is university malaya?"`
- Use ambiguous phrases without context
- Mix multiple operations in one phrase

## Understanding AI Reasoning

When the AI resolves your phrase, it provides reasoning:

```
Command: "tally up the numbers [1, 2, 3]"
<--  Operator Found: OP_SUM
<--  AI Reasoning: Tally up implies addition.
=> 6
```

This helps you understand how the system interpreted your command.

## Error Handling

If the system can't understand your phrase:

```
ERROR: Unknown command: 'hello there' (I don't know that operation)
Tip: I didn't understand that. Please REPHRASE your command or type 'help' to see valid examples.
```

**What to do:**
1. Try rephrasing with more mathematical language
2. Use the `help` command to see valid syntax
3. Try using direct keywords: `sum`, `mean`, `product`, etc.

## Performance Considerations

- **Direct keywords** (sum, mean) are fastest - no AI call needed
- **Synonym lookups** are very fast - predefined mappings
- **LLM resolution** takes longer (~500-2000ms) but handles complex phrases

**Tip:** For frequently used operations, prefer direct keywords for better performance.

## Examples in Practice

### Example 1: Quick Calculation
```
>> tally up [10, 20, 30, 40]
<--  Operator Found: OP_SUM
<--  AI Reasoning: Tally up implies addition.
=> 100
```

### Example 2: Statistical Analysis
```
>> find the average of these test scores [85, 90, 75, 88, 92]
<--  Operator Found: OP_MEAN
<--  AI Reasoning: Average is a statistical measure of central tendency.
=> 86.0
```

### Example 3: Data Processing
```
>> arrange from highest to lowest [5, 2, 8, 1, 9]
<--  Operator Found: OP_SORT_DESC
<--  AI Reasoning: Arranging from highest to lowest means descending sort.
=> [9, 8, 5, 2, 1]
```

## Advanced Usage

You can combine natural language with functional operations:

```
>> map add 5 over [1, 2, 3] then find the total of _
```

This demonstrates function composition with natural language!

## Troubleshooting

**Problem:** "Warning: GEMINI_API_KEY not set"
- **Solution:** Set your API key in `.env` file
- **Note:** Direct keywords and synonyms still work without API key

**Problem:** "Unknown command"
- **Solution:** Try rephrasing with more mathematical terms
- **Alternative:** Use direct keywords from the help menu

**Problem:** Slow response
- **Solution:** Use direct keywords instead of natural language for better performance

---

**Remember:** Natural language is powerful, but direct keywords are faster. Use natural language when you need flexibility, and keywords when you need speed!

