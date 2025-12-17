# Functional Programming Guide for SpeakMath

This guide explains how to use functional programming features in SpeakMath, including map, reduce, and function composition.

## Table of Contents

1. [Introduction to Functional Programming](#introduction)
2. [Map Operations](#map-operations)
3. [Reduce Operations](#reduce-operations)
4. [Function Composition](#function-composition)
5. [Functional Properties](#functional-properties)
6. [Advantages of Functional Approach](#advantages)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## Introduction to Functional Programming

Functional programming is a programming paradigm that treats computation as the evaluation of mathematical functions. In SpeakMath, functional operations are **pure** (no side effects) and **referentially transparent** (same input always produces same output).

### Key Concepts

- **Map**: Apply a function to each element of a list
- **Reduce**: Combine all elements of a list into a single value
- **Composition**: Chain operations together
- **Purity**: Functions don't modify external state
- **Immutability**: Operations don't change original data

## Map Operations

Map applies a transformation to each element in a list.

### Syntax
```
map <operation> <argument> over <list>
```

### Examples

**Add a constant to each element:**
```
>> map add 5 over [1, 2, 3, 4]
=> [6, 7, 8, 9]
```

**Multiply each element:**
```
>> map multiply 2 over [1, 2, 3, 4]
=> [2, 4, 6, 8]
```

**With variables:**
```
>> set prices to [10, 20, 30]
>> map add 5 over prices
=> [15, 25, 35]
```

### Properties

- **Preserves length**: Output list has same length as input
- **Pure**: Original list is never modified
- **Deterministic**: Same input always produces same output

## Reduce Operations

Reduce combines all elements of a list into a single value.

### Syntax
```
reduce <operation> over <list>
```

### Examples

**Sum all elements:**
```
>> reduce sum over [1, 2, 3, 4, 5]
=> 15
```

**Multiply all elements:**
```
>> reduce multiply over [2, 3, 4]
=> 24
```

**Find maximum:**
```
>> reduce max over [5, 2, 8, 1, 9]
=> 9
```

**Find minimum:**
```
>> reduce min over [5, 2, 8, 1, 9]
=> 1
```

### Properties

- **Associative**: Order of combination doesn't matter (for sum/product)
- **Pure**: Original list is never modified
- **Single value output**: Always returns a scalar, not a list

## Function Composition

Compose multiple operations together using the `then` keyword.

### Syntax
```
<operation1> then <operation2>
```

The result of the first operation is automatically passed to the second.

### Examples

**Map then Reduce:**
```
>> map multiply 2 over [1, 2, 3, 4] then reduce sum over _
=> 20
```

**Explanation:**
1. First: `[1, 2, 3, 4]` → `[2, 4, 6, 8]` (multiply by 2)
2. Then: `[2, 4, 6, 8]` → `20` (sum all)

**Multiple compositions:**
```
>> set data to [10, 20, 30]
>> map add 5 over data then reduce sum over _
=> 75
```

### Using Placeholder Variable

The `_` variable represents the result of the previous operation:

```
>> map add 10 over [1, 2, 3] then mean _
=> 16.0
```

## Functional Properties

### 1. Purity (No Side Effects)

Functions don't modify external state:

```
>> set original to [1, 2, 3]
>> map add 5 over original
=> [6, 7, 8]
>> print original
=> [1, 2, 3]  # Original unchanged!
```

### 2. Referential Transparency

Expressions can be replaced with their values:

```
# These are equivalent:
>> set x to map add 2 over [1, 2, 3]
>> sum x
=> 12

>> sum [3, 4, 5]  # Direct value
=> 12
```

### 3. Determinism

Same input always produces same output:

```
>> map add 3 over [1, 2, 3]
=> [4, 5, 6]
>> map add 3 over [1, 2, 3]
=> [4, 5, 6]  # Always the same!
```

## Advantages of Functional Approach

### 1. **Readability**

Functional code reads like mathematics:

```
# Clear intent: multiply each by 2, then sum
map multiply 2 over [1, 2, 3] then reduce sum over _
```

### 2. **Composability**

Operations can be easily chained:

```
# Process data through multiple steps
map add 10 over data then map multiply 2 over _ then reduce sum over _
```

### 3. **Predictability**

No hidden side effects - easier to reason about:

```
# You know original data won't change
set data to [1, 2, 3]
map add 5 over data  # data is still [1, 2, 3]
```

### 4. **Testability**

Pure functions are easier to test:

```
# Same input = same output, always
assert map add 2 over [1, 2, 3] == [3, 4, 5]
```

### 5. **Parallelization Potential**

Pure functions can be parallelized (future enhancement):

```
# Each element processed independently
map add 5 over [1, 2, 3, 4, 5]  # Could run in parallel
```

## Examples

### Example 1: Price Calculation

Calculate total after applying discount:

```
>> set prices to [100, 200, 150]
>> map multiply 0.9 over prices then reduce sum over _
=> 405.0
```

### Example 2: Data Transformation

Transform and aggregate data:

```
>> set scores to [85, 90, 75, 88, 92]
>> map multiply 2 over scores then mean _
=> 172.0
```

### Example 3: Complex Pipeline

Multiple transformations:

```
>> set data to [1, 2, 3, 4, 5]
>> map add 10 over data
=> [11, 12, 13, 14, 15]
>> map multiply 2 over [11, 12, 13, 14, 15]
=> [22, 24, 26, 28, 30]
>> reduce sum over [22, 24, 26, 28, 30]
=> 130
```

Or using composition:

```
>> map add 10 over [1, 2, 3, 4, 5] then map multiply 2 over _ then reduce sum over _
=> 130
```

## Best Practices

### ✅ DO:

1. **Use composition for readability:**
   ```
   map add 5 over data then reduce sum over _
   ```

2. **Keep operations pure:**
   - Don't rely on side effects
   - Original data remains unchanged

3. **Use meaningful variable names:**
   ```
   set prices to [10, 20, 30]
   map add tax over prices
   ```

4. **Chain related operations:**
   ```
   map transform over data then filter valid over _ then reduce sum over _
   ```

### ❌ DON'T:

1. **Don't expect side effects:**
   ```
   map add 5 over data  # data is NOT modified
   ```

2. **Don't mix paradigms unnecessarily:**
   - Prefer functional style for list operations
   - Use imperative style only when needed

3. **Don't ignore composition:**
   ```
   # Instead of:
   set temp to map add 5 over data
   sum temp
   
   # Use:
   map add 5 over data then reduce sum over _
   ```

## Comparison: Functional vs Imperative

### Imperative Approach (Traditional)
```
set result to []
set data to [1, 2, 3]
# Loop through and modify
# ... complex loop logic ...
```

### Functional Approach (SpeakMath)
```
map add 5 over [1, 2, 3]
=> [6, 7, 8]
```

**Benefits:**
- More concise
- Easier to understand
- No mutation concerns
- Naturally composable

## Performance Considerations

- **Map/Reduce are optimized** for list operations
- **Composition has minimal overhead**
- **Functional operations are typically fast** for small to medium lists
- **Large lists** may benefit from optimization (future enhancement)

## Advanced Topics

### Function Composition Laws

**Map Fusion:**
```
map g (map f xs) ≡ map (g ∘ f) xs
```

**Reduce Associativity:**
```
reduce op (xs ++ ys) ≡ reduce op xs `op` reduce op ys
```

### Type Safety

Functional operations maintain type safety:
- Map: `[Number] → [Number]`
- Reduce: `[Number] → Number`
- Composition preserves types through the pipeline

## Troubleshooting

**Problem:** "Map requires numeric argument"
- **Solution:** Provide a numeric argument: `map add 5 over [1, 2, 3]`

**Problem:** "Cannot reduce empty list"
- **Solution:** Ensure your list has at least one element

**Problem:** Composition not working
- **Solution:** Use `_` placeholder: `map add 5 over data then reduce sum over _`

---

**Remember:** Functional programming makes your code more readable, predictable, and maintainable. Embrace composition and purity!

