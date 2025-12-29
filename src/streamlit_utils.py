import sys
import io
import contextlib
import streamlit as st
from .lexer import lex
from .parser import Parser
from .interpreter import Interpreter

@contextlib.contextmanager
def capture_output():
    new_out = io.StringIO()
    old_out = sys.stdout
    sys.stdout = new_out
    try:
        yield new_out
    finally:
        sys.stdout = old_out

def execute_with_pipeline(text: str, interp: Interpreter):
    """
    Executes a SpeakMath command and captures each stage of the pipeline.
    Returns: (result, pipeline_data, updated_interpreter)
    """
    pipeline = {
        'tokens': None,
        'ast': None,
        'logs': "",
        'result': None,
        'error': None
    }
    
    try:
        # Stage 1: Lexer
        tokens = lex(text)
        # Store simple token repr for display
        pipeline['tokens'] = [{'type': t.type, 'value': t.value} for t in tokens]
        
        # Stage 2: Parser
        parser = Parser(tokens)
        parser.set_source(text) # Provide source text for debug capture
        ast_node = parser.parse()
        pipeline['ast'] = repr(ast_node)
        pipeline['ast_node'] = ast_node # Store actual object for visualization
        
        # Stage 3: Interpreter
        # Retrieve source from AST metadata if available (for logic display)
        # We can inspect the node before execution if needed, but logging happens during execution
        
        with capture_output() as output:
            res = interp.eval(ast_node)
            
        pipeline['result'] = res
        pipeline['logs'] = output.getvalue()
        
    except Exception as e:
        pipeline['error'] = str(e)
        
    return pipeline, interp


def get_variable_state(interp: Interpreter) -> dict:
    """Extracts current variable state from interpreter."""
    if hasattr(interp, 'vars'):
        return interp.vars.copy()
    return {}

def format_ast_to_dot(node) -> str:
    """
    Converts AST node tree into a Graphviz DOT string.
    """
    if not node:
        return ""
        
    dot_lines = ["digraph AST {", "  node [shape=box style=filled fontname=\"Sans-Serif\"];"]
    
    # Counter for unique node IDs
    counter = 0
    
    def visit(n):
        nonlocal counter
        node_id = f"node{counter}"
        counter += 1
        
        label = n.__class__.__name__
        color = "#e8f4f8"  # default light blue
        
        # Customize label/color based on node type
        if hasattr(n, 'op'):
            label += f"\\nOp: {n.op}"
            color = "#ffecb3" # amber for operations
        
        if hasattr(n, 'cmd'):
            label += f"\\nCmd: {n.cmd}"
        
        if hasattr(n, 'value'): # NumberNode, FilterNode
            label += f"\\nVal: {n.value}"
            if "NumberNode" in label: color = "#c8e6c9" # green for numbers/values
            
        if hasattr(n, 'name'): # VariableNode
            label += f"\\nVar: {n.name}"
            color = "#dcedc8"
            
        if hasattr(n, 'llm_metadata') and n.llm_metadata:
            source = n.llm_metadata.get('source', '')
            if source == "AI":
                label += "\\n(AI Resolved)"
                color = "#e1bee7" # purple for AI

        # Show source debug info
        if hasattr(n, 'debug_info') and n.debug_info.get('source'):
             src_text = n.debug_info['source'][:20] + "..." if len(n.debug_info['source']) > 20 else n.debug_info['source']
             label += f"\\nSrc: '{src_text}'"

        dot_lines.append(f"  {node_id} [label=\"{label}\" fillcolor=\"{color}\"];")
        
        # Traverse children
        children = []
        if hasattr(n, 'first'): children.append(('first', n.first))
        if hasattr(n, 'second'): children.append(('second', n.second))
        if hasattr(n, 'target'): children.append(('target', n.target))
        if hasattr(n, 'left'): children.append(('left', n.left))
        if hasattr(n, 'right'): children.append(('right', n.right))
        if hasattr(n, 'expr'): children.append(('expr', n.expr))
        if hasattr(n, 'action'): children.append(('action', n.action))
        if hasattr(n, 'arg') and n.arg is not None: 
            # Args might be primitives or nodes? usually primitives in MapNode
            # If primitive, make a leaf node
            child_id = f"node{counter}"
            counter += 1
            dot_lines.append(f"  {child_id} [label=\"Arg: {n.arg}\" shape=ellipse fillcolor=\"#f5f5f5\"];")
            dot_lines.append(f"  {node_id} -> {child_id} [label=\"arg\"];")

        if hasattr(n, 'values'): # ListNode
            for i, val in enumerate(n.values):
                children.append((f"[{i}]", val))
                
        for edge_label, child in children:
            if child:
                child_id = visit(child)
                dot_lines.append(f"  {node_id} -> {child_id} [label=\"{edge_label}\" fontsize=10 color=\"#888888\"];")
                
        return node_id

    visit(node)
    dot_lines.append("}")
    return "\n".join(dot_lines)

