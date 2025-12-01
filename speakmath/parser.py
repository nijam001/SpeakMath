
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
        # compute keywords
        if c.type in ("SUM","MEAN","PRODUCT","MAX","MIN","SORT_ASC","SORT_DESC"):
            token = self.eat(c.type)
            phrase = token.value.lower()
            op = resolve_phrase(phrase) or SEMANTIC_MAP.get(phrase, None)
            if not op:
                raise ParseError("Unknown verb: "+phrase)
            target = self.parse_expression_or_target()
            return ast.ComputeNode(op, target)
        # identifier as verb?
        if c.type == "IDENTIFIER":
            # try treating identifier as verb phrase
            phrase = c.value.lower()
            op = resolve_phrase(phrase) or SEMANTIC_MAP.get(phrase)
            if op:
                self.eat("IDENTIFIER")
                target = self.parse_expression_or_target()
                return ast.ComputeNode(op, target)
        raise ParseError("Unknown command start: "+str(c))

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
        op = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_MAP")
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
        op = resolve_phrase(op_phrase) or SEMANTIC_MAP.get(op_phrase, "OP_REDUCE")
        return ast.ReduceNode(op, target)

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
            vals.append(self.parse_number_literal())
            while self.cur().type == "COMMA":
                self.eat("COMMA"); vals.append(self.parse_number_literal())
        self.eat("RBRACK")
        return ast.ListNode(vals)

    def parse_list_shorthand(self):
        vals = [self.parse_number_literal()]
        while self.cur().type == "COMMA":
            self.eat("COMMA"); vals.append(self.parse_number_literal())
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
