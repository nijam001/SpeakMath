# lexer.py
import re

TOKEN_SPEC = [
    ("NUMBER",       r"\d+(\.\d+)?"),
    ("COMMA",        r","),
    ("LBRACK",       r"\["),
    ("RBRACK",       r"\]"),
    ("LPAREN",       r"\("),
    ("RPAREN",       r"\)"),
    ("OPERATOR",     r"(==|!=|>=|<=|>|<)"),
    ("ADDOP",        r"(\+|\-)"),
    ("MULOP",        r"(\*|/)"),
    ("SET",          r"\bset\b"),
    ("TO",           r"\bto\b"),
    ("IF",           r"\bif\b"),
    ("THEN",         r"\bthen\b"),
    ("MAP",          r"\bmap\b"),
    ("FILTER",       r"\bfilter\b"),
    ("REDUCE",       r"\breduce\b"),
    ("SUM",          r"\bsum\b"),
    ("MEAN",         r"\b(mean|average|find the mean)\b"),
    ("PRODUCT",      r"\b(product|multiply)\b"),
    ("MAX",          r"\bmax\b"),
    ("MIN",          r"\bmin\b"),
    ("SORT_ASC",     r"\bsort\s+ascending\b"),
    ("SORT_DESC",    r"\bsort\s+descending\b"),
    ("PRINT",        r"\bprint\b"),
    ("OVER_ON",      r"\b(over|on)\b"),
    ("IDENTIFIER",   r"[A-Za-z_][A-Za-z0-9_]*"),
    ("SKIP",         r"[ \t\r\n]+"),
    ("UNKNOWN",      r"."),
]

MASTER_RE = re.compile("|".join(f"(?P<{n}>{p})" for n,p in TOKEN_SPEC), re.IGNORECASE)

class Token:
    def __init__(self, type_, value, pos):
        self.type = type_
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def lex(text: str):
    tokens = []
    for mo in MASTER_RE.finditer(text):
        kind = mo.lastgroup
        val = mo.group().strip()
        pos = mo.start()
        if kind == "SKIP":
            continue
        if kind == "UNKNOWN":
            # ignore stray punctuation usually, but include comma/brackets handled above
            continue
        tokens.append(Token(kind, val, pos))
    tokens.append(Token("EOF","",len(text)))
    return tokens
