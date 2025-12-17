
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
        if isinstance(node, ast.ComputeNode):
            return self.execute_compute(node.op, node.target)
        if isinstance(node, ast.MapNode):
            return self.execute_map(node)
        if isinstance(node, ast.ReduceNode):
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
            
            # Enhanced composition support:
            # 1. If second is ComputeNode with "_" variable, replace with first result
            if isinstance(node.second, ast.ComputeNode) and isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                # Convert first output to appropriate AST node
                if isinstance(first_out, list):
                    node.second.target = ast.ListNode([ast.NumberNode(x) if isinstance(x, (int, float)) else ast.NumberNode(0) for x in first_out])
                else:
                    node.second.target = ast.NumberNode(first_out) if isinstance(first_out, (int, float)) else ast.NumberNode(0)
                return self.eval(node.second)
            
            # 2. If second is MapNode/ReduceNode with "_" target, replace with first result
            if isinstance(node.second, (ast.MapNode, ast.ReduceNode)) and isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                if isinstance(first_out, list):
                    node.second.target = ast.ListNode([ast.NumberNode(x) if isinstance(x, (int, float)) else ast.NumberNode(0) for x in first_out])
                else:
                    # If first output is scalar, wrap in list for map/reduce
                    if isinstance(first_out, (int, float)):
                        node.second.target = ast.ListNode([ast.NumberNode(first_out)])
                    else:
                        node.second.target = ast.ListNode([])
                return self.eval(node.second)
            
            # 3. If first output is a list and second is a functional operation, try to use it
            if isinstance(first_out, list) and isinstance(node.second, (ast.ComputeNode, ast.MapNode, ast.ReduceNode)):
                # Create a temporary variable to hold first result
                temp_var = "_temp_composition"
                self.vars[temp_var] = first_out
                # Replace target if it's a variable reference to "_"
                if isinstance(node.second.target, ast.VariableNode) and node.second.target.name == "_":
                    node.second.target = ast.VariableNode(temp_var)
                result = self.eval(node.second)
                # Clean up temp variable
                if temp_var in self.vars:
                    del self.vars[temp_var]
                return result
            
            # 4. Otherwise, evaluate second normally (allows side-effects like assignments)
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

    def ensure_numeric_list(self, lst, allow_empty=False):
        if not isinstance(lst, list):
            raise SemanticError("Expected list for operation")
        if len(lst) == 0 and not allow_empty:
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
        # Allow empty lists for map (returns empty list)
        if not isinstance(tval, list):
            raise SemanticError("Map target must be a list")
        if len(tval) == 0:
            return []
        
        self.ensure_numeric_list(tval, allow_empty=True)
        op = node.op
        arg = node.arg if node.arg is not None else None
        out = []
        
        # Normalize operation name
        op_lower = op.lower() if isinstance(op, str) else str(op).lower()
        
        # Addition operations
        if op_lower in ("op_map", "map", "op_map_add", "op_sum", "add", "sum"):
            if arg is None:
                raise SemanticError("Map add requires numeric argument")
            for x in tval:
                out.append(x + arg)
            return out
        
        # Multiplication operations
        if op_lower in ("multiply", "product", "op_product", "op_map_multiply"):
            if arg is None:
                raise SemanticError("Map multiply requires numeric argument")
            for x in tval:
                out.append(x * arg)
            return out
        
        # Subtraction (if needed)
        if op_lower in ("subtract", "minus", "op_subtract"):
            if arg is None:
                raise SemanticError("Map subtract requires numeric argument")
            for x in tval:
                out.append(x - arg)
            return out
        
        # Division (if needed)
        if op_lower in ("divide", "op_divide"):
            if arg is None:
                raise SemanticError("Map divide requires numeric argument")
            if arg == 0:
                raise SemanticError("Division by zero")
            for x in tval:
                out.append(x / arg)
            return out
        
        raise SemanticError(f"Unknown map operation: {op}")

    def execute_reduce(self, node: ast.ReduceNode):
        tval = self.eval(node.target)
        if not isinstance(tval, list):
            raise SemanticError("Reduce target must be a list")
        if len(tval) == 0:
            raise SemanticError("Cannot reduce empty list")
        
        self.ensure_numeric_list(tval)
        op = node.op
        
        # Normalize operation name
        op_lower = op.lower() if isinstance(op, str) else str(op).lower()
        
        # Sum operations
        if op_lower in ("op_reduce", "reduce", "op_reduce", "add", "sum", "op_sum"):
            return sum(tval)
        
        # Product operations
        if op_lower in ("multiply", "product", "op_product"):
            prod = 1
            for x in tval:
                prod *= x
            return prod
        
        # Max operation
        if op_lower in ("max", "op_max", "maximum"):
            return max(tval)
        
        # Min operation
        if op_lower in ("min", "op_min", "minimum"):
            return min(tval)
        
        raise SemanticError(f"Unknown reduce operation: {op}")

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
