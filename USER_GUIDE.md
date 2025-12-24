# 📘 SpeakMath User Guide

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

---

## 💻 Web Interface (New!)

SpeakMath now comes with a beautiful **Streamlit Chatbot** interface.

### Running the App
```bash
streamlit run streamlit_app.py
```

### Key Features
1.  **Chatbot Experience**: Interact naturally with a message history.
2.  **Pipeline Visualization**: See exactly how your code is processed:
    *   **1️⃣ Lexer**: View color-coded token badges.
    *   **2️⃣ Parser**: Explore the Abstract Syntax Tree (AST) visualization.
    *   **3️⃣ Interpreter**: See logs and results interactively.
3.  **Variable Inspector**: A sidebar panel that tracks all your active variables (`nums`, `x`, etc.).
4.  **Sticky Input Bar**: A modern, glass-styled input bar stays at the bottom so you can type comfortably.

---

## 🎮 CLI Modes

### Interactive Mode (REPL)
Run the classic terminal interpreter:
```bash
python -m src
```
*   Type `help` to see a list of commands.
*   Type `exit` or `quit` to leave.

### Demo Mode
Run the built-in demo script:
```bash
python -m src --demo
```

---

## 🗣️ Language Syntax

### Basic Commands
| Command | Example | Description |
| :--- | :--- | :--- |
| `set` | `set x to 5` | Assign a value to a variable. |
| `print` | `print x` | Display a value or variable. |
| `[]` | `[1, 2, 3]` | Create a list of numbers. |
| `help` | `help` | Show available commands (CLI only). |

### Math Operations
Standard operators are supported directly:
```text
sum [1, 2, 3]
mean [10, 20, 30]
product [2, 4]
max [5, 1, 9]
```

### Functional Operations (Map & Reduce)
SpeakMath supports powerful functional programming concepts:

#### **Map** (Apply to all)
You can use variables in your map operations!
```text
set x to 2
set nums to [1, 2, 3]

map add 5 over nums         => [6, 7, 8]
map multiply x over nums    => [2, 4, 6]  <-- Uses variable 'x'
```

#### **Reduce** (Combine to one)
```text
reduce multiply over [2, 3, 4] => 24
reduce max over [10, 5, 8]     => 10
```

### 🧠 LLM-Powered Natural Language
Thanks to AI integration, you can use flexible english phrases. The system understands context!

**Examples:**
- **"Tally up these numbers [1, 2, 3]"** → Maps to `SUM`
- **"Find the total of nums"** → Correctly identifies `nums` as the target variable.
- **"Arrange from smallest to biggest"** → Maps to `SORT ASCENDING`

### 🛡️ Smart Error Handling
- The system explains *why* it chose a certain operation (e.g., "Reasoning: 'Tally up' implies addition").
- If it encounters a complex phrase like `find the total of nums`, the smart parser separates the **command** ("find the total of") from the **variable** ("nums") to execute correctly.

---

## 🔧 Troubleshooting
- **"Warning: GEMINI_API_KEY not set"**: The LLM features won't work. Check your `.env` file.
- **Visualizations missing?**: Ensure `graphviz` is installed on your system for the AST chart to render fully.
