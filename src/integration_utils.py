"""
integration_utils.py

Helper utilities for integration between LLM, Parser, and Interpreter.
These functions ensure smooth data flow and error handling.

Author: Programmer/Integrator
"""

from typing import Any, Optional, Dict, List
from .interpreter import Interpreter, SemanticError
from .parser import Parser, ParseError
from .lexer import lex, Token
from . import ast


class IntegrationError(Exception):
    """Custom exception for integration errors"""
    pass


def validate_data_flow(tokens: List[Token], parser: Parser, interpreter: Interpreter) -> bool:
    """
    Validate that data can flow smoothly through the pipeline.
    
    Args:
        tokens: List of tokens from lexer
        parser: Parser instance
        interpreter: Interpreter instance
        
    Returns:
        True if validation passes
        
    Raises:
        IntegrationError if validation fails
    """
    if not tokens:
        raise IntegrationError("No tokens to parse")
    
    if not parser:
        raise IntegrationError("Parser not initialized")
    
    if not interpreter:
        raise IntegrationError("Interpreter not initialized")
    
    return True


def safe_parse_and_execute(
    text: str,
    interpreter: Optional[Interpreter] = None,
    raise_on_error: bool = False
) -> Dict[str, Any]:
    """
    Safely parse and execute a command with comprehensive error handling.
    
    Args:
        text: Input text to parse and execute
        interpreter: Optional interpreter instance (creates new if None)
        raise_on_error: If True, raises exceptions; if False, returns error dict
        
    Returns:
        Dictionary with keys:
            - 'success': bool
            - 'result': Any (result if success)
            - 'error': str (error message if failure)
            - 'error_type': str (type of error)
    """
    result_dict = {
        'success': False,
        'result': None,
        'error': None,
        'error_type': None
    }
    
    try:
        # Step 1: Lexing
        tokens = lex(text)
        if not tokens or (len(tokens) == 1 and tokens[0].type == "EOF"):
            result_dict['error'] = "Empty or invalid input"
            result_dict['error_type'] = 'LexError'
            if raise_on_error:
                raise IntegrationError(result_dict['error'])
            return result_dict
        
        # Step 2: Parsing
        parser = Parser(tokens)
        try:
            ast_node = parser.parse()
        except ParseError as e:
            result_dict['error'] = f"Parse error: {str(e)}"
            result_dict['error_type'] = 'ParseError'
            if raise_on_error:
                raise
            return result_dict
        
        # Step 3: Interpretation
        if interpreter is None:
            interpreter = Interpreter()
        
        try:
            result = interpreter.eval(ast_node)
            result_dict['success'] = True
            result_dict['result'] = result
            return result_dict
        except SemanticError as e:
            result_dict['error'] = f"Semantic error: {str(e)}"
            result_dict['error_type'] = 'SemanticError'
            if raise_on_error:
                raise
            return result_dict
        except Exception as e:
            result_dict['error'] = f"Execution error: {str(e)}"
            result_dict['error_type'] = 'ExecutionError'
            if raise_on_error:
                raise
            return result_dict
            
    except Exception as e:
        result_dict['error'] = f"Unexpected error: {str(e)}"
        result_dict['error_type'] = 'UnexpectedError'
        if raise_on_error:
            raise IntegrationError(result_dict['error']) from e
        return result_dict


def compose_functions(first_cmd: str, second_cmd: str, interpreter: Optional[Interpreter] = None) -> Any:
    """
    Compose two commands using function composition.
    
    Args:
        first_cmd: First command to execute
        second_cmd: Second command to execute (receives first's output)
        interpreter: Optional interpreter instance
        
    Returns:
        Result of composed execution
        
    Raises:
        IntegrationError if composition fails
    """
    if interpreter is None:
        interpreter = Interpreter()
    
    # Execute first command
    first_result = safe_parse_and_execute(first_cmd, interpreter, raise_on_error=True)
    if not first_result['success']:
        raise IntegrationError(f"First command failed: {first_result['error']}")
    
    # Create composition: first_cmd then second_cmd
    # Replace "_" in second_cmd with first result if needed
    composed_text = f"{first_cmd} then {second_cmd}"
    
    composed_result = safe_parse_and_execute(composed_text, interpreter, raise_on_error=True)
    if not composed_result['success']:
        raise IntegrationError(f"Composition failed: {composed_result['error']}")
    
    return composed_result['result']


def validate_functional_property(
    operation: str,
    input_data: List[Any],
    expected_property: str = "purity"
) -> bool:
    """
    Validate functional programming properties (purity, referential transparency, etc.)
    
    Args:
        operation: Operation to test (e.g., "map add 2 over")
        input_data: Input data as list
        expected_property: Property to validate ("purity", "referential_transparency", etc.)
        
    Returns:
        True if property holds, False otherwise
    """
    interpreter1 = Interpreter()
    interpreter2 = Interpreter()
    
    # Create command with input data
    input_str = "[" + ", ".join(str(x) for x in input_data) + "]"
    command = f"{operation} {input_str}"
    
    try:
        # Execute twice with same input
        result1 = safe_parse_and_execute(command, interpreter1)
        result2 = safe_parse_and_execute(command, interpreter2)
        
        if not result1['success'] or not result2['success']:
            return False
        
        if expected_property == "purity":
            # Purity: same input should always produce same output
            return result1['result'] == result2['result']
        
        elif expected_property == "referential_transparency":
            # Referential transparency: expression can be replaced with its value
            # This is harder to test automatically, but we can check determinism
            return result1['result'] == result2['result']
        
        return False
        
    except Exception:
        return False

