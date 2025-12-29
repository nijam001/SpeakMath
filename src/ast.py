
# ast.py
class ASTNode:
    def __init__(self):
        self.debug_info = {} # Stores visualizer/debugger metadata like source text


class CommandNode(ASTNode):
    def __init__(self, cmd):
        self.cmd = cmd
    def __repr__(self):
        return f"CommandNode({self.cmd})"

class ComputeNode(ASTNode):
    def __init__(self, op, target, is_llm_resolved=False, llm_metadata=None):
        self.op = op  # canonical op, e.g., OP_SUM
        self.target = target
        self.is_llm_resolved = is_llm_resolved
        self.llm_metadata = llm_metadata or {}
    def __repr__(self):
        llm_flag = " [LLM]" if self.is_llm_resolved else ""
        return f"ComputeNode({self.op}, {self.target}){llm_flag}"

class AssignNode(ASTNode):
    def __init__(self, varname, expr):
        self.varname = varname
        self.expr = expr
    def __repr__(self):
        return f"AssignNode({self.varname}, {self.expr})"

class IfNode(ASTNode):
    def __init__(self, left, comp, right, action):
        self.left = left
        self.comp = comp
        self.right = right
        self.action = action
    def __repr__(self):
        return f"IfNode({self.left} {self.comp} {self.right} then {self.action})"

class PrintNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"PrintNode({self.expr})"

class ListNode(ASTNode):
    def __init__(self, values):
        self.values = values
    def __repr__(self):
        return f"ListNode({self.values})"

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"NumberNode({self.value})"

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"VariableNode({self.name})"

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"BinaryOpNode({self.left} {self.op} {self.right})"

class FilterNode(ASTNode):
    def __init__(self, op, value, target):
        self.op = op
        self.value = value
        self.target = target
    def __repr__(self):
        return f"FilterNode({self.op}, {self.value}, {self.target})"

class MapNode(ASTNode):
    def __init__(self, op, arg, target, is_llm_resolved=False, llm_metadata=None):
        self.op = op  # canonical or operation name
        self.arg = arg
        self.target = target
        self.is_llm_resolved = is_llm_resolved
        self.llm_metadata = llm_metadata or {}
    def __repr__(self):
        llm_flag = " [LLM]" if self.is_llm_resolved else ""
        return f"MapNode({self.op}, {self.arg}, {self.target}){llm_flag}"

class ReduceNode(ASTNode):
    def __init__(self, op, target, is_llm_resolved=False, llm_metadata=None):
        self.op = op
        self.target = target
        self.is_llm_resolved = is_llm_resolved
        self.llm_metadata = llm_metadata or {}
    def __repr__(self):
        llm_flag = " [LLM]" if self.is_llm_resolved else ""
        return f"ReduceNode({self.op}, {self.target}){llm_flag}"

class SequenceNode(ASTNode):
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def __repr__(self):
        return f"SequenceNode({self.first} then {self.second})"
