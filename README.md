# SpeakMath: Natural Expressions into Verified Computations

![Project Status](https://img.shields.io/badge/Status-Week%208-orange)
![Course](https://img.shields.io/badge/Course-WIF3010-blue)
![Paradigm](https://img.shields.io/badge/Paradigm-Functional%20Programming-green)

**SpeakMath** is a math-focused natural language mini-programming language that interprets expressions like *"find the mean of these values"* into verified computations. The LLM suggests operator meanings, while our grammar verifies expressions before evaluation.

**University of Malaya** | Faculty of Computer Science & Information Technology  
**WIF3010: Programming Language Concepts** | Project Brief 2025

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [System Architecture](#-system-architecture)
- [Grammar Design (Week 8)](#-grammar-design-week-8)
- [Team Roles](#-team-roles)
- [Current Progress](#-current-progress)
- [Next Steps](#-next-steps)

---

## 🤖 About the Project

**Project Title:** SpeakMath (Topic #3 from WIF3010 Brief)

**Core Concept:**  
Create a math-focused natural mini-language where:
- Users write commands like *"find the mean of these values"*
- LLM suggests operator meanings (e.g., "average" → `mean`)
- Our grammar verifies expressions before evaluation
- Execution is handled by our own interpreter

**Paradigm Extension:** Functional Programming (map/reduce/composition)

### Why SpeakMath?

- Makes mathematical operations accessible through natural language
- Combines formal grammar verification with LLM flexibility
- Perfect for demonstrating functional programming concepts
- Clear scope for proof of correctness

---

## 🏗 System Architecture
```mermaid
graph LR
    A[User Input] --> B[Lexer]
    B --> C[Parser]
    C --> D{Verb Known?}
    D -- Yes --> E[Semantic Mapper]
    D -- No --> F[LLM Layer (Gemini)]
    F --> E
    E --> G[Interpreter]
    G --> H[Output]
```

## 📜 Grammar Design

### Syntax Definition

The formal BNF/EBNF syntax definition is available in [docs/syntax_definition.md](docs/syntax_definition.md).

**Implemented Features:**
- Variable assignment: `set x to 5`
- Conditionals: `if x > 10 then print x`
- Functional ops: `map add 2 over [1, 2, 3]`
- Natural Language: "find the average of these numbers"

### Example Commands
```
sum [1, 2, 3, 4, 5]
mean [10, 20, 30, 40]
product [5, 6]
```

---

## 📅 Current Progress

### Features Implemented ✅
- [x] Recursive Descent Parser & Lexer
- [x] Interpreter with memory management
- [x] LLM Integration (Google Gemini) - **With Reasoning!**
- [x] Functional Programming (Map/Reduce)
- [x] Interactive REPL with Help & History
- [x] Smart Error Handling

---

## 🚀 Usage

For detailed instructions, see the **[USER GUIDE](USER_GUIDE.md)**.

### Quick Start
1. Install dependencies: `pip install -r requirements.txt`
2. Set `GEMINI_API_KEY` in `.env`
3. Run: `python -m src`

---

## 📊 Assessment Focus

| Criteria | Marks | Current Status |
|----------|-------|----------------|
| Proposal & Grammar Design | 15 | ✅ Completed |
| Parser & Interpreter | 20 | ✅ Completed |
| LLM Integration | 15 | ✅ Completed |
| Paradigm Extension (Functional) | 10 | ✅ Completed (Map/Reduce) |
| Proof of Correctness | 10 | 🟡 In Progress |
| Testing & Evaluation | 10 | ✅ Completed (Unit Tests) |
| Presentations | 10 | 🟡 Preparing |
| Final Report | 10 | ⏳ Pending |

---

**University of Malaya** | FCSIT  
**Last Updated:** Week 10, 2025
