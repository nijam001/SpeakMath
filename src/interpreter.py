
# interpreter.py
from . import ast
from typing import Any

class SemanticError(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.vars = {}
        # Dispatch table for eval
        self.eval_dispatch = {
            ast.NumberNode: lambda n: n.value,
            ast.VariableNode: self.eval_variable,
            ast.ListNode: lambda n: [self.eval(v) for v in n.values],
            ast.BinaryOpNode: self.eval_binary_op,
            ast.AssignNode: self.eval_assign,
            ast.PrintNode: self.eval_print,
            ast.ComputeNode: self.eval_compute,
            ast.MapNode: self.execute_map,
            ast.ReduceNode: self.execute_reduce,
            ast.IfNode: self.eval_if,
            ast.FilterNode: self.visit_FilterNode,
            ast.SequenceNode: self.eval_sequence,
        }
        
        # Dispatch table for compute operations
        self.compute_dispatch = {
            "OP_SUM": lambda v: sum(v),
            "OP_MEAN": lambda v: sum(v)/len(v),
            "OP_PRODUCT": self._compute_product,
            "OP_MAX": lambda v: max(v),
            "OP_MIN": lambda v: min(v),
            "OP_SORT_ASC": lambda v: sorted(v),
            "OP_SORT_DESC": lambda v: sorted(v, reverse=True),
        }

    def eval(self, node: ast.ASTNode) -> Any:
        handler = self.eval_dispatch.get(type(node))
        if handler:
            return handler(node)
        raise SemanticError("Unhandled AST node: "+str(node))

    def eval_variable(self, node: ast.VariableNode):
        if node.name not in self.vars:
            raise SemanticError(f"Undefined variable: {node.name}")
        return self.vars[node.name]

    def eval_binary_op(self, node: ast.BinaryOpNode):
        l = self.eval(node.left); r = self.eval(node.right)
        if node.op == "+": return l + r
        if node.op == "-": return l - r
        if node.op == "*": return l * r
        if node.op == "/": return l / r
        raise SemanticError("Unknown binary op: "+str(node.op))

    def eval_assign(self, node: ast.AssignNode):
        val = self.eval(node.expr)
        self.vars[node.varname] = val
        return val

    def eval_print(self, node: ast.PrintNode):
        val = self.eval(node.expr)
        print(val)
        return val

    def eval_compute(self, node: ast.ComputeNode):
        self._log_resolution(node)
        return self.execute_compute(node.op, node.target)

    def eval_if(self, node: ast.IfNode):
        l = self.eval(node.left); r = self.eval(node.right)
        if self.compare(l, r, node.comp):
            return self.eval(node.action)
        return None

    def eval_sequence(self, node: ast.SequenceNode):
        first_out = self.eval(node.first)
        
        # Enhanced composition handling
        if isinstance(node.second, (ast.ComputeNode, ast.MapNode, ast.ReduceNode)):
            # If target is explicit placeholder "_"
            if hasattr(node.second, 'target') and isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                converted_target = self._convert_to_node(first_out, isinstance(node.second, (ast.MapNode, ast.ReduceNode)))
                node.second.target = converted_target
                return self.eval(node.second)

            # Implicit composition for list results into functional ops
            if isinstance(first_out, list):
                # Use temp variable strategy
                temp_var = "_temp_composition"
                self.vars[temp_var] = first_out
                if isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                    node.second.target = ast.VariableNode(temp_var)
                
                result = self.eval(node.second)
                if temp_var in self.vars: del self.vars[temp_var]
                return result

        # Standard sequence evaluation
        return self.eval(node.second)

    def _convert_to_node(self, value, prefer_list=False):
        if isinstance(value, list):
            return ast.ListNode([ast.NumberNode(x) if isinstance(x, (int, float)) else ast.NumberNode(0) for x in value])
        
        if prefer_list:
             if isinstance(value, (int, float)):
                 return ast.ListNode([ast.NumberNode(value)])
             return ast.ListNode([])
             
        return ast.NumberNode(value) if isinstance(value, (int, float)) else ast.NumberNode(0)

    def compare(self, l, r, comp):
        if comp == ">": return l > r
        if comp == "<": return l < r
        if comp == "==": return l == r
        if comp == "!=": return l != r
        if comp == ">=": return l >= r
        if comp == "<=": return l <= r
        raise SemanticError("Unknown comparator: "+str(comp))

    def ensure_numeric_list(self, lst, allow_empty=False):
        if not isinstance(lst, list):
            raise SemanticError("Expected list for operation")
        if len(lst) == 0 and not allow_empty:
            raise SemanticError("List must be non-empty")
        for x in lst:
            if not isinstance(x, (int, float)):
                raise SemanticError("List must be numeric")
        return True

    def _compute_product(self, tval):
        prod=1
        for x in tval: prod*=x
        return prod
    
    def _log_resolution(self, node):
        """Helper to log resolution info if present"""
        if not hasattr(node, 'llm_metadata') or not node.llm_metadata:
            return
            
        try:
            phrase = node.llm_metadata.get('original_phrase')
            op = node.op
            source = node.llm_metadata.get('source', 'Unknown')
            reasoning = node.llm_metadata.get('reasoning')
            
            # Print format: "ℹ️ [Source] 'phrase' -> OP"
            print(f"  ℹ️  [{source}] Resolution: '{phrase}' → {op}")
            if reasoning:
                print(f"      Reasoning: {reasoning}")
        except:
            pass

    def execute_compute(self, op, target):
        tval = self.eval(target) if hasattr(target, '__class__') else target
        if isinstance(tval, (int,float)):
            return tval
            
        handler = self.compute_dispatch.get(op)
        if handler:
            if "SORT" in op:
                 if not isinstance(tval, list): raise SemanticError("Sort target must be list")
            else:
                 self.ensure_numeric_list(tval)
                 
            return handler(tval)
            
        raise SemanticError("Unknown compute op: "+str(op))

    def execute_map(self, node: ast.MapNode):
        self._log_resolution(node)
        tval = self.eval(node.target)
        if not isinstance(tval, list):
            raise SemanticError("Map target must be a list")
        if len(tval) == 0:
            return []
        
        self.ensure_numeric_list(tval, allow_empty=True)
        op = node.op
        arg = node.arg
        
        # Resolve variable argument if it's a variable name
        if isinstance(arg, str) and arg in self.vars:
            arg = self.vars[arg]
            
        out = []
        
        op_lower = str(op).lower()
        
        # Dispatch map logic? For now keep simple ifs as they handle group synonyms
        if op_lower in ("op_map", "map", "op_map_add", "op_sum", "add", "sum"):
            if arg is None: raise SemanticError("Map add requires numeric argument")
            return [x + arg for x in tval]
        
        if op_lower in ("multiply", "product", "op_product", "op_map_multiply"):
            if arg is None: raise SemanticError("Map multiply requires numeric argument")
            return [x * arg for x in tval]
            
        if op_lower in ("subtract", "minus", "op_subtract"):
            if arg is None: raise SemanticError("Map subtract requires numeric argument")
            return [x - arg for x in tval]
            
        if op_lower in ("divide", "op_divide"):
            if arg is None: raise SemanticError("Map divide requires numeric argument")
            if arg == 0: raise SemanticError("Division by zero")
            return [x / arg for x in tval]
        
        raise SemanticError(f"Unknown map operation: {op}")

    def execute_reduce(self, node: ast.ReduceNode):
        self._log_resolution(node)
        tval = self.eval(node.target)
        if not isinstance(tval, list): raise SemanticError("Reduce target must be a list")
        if len(tval) == 0: raise SemanticError("Cannot reduce empty list")
        
        self.ensure_numeric_list(tval)
        op = str(node.op).lower()
        
        if op in ("op_reduce", "reduce", "add", "sum", "op_sum"):
            return sum(tval)
        if op in ("multiply", "product", "op_product"):
            return self._compute_product(tval)
        if op in ("max", "op_max", "maximum"):
            return max(tval)
        if op in ("min", "op_min", "minimum"):
            return min(tval)
        
        raise SemanticError(f"Unknown reduce operation: {node.op}")

    def visit_FilterNode(self, node):
        target_val = self.eval(node.target)
        if not isinstance(target_val, list):
             raise SemanticError(f"Filter target must be a list, got {target_val}")
        
        comp_val = self.eval(node.value)
        op = node.op
        
        # Use existing compare logic
        return [x for x in target_val if isinstance(x, (int, float)) and self.compare(x, comp_val, op)]
