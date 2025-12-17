
# parser.py
from typing import List
from .lexer import Token, lex
from . import ast
from .llm_layer import resolve_phrase
from .semantic_map import SEMANTIC_MAP

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos]

    def eat(self, ttype):
        c = self.cur()
        if c.type == ttype:
            self.pos += 1
            return c
        raise ParseError(f"Expected {ttype} got {c.type} ({c.value}) at {c.pos}")

    def look(self, offset=0):
        i = self.pos + offset
        if i < len(self.tokens):
            return self.tokens[i]
        return Token("EOF","",len(self.tokens))

    def parse(self):
        node = self.parse_command()
        if self.cur().type != "EOF":
            raise ParseError("Trailing tokens after command: "+str(self.cur()))
        return node

    # compute keywords
    def parse_command(self):
        c = self.cur()
        if c.type == "SET":
            return self.parse_assign()
        if c.type == "IF":
            return self.parse_if()
        if c.type == "PRINT":
            self.eat("PRINT")
            expr = self.parse_expression_or_target()
            return ast.PrintNode(expr)
        if c.type == "MAP":
            return self.parse_map()
        if c.type == "REDUCE":
            return self.parse_reduce()
        if c.type == "FILTER":
            return self.parse_filter()
        
        # Check if it is a known compute keyword or potentially start of a NL phrase
        # We will attempt to consume a sequence of tokens that could form a verb phrase.
        # Tokens allowed in verb phrase: IDENTIFIER, keywords (SUM, MEAN, etc), OVER_ON
        # We stop when we hit: NUMBER, LBRACK, LPAREN, or EOF
        
        phrase_tokens = []
        start_pos = self.pos
        curr_phrase = ""
        valid_op = None
        reasoning = None
        best_len = 0
        
        # Stop-words/Prepositions allowed to extend a valid verb
        # If we encounter an identifier NOT in this list, and we already have a valid verb, we stop.
        SAFE_PHRASE_IDS = {
            "the", "of", "up", "down", "to", "from", "by", "over", "on", "a", "an", "is", "calculate", "find",
            "these", "those", "this", "that",
            "items", "values", "numbers", "list", "collection", "set", "elements", "data",
            "lowest", "highest", "smallest", "largest", "biggest", "ascending", "descending", "low", "high",
            "addition", "subtraction", "multiplication", "division"
        }
        
        # Look ahead up to 10 tokens to form a phrase
        for i in range(10):
            tok = self.look(i)
            # HARD STOPS: Number, Bracket, Paren, EOF, Keywords that start other structures
            if tok.type in ("NUMBER", "LBRACK", "LPAREN", "EOF", "SET", "IF", "THEN"):
                break
            
            # SOFT STOP: If we already have a valid op, and this is an "unsafe" identifier (likely a variable), break.
            # But if valid_op is None (e.g. "calculate"), we must continue.
            if valid_op and tok.type == "IDENTIFIER" and tok.value.lower() not in SAFE_PHRASE_IDS:
                break
                
            # Add to phrase
            # For keywords, use the value (e.g. "average"), for identifiers use value
            part = tok.value
            if curr_phrase:
                curr_phrase += " " + part
            else:
                curr_phrase = part
            
            # Check if this sub-phrase resolves to an op
            check_res = resolve_phrase(curr_phrase) or SEMANTIC_MAP.get(curr_phrase.lower())
            
            check_op = None
            check_reasoning = None
            
            if isinstance(check_res, dict):
                check_op = check_res.get("operator")
                check_reasoning = check_res.get("reasoning")
            elif isinstance(check_res, str):
                check_op = check_res
                
            if check_op:
                valid_op = check_op
                best_len = i + 1
                if check_reasoning:
                     reasoning = check_reasoning
            elif valid_op and tok.value.lower() in SAFE_PHRASE_IDS:
                # Heuristic: If valid verb exists, extend consumption over safe filler words
                # even if resolution fails for the extended phrase.
                best_len = i + 1
                
        # If we found a valid op, consume those tokens
        if valid_op:
            if reasoning:
                print(f"<--  Operator Found: {valid_op}")
                print(f"<--  AI Reasoning: {reasoning}")
            for _ in range(best_len):
                self.eat(self.cur().type)
            target = self.parse_expression_or_target()
            return ast.ComputeNode(valid_op, target)
            
        # Fallback for single keywords if loop somehow failed to pick them up (unlikely with above logic)
        # or if they were matched but not extended. 
        # Actually logic above handles single keywords too (i=0).
        
        # If we failed to find any op, error.
        # But if we had a specific "UNKNOWN" response from LLM for the longest phrase, maybe use that?
        # For simplicity, just error.
        raise ParseError(f"Unknown command: '{curr_phrase}' (I don't know that operation)")

    def parse_assign(self):
        self.eat("SET")
        var = self.eat("IDENTIFIER").value
        self.eat("TO")
        expr = self.parse_expression()
        return ast.AssignNode(var, expr)

    def parse_if(self):
        self.eat("IF")
        left = self.parse_expression()
        comp = self.eat("OPERATOR").value
        right = self.parse_expression()
        self.eat("THEN")
        action = self.parse_command()
        return ast.IfNode(left, comp, right, action)

    def parse_map(self):
        self.eat("MAP")
        # next token should be operation (identifier or keywords)
        op_tok = self.cur()
        if op_tok.type in ("IDENTIFIER","SUM","PRODUCT"):
            op_phrase = self.eat(op_tok.type).value.lower()
        else:
            raise ParseError("Expected operation after map")
        # optional numeric arg
        arg = None
        if self.cur().type == "NUMBER":
            arg = float(self.eat("NUMBER").value)
        if self.cur().type == "OVER_ON":
            self.eat("OVER_ON")
        target = self.parse_expression_or_target()
        # normalize op to canonical via resolve_phrase
        op_res = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_MAP")
        op = op_res if isinstance(op_res, str) else op_res.get("operator") if isinstance(op_res, dict) else "OP_MAP"
        if isinstance(op_res, dict) and op_res.get("reasoning"):
             print(f"  (AI Reasoning: {op_res.get('reasoning')})")
        return ast.MapNode(op, arg, target)

    def parse_reduce(self):
        self.eat("REDUCE")
        op_tok = self.cur()
        if op_tok.type in ("IDENTIFIER","SUM","PRODUCT"):
            op_phrase = self.eat(op_tok.type).value.lower()
        else:
            raise ParseError("Expected operation after reduce")
        if self.cur().type == "OVER_ON":
            self.eat("OVER_ON")
        target = self.parse_expression_or_target()
        op_res = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_REDUCE")
        op = op_res if isinstance(op_res, str) else op_res.get("operator") if isinstance(op_res, dict) else "OP_REDUCE"
        if isinstance(op_res, dict) and op_res.get("reasoning"):
             print(f"  (AI Reasoning: {op_res.get('reasoning')})")
        return ast.ReduceNode(op, target)

    def parse_filter(self):
        # Syntax: FILTER op val OVER target
        self.eat("FILTER")
        
        # operator: > < == etc
        # Lexer has OPERATOR token
        if self.cur().type == "OPERATOR":
            op = self.eat("OPERATOR").value
        else:
            raise ParseError(f"Expected operator after filter, got {self.cur()}")
            
        # value to compare against
        val = self.parse_expression() # allows number or variable
        
        # 'over', 'on', 'in'
        c = self.cur()
        if c.type == "OVER_ON":
            self.eat("OVER_ON")
        elif c.type == "IDENTIFIER" and c.value.lower() in ("over", "on", "in"):
             self.eat("IDENTIFIER")
        else:
            raise ParseError(f"Expected 'over', 'on', or 'in' in filter command, got {c}")
            
        target = self.parse_expression_or_target()
        return ast.FilterNode(op, val, target)

    def parse_expression_or_target(self):
        c = self.cur()
        if c.type == "LBRACK":
            return self.parse_list_bracket()
        if c.type == "NUMBER":
            if self.look(1).type == "COMMA":
                return self.parse_list_shorthand()
            return self.parse_expression()
        if c.type == "IDENTIFIER":
            return ast.VariableNode(self.eat("IDENTIFIER").value)
        if c.type == "LPAREN":
            return self.parse_expression()
        return self.parse_expression()

    def parse_list_bracket(self):
        self.eat("LBRACK")
        vals = []
        if self.cur().type != "RBRACK":
            vals.append(self.parse_expression())
            while self.cur().type == "COMMA":
                self.eat("COMMA"); vals.append(self.parse_expression())
        self.eat("RBRACK")
        return ast.ListNode(vals)

    def parse_list_shorthand(self):
        vals = [self.parse_number_literal()]
        while self.cur().type == "COMMA":
            self.eat("COMMA"); vals.append(self.parse_expression())
        return ast.ListNode(vals)

    def parse_number_literal(self):
        tok = self.eat("NUMBER")
        if "." in tok.value:
            return ast.NumberNode(float(tok.value))
        return ast.NumberNode(int(tok.value))

    def parse_expression(self):
        node = self.parse_term()
        while self.cur().type == "ADDOP":
            op = self.eat("ADDOP").value
            right = self.parse_term()
            node = ast.BinaryOpNode(node, op, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.cur().type == "MULOP":
            op = self.eat("MULOP").value
            right = self.parse_factor()
            node = ast.BinaryOpNode(node, op, right)
        return node

    def parse_factor(self):
        c = self.cur()
        if c.type == "NUMBER":
            return self.parse_number_literal()
        if c.type == "IDENTIFIER":
            return ast.VariableNode(self.eat("IDENTIFIER").value)
        if c.type == "LPAREN":
            self.eat("LPAREN"); node = self.parse_expression(); self.eat("RPAREN"); return node
        if c.type == "LBRACK":
            return self.parse_list_bracket()
        raise ParseError("Unexpected token in factor: "+str(c))
