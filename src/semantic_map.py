
# semantic_map.py
SEMANTIC_MAP = {
    # canonical single-word mappings
    "sum": "OP_SUM",
    "add": "OP_SUM",
    "total": "OP_SUM",
    "mean": "OP_MEAN",
    "average": "OP_MEAN",
    "find the mean": "OP_MEAN",
    "product": "OP_PRODUCT",
    "multiply": "OP_PRODUCT",
    "max": "OP_MAX",
    "min": "OP_MIN",
    "sort ascending": "OP_SORT_ASC",
    "sort descending": "OP_SORT_DESC",
    "sort": "OP_SORT_ASC",
    "map": "OP_MAP",
    "reduce": "OP_REDUCE",
    "print": "OP_PRINT",
    "set": "OP_ASSIGN",
    "if": "OP_IF",
}

# synonyms / phrases that may need LLM or rule-based normalization
SYNONYM_MAP = {
    "total": "OP_SUM",
    "add these up": "OP_SUM",
    "combine": "OP_REDUCE",
    "collapse list": "OP_REDUCE",
    "double each value": "OP_MAP",  # implies map multiply 2
    "increment each by 2": "OP_MAP", # implies map add 2
    "arrange smallest to biggest": "OP_SORT_ASC",
    "arrange biggest to smallest": "OP_SORT_DESC",
    "get the largest": "OP_MAX",
    "get the smallest": "OP_MIN",
    "echo": "OP_PRINT",
    "show output": "OP_PRINT",
    "addition": "OP_SUM",
    "multiplication": "OP_PRODUCT",
}
