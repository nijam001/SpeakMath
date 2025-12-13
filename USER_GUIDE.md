# SpeakMath User Guide

SpeakMath is a mini-programming language that bridges the gap between natural language and mathematical computations. It uses a formal grammar for structure but leverages an LLM (Google Gemini) to understand flexible "verbs" and operators.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- A Google Gemini API Key

### 2. Installation
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Setup API Key
Create a `.env` file in the project root and add your API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

## 🎮 How to Run

### Interactive Mode (REPL)
Run the interpreter interactively:
```bash
python -m src
```
**New!** Type `help` to see a list of commands.
Type `exit` or `quit` to leave.

### Demo Mode
Run the built-in demo script:
```bash
python -m src --demo
```

## 🗣️ Language Syntax

### Basic Commands
| Command | Example | Description |
| :--- | :--- | :--- |
| `set` | `set x to 5` | Assign a value to a variable. |
| `print` | `print x` | Display a value or variable. |
| `[]` | `[1, 2, 3]` | Create a list of numbers. |
| `help` | `help` | **(New)** Show available commands in REPL. |

### Math Operations
Standard operators are supported directly:
```text
sum 1, 2, 3
mean [10, 20, 30]
product 2, 4
max 5, 1, 9
```

### Functional Operations
SpeakMath supports `map` and `reduce`:
```text
map add 2 over [1, 2, 3]       => [3, 4, 5]
reduce multiply over [2, 3, 4] => 24
```

### 🧠 LLM-Powered Natural Language
Thanks to the AI integration, you can use natural phrases for operators. The system will figure out what you mean and even **explain its reasoning**!

**Examples of what you can say:**
- "tally up these numbers [1, 2, 3]" → `sum`
  - *System Output: (AI Reasoning: Tally up implies addition)*
- "find the average of 10, 20" → `mean`
- "arrange from smallest to biggest [3, 1, 2]" → `sort ascending`

**Smart Error Handling:**
If you ask something non-mathematical like "where is UM?", the system will now politely tell you it doesn't understand and suggest rephrasing, rather than crashing.

## 🔧 Troubleshooting
- **"Warning: GEMINI_API_KEY not set"**: The LLM features won't work. Check your `.env` file.
- **"Unknown command"**: The LLM couldn't map your phrase. Try rephrasing or use the `help` command.
