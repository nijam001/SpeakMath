
# parser.py
from typing import List
from .lexer import Token, lex
from . import ast
from .llm_layer import resolve_phrase
from .semantic_map import SEMANTIC_MAP

class ParseError(Exception):
    """Legacy exception for backwards compatibility"""
    pass

# Stop-words/Prepositions allowed to extend a valid verb
SAFE_PHRASE_IDS = {
    "the", "of", "up", "down", "to", "from", "by", "over", "on", "a", "an", "is", "calculate", "find",
    "these", "those", "this", "that", "all", "in",
    "items", "values", "numbers", "number", "list", "collection", "set", "elements", "data",
    "lowest", "highest", "smallest", "largest", "biggest", "ascending", "descending", "low", "high",
    "addition", "subtraction", "multiplication", "division", "total", "average", "product", "sum", "mean"
}

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.pos = 0
        # Capture input text if tokens have position info usually passed from lexer? 
        # Lexer just returns tokens. We need to reconstruct or store input.
        # Let's assume input_text is set manually or via tokens if they had source refs.
        # For now, we will relying on main passed it or we reconstruct from tokens.
        self.input_text = "" 
        
    def set_source(self, text):
        self.input_text = text

    def _track(self, node, start_pos):
        """Helper to attach source text to a node"""
        if not hasattr(node, 'debug_info'):
            node.debug_info = {}
            
        if self.input_text:
            # End pos is current token start (or length if EOF)
            end_pos = self.cur().pos
            node.debug_info['source'] = self.input_text[start_pos:end_pos].strip()
        return node


    def cur(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

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
    
    def get_context(self, pos, window=20):
        """Get surrounding text for error context"""
        if not self.input_text:
            return ""
        start = max(0, pos - window)
        end = min(len(self.input_text), pos + window)
        return self.input_text[start:end]

    def parse(self):
        node = self.parse_command()
        if self.cur().type != "EOF":
            raise ParseError("Trailing tokens after command: "+str(self.cur()))
        return node

    # compute keywords
    def parse_command(self):
        # First, try to parse a single command
        start_pos = self.cur().pos
        first_cmd = self.parse_single_command()
        
        # Attach debug info
        end_pos = self.cur().pos if self.cur().type != "EOF" else len(self.input_text)
        if not hasattr(first_cmd, 'debug_info'):
             first_cmd.debug_info = {}
        first_cmd.debug_info['source'] = self.input_text[start_pos:end_pos]
        
        # Check if there's a "then" keyword for composition
        if self.cur().type == "THEN":
            self.eat("THEN")
            self.eat("THEN")
            second_cmd = self.parse_single_command()
            seq_node = ast.SequenceNode(first_cmd, second_cmd)
            # Sequence covers full range? Or just combined? 
            # Ideally each sub-node has its own source.
            return seq_node
        
        return first_cmd
    
    def parse_single_command(self):
        """Parse a single command (without composition)"""
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
        
        # 1. Local Resolution Loop (Cheap)
        # Try to find the longest phrase that resolves LOCALLY (semantic map, synonyms, etc.)
        curr_phrase = ""
        valid_op = None
        best_len = 0
        best_reasoning = None # Local has no reasoning
        
        for i in range(10):
            tok = self.look(i)
            # HARD STOPS
            if tok.type in ("NUMBER", "LBRACK", "LPAREN", "EOF", "SET", "IF"):
                break
            
            # SOFT STOP: If we have a valid op, and hit an unsafe identifier, stop.
            if valid_op and tok.type == "IDENTIFIER" and tok.value.lower() not in SAFE_PHRASE_IDS:
                break
            
            part = tok.value
            curr_phrase += " " + part if curr_phrase else part
            
            # Use LOCAL resolver only
            from .llm_layer import resolve_phrase_local
            local_op = resolve_phrase_local(curr_phrase)
            
            if local_op:
                valid_op = local_op
                best_len = i + 1
                best_reasoning = None # Local has no reasoning
        
        # 2. LLM Fallback (Expensive)
        if not valid_op:
            # Reconstruct longest phrase up to Hard Stop, ignoring Soft Stop logic since we have no op yet.
            llm_phrase = ""
            llm_len = 0
            for i in range(10):
                tok = self.look(i)
                # Hard Stops
                if tok.type in ("NUMBER", "LBRACK", "LPAREN", "EOF", "SET", "IF"):
                    break
                
                # Soft Stop: If we hit a variable (unsafe identifier) after the first word, 
                # assume it's an argument to the command.
                if i > 0 and tok.type == "IDENTIFIER" and tok.value.lower() not in SAFE_PHRASE_IDS:
                    break
                    
                part = tok.value
                llm_phrase += " " + part if llm_phrase else part
                llm_len = i + 1
            
            if llm_phrase:
                from .llm_layer import resolve_phrase_llm
                llm_res = resolve_phrase_llm(llm_phrase)
                
                if llm_res and isinstance(llm_res, dict) and llm_res.get("operator"):
                    valid_op = llm_res["operator"]
                    best_reasoning = llm_res.get("reasoning")
                    best_len = llm_len

        # If we found a valid op, consume those tokens
        if valid_op:
            # Removed redundant printing here. Defer to Interpreter.
            for _ in range(best_len):
                self.eat(self.cur().type)
                
            # Consume remaining "safe" noise tokens
            while True:
                c = self.cur()
                if c.type in ("NUMBER", "LBRACK", "LPAREN", "EOF"):
                    break
                if c.value.lower() in SAFE_PHRASE_IDS:
                    self.eat(c.type)
                else:
                    break
            
            target = self.parse_expression_or_target()
            
            # Create ComputeNode with metadata for BOTH Local and AI
            source = "AI" if best_reasoning else "Local"
            metadata = {
                "original_phrase": curr_phrase if valid_op != "OP_MEAN" else "mean/average", # simplify?
                "reasoning": best_reasoning,
                "source": source
            }
            # Start: If it was local, curr_phrase might be short. 
            # Actually curr_phrase is whatever matched loop.
            metadata["original_phrase"] = curr_phrase 
            
            return ast.ComputeNode(valid_op, target, is_llm_resolved=(source=="AI"), llm_metadata=metadata)
            
        raise ParseError(f"Unknown command: '{curr_phrase}' (I don't know that operation)")

    def _resolve_op_phrase(self, phrase, default_op=None):
        """
        Helper to resolve a phrase to an operator using semantic map or LLM.
        Returns: (operator, reasoning, is_llm_resolved)
        """
        op_res = resolve_phrase(phrase) or SEMANTIC_MAP.get(phrase.lower(), default_op)
        
        if op_res is None:
            return None, None, False
            
        is_llm = False
        reasoning = None
        op = default_op
        
        if isinstance(op_res, dict):
            op = op_res.get("operator") or default_op
            reasoning = op_res.get("reasoning")
            is_llm = reasoning is not None
        else:
            op = op_res if isinstance(op_res, str) else default_op
            
        if op == "UNKNOWN":
            op = None
            
        return op, reasoning, is_llm

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
        op_tok = self.cur()
        if op_tok.type in ("IDENTIFIER","SUM","PRODUCT"):
            op_phrase = self.eat(op_tok.type).value.lower()
        else:
            raise ParseError("Expected operation after map")
        
        arg = None
        if self.cur().type == "NUMBER":
            arg = float(self.eat("NUMBER").value)
        elif self.cur().type == "IDENTIFIER" and self.peek().type == "OVER_ON":
            arg = self.eat("IDENTIFIER").value
            
        if self.cur().type == "OVER_ON":
            self.eat("OVER_ON")
        target = self.parse_expression_or_target()
        
        op, reasoning, is_llm = self._resolve_op_phrase(op_phrase, default_op="OP_MAP")
        
        source = "AI" if is_llm else "Local"
        metadata = {
            "original_phrase": op_phrase,
            "reasoning": reasoning,
            "source": source
        }
        return ast.MapNode(op, arg, target, is_llm_resolved=is_llm, llm_metadata=metadata)

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
        
        op, reasoning, is_llm = self._resolve_op_phrase(op_phrase, default_op="OP_REDUCE")
        
        source = "AI" if is_llm else "Local"
        metadata = {
            "original_phrase": op_phrase,
            "reasoning": reasoning,
            "source": source
        }
        return ast.ReduceNode(op, target, is_llm_resolved=is_llm, llm_metadata=metadata)

    def parse_filter(self):
        """
        Parse filter command.
        Syntax: filter <op> <val> over|in <target>
        Example: filter < 5 over [1, 2, 3]
        """
        self.eat("FILTER")
        
        op = ""
        comp_val = None
        
        c = self.cur()
        if c.type == "OPERATOR":
            op = self.eat("OPERATOR").value
            comp_val = self.parse_number_literal()
        else:
             raise ParseError("Expected operator (<, >, ==) after filter")
             
        if self.cur().type in ("OVER_ON", "IDENTIFIER"):
            # Allow 'over', 'on', 'in'
            tok = self.cur()
            if tok.type == "OVER_ON":
                self.eat("OVER_ON")
            elif tok.value.lower() == "in":
                 self.eat("IDENTIFIER") # consume 'in'
                 
        target = self.parse_expression_or_target()
        return ast.FilterNode(op, comp_val, target)

    def parse_expression_or_target(self):
        start = self.cur().pos
        c = self.cur()
        node = None
        if c.type == "LBRACK":
            node = self.parse_list_bracket()
        elif c.type == "NUMBER":
            if self.look(1).type == "COMMA":
                node = self.parse_list_shorthand()
            else:
                node = self.parse_expression()
        elif c.type == "IDENTIFIER":
            node = ast.VariableNode(self.eat("IDENTIFIER").value)
        elif c.type == "LPAREN":
            node = self.parse_expression()
        else:
            node = self.parse_expression()
        return self._track(node, start)

    def parse_list_bracket(self):
        start = self.cur().pos
        self.eat("LBRACK")
        vals = []
        if self.cur().type != "RBRACK":
            vals.append(self.parse_expression())
            while self.cur().type == "COMMA":
                self.eat("COMMA"); vals.append(self.parse_expression())
        self.eat("RBRACK")
        return self._track(ast.ListNode(vals), start)

    def parse_list_shorthand(self):
        vals = [self.parse_number_literal()]
        while self.cur().type == "COMMA":
            self.eat("COMMA"); vals.append(self.parse_expression())
        return ast.ListNode(vals)

    def parse_number_literal(self):
        start = self.cur().pos
        tok = self.eat("NUMBER")
        if "." in tok.value:
            return self._track(ast.NumberNode(float(tok.value)), start)
        return self._track(ast.NumberNode(int(tok.value)), start)

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
