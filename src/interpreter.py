
# interpreter.py
from . import ast
from .semantic_map import SEMANTIC_MAP
from typing import Any

class SemanticError(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.vars = {}

    def eval(self, node: ast.ASTNode) -> Any:
        if isinstance(node, ast.NumberNode):
            return node.value
        if isinstance(node, ast.VariableNode):
            if node.name not in self.vars:
                raise SemanticError(f"Undefined variable: {node.name}")
            return self.vars[node.name]
        if isinstance(node, ast.ListNode):
            return [self.eval(v) for v in node.values]
        if isinstance(node, ast.BinaryOpNode):
            l = self.eval(node.left); r = self.eval(node.right)
            if node.op == "+": return l + r
            if node.op == "-": return l - r
            if node.op == "*": return l * r
            if node.op == "/": return l / r
            raise SemanticError("Unknown binary op: "+str(node.op))
        if isinstance(node, ast.AssignNode):
            val = self.eval(node.expr)
            self.vars[node.varname] = val
            return val
        if isinstance(node, ast.PrintNode):
            val = self.eval(node.expr)
            print(val)
            return val
        if isinstance(node, ast.LLMResolvedNode):
            # Handle LLM-resolved nodes by delegating to execute_compute
            if node.is_llm_resolved:
                print(f"  ℹ️  LLM Resolution: '{node.original_phrase}' → {node.resolved_op}")
                if node.reasoning:
                    print(f"     Reasoning: {node.reasoning}")
            return self.execute_compute(node.resolved_op, node.target)
        if isinstance(node, ast.ComputeNode):
            # Log if LLM-resolved
            if node.is_llm_resolved and node.llm_metadata:
                print(f"  ℹ️  LLM Resolution: '{node.llm_metadata.get('original_phrase')}' → {node.op}")
                if node.llm_metadata.get('reasoning'):
                    print(f"     Reasoning: {node.llm_metadata.get('reasoning')}")
            return self.execute_compute(node.op, node.target)
        if isinstance(node, ast.MapNode):
            if node.is_llm_resolved and node.llm_metadata:
                print(f"  ℹ️  LLM Resolution in map: '{node.llm_metadata.get('original_phrase')}' → {node.op}")
            return self.execute_map(node)
        if isinstance(node, ast.ReduceNode):
            if node.is_llm_resolved and node.llm_metadata:
                print(f"  ℹ️  LLM Resolution in reduce: '{node.llm_metadata.get('original_phrase')}' → {node.op}")
            return self.execute_reduce(node)
        if isinstance(node, ast.IfNode):
            l = self.eval(node.left); r = self.eval(node.right)
            if self.compare(l, r, node.comp):
                return self.eval(node.action)
            return None
        if isinstance(node, ast.FilterNode):
             return self.visit_FilterNode(node)
        if isinstance(node, ast.SequenceNode):
            first_out = self.eval(node.first)
            # when second expects input, if it is a ComputeNode with target variable, pass list
            # we'll support composition where second uses result of first as its implicit input
            # For simplicity: if second is ComputeNode and its target is VariableNode named "_" then replace it
            if isinstance(node.second, ast.ComputeNode) and isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                node.second.target = ast.ListNode([ast.NumberNode(x) for x in first_out])
                return self.eval(node.second)
            # otherwise just evaluate second normally, allowing side-effects
            return self.eval(node.second)
        raise SemanticError("Unhandled AST node: "+str(node))

    def compare(self, l, r, comp):
        if comp == ">": return l > r
        if comp == "<": return l < r
        if comp == "==": return l == r
        if comp == "!=": return l != r
        if comp == ">=": return l >= r
        if comp == "<=": return l <= r
        raise SemanticError("Unknown comparator: "+str(comp))

    def ensure_numeric_list(self, lst):
        if not isinstance(lst, list):
            raise SemanticError("Expected list for operation")
        if len(lst) == 0:
            raise SemanticError("List must be non-empty")
        for x in lst:
            if not isinstance(x, (int, float)):
                raise SemanticError("List must be numeric")
        return True

    def execute_compute(self, op, target):
        # target can be AST node
        tval = self.eval(target) if hasattr(target, '__class__') else target
        # if target is a scalar, wrap?
        if isinstance(tval, (int,float)):
            return tval
        if op == "OP_SUM":
            self.ensure_numeric_list(tval); return sum(tval)
        if op == "OP_MEAN":
            self.ensure_numeric_list(tval); return sum(tval)/len(tval)
        if op == "OP_PRODUCT":
            self.ensure_numeric_list(tval)
            prod=1
            for x in tval: prod*=x
            return prod
        if op == "OP_MAX":
            self.ensure_numeric_list(tval); return max(tval)
        if op == "OP_MIN":
            self.ensure_numeric_list(tval); return min(tval)
        if op == "OP_SORT_ASC":
            if not isinstance(tval, list): raise SemanticError("Sort target must be list")
            return sorted(tval)
        if op == "OP_SORT_DESC":
            if not isinstance(tval, list): raise SemanticError("Sort target must be list")
            return sorted(tval, reverse=True)
        raise SemanticError("Unknown compute op: "+str(op))

    def execute_map(self, node: ast.MapNode):
        tval = self.eval(node.target)
        self.ensure_numeric_list(tval)
        op = node.op
        arg = node.arg if node.arg is not None else None
        out = []
        if op == "OP_MAP" or op == "map" or op == "OP_MAP_ADD" or op == "OP_SUM":
            # default map must have arg for arithmetic add/mul; we'll support basic ops through op string
            for x in tval:
                if arg is None: raise SemanticError("Map requires numeric argument for arithmetic")
                out.append(x + arg)
            return out
        # if op maps to OP_MAP with inner meaning like OP_MAP_MULTIPLY
        if op in ("multiply","product","op_product","OP_PRODUCT"):
            if arg is None: raise SemanticError("Map multiply requires argument")
            for x in tval: out.append(x * arg)
            return out
        # support simple verbs "add" and "multiply"
        if op == "add":
            if arg is None: raise SemanticError("Map add requires argument")
            for x in tval: out.append(x + arg)
            return out
        if op == "multiply":
            if arg is None: raise SemanticError("Map multiply requires argument")
            for x in tval: out.append(x * arg)
            return out
        raise SemanticError("Unknown map op: "+str(op))

    def execute_reduce(self, node: ast.ReduceNode):
        tval = self.eval(node.target)
        self.ensure_numeric_list(tval)
        op = node.op
        if op in ("OP_REDUCE","reduce","op_reduce"):
            # default: sum
            return sum(tval)
        if op in ("add","sum","OP_SUM"):
            return sum(tval)
        if op in ("multiply","product","OP_PRODUCT"):
            prod=1
            for x in tval: prod*=x
            return prod
        raise SemanticError("Unknown reduce op: "+str(op))

    def visit_FilterNode(self, node):
        target_val = self.eval(node.target)
        if not isinstance(target_val, list):
             raise SemanticError(f"Filter target must be a list, got {target_val}")
        
        comp_val = self.eval(node.value)
        # support standard ops
        op = node.op
        
        res = []
        for x in target_val:
            if not isinstance(x, (int, float)): continue
            if op == ">" and x > comp_val: res.append(x)
            elif op == "<" and x < comp_val: res.append(x)
            elif op == ">=" and x >= comp_val: res.append(x)
            elif op == "<=" and x <= comp_val: res.append(x)
            elif op == "==" and x == comp_val: res.append(x)
            elif op == "!=" and x != comp_val: res.append(x)
            
        return res
