# parse_result.py
"""
Structured result objects for parser operations.
Provides detailed error information and success/failure tracking.
"""

from typing import Optional, Dict, Any
from . import ast

class FailureObject:
    """
    Structured error object for parse failures.
    Provides context and suggestions for debugging.
    """
    ERROR_LEXICAL = "lexical_failure"
    ERROR_SEMANTIC = "semantic_failure"
    ERROR_SYNTAX = "syntax_error"
    
    def __init__(
        self,
        error_type: str,        # Type of error: lexical, semantic, or syntax
        token: str,             # The problematic token that caused the error
        position: int,          # Character position in the input where error occurred
        message: str,           # Human-readable error message
        suggestion: Optional[str] = None,  # Optional helpful suggestion for fixing the error
        context: Optional[str] = None      # Optional surrounding text for context
    ):
        # Store all error details for later retrieval and formatting
        self.error_type = error_type
        self.token = token
        self.position = position
        self.message = message
        self.suggestion = suggestion
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        # Create dictionary with all error information
        # Useful for logging, API responses, or saving errors to files
        return {
            "error_type": self.error_type,
            "token": self.token,
            "position": self.position,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context
        }
    
    def __repr__(self):
        """String representation for debugging"""
        # Returns concise one-line summary of the error for debugging
        return f"FailureObject({self.error_type}: {self.message} at pos {self.position})"
    
    def format_error(self) -> str:
        """Format error for user-friendly display"""
        # Build multi-line formatted error message for console output
        lines = []
        
        # Add error type header (e.g., "❌ Semantic Failure")
        lines.append(f"❌ {self.error_type.replace('_', ' ').title()}")
        
        # Add token and position information
        lines.append(f"   Token: '{self.token}' at position {self.position}")
        
        # Add the error message
        lines.append(f"   {self.message}")
        
        # Add optional suggestion if available
        if self.suggestion:
            lines.append(f"   💡 Suggestion: {self.suggestion}")
        
        # Add optional context if available
        if self.context:
            lines.append(f"   Context: \"{self.context}\"")
        
        # Join all lines with newlines for pretty printing
        return "\n".join(lines)


class ParseResult:
    """
    Result object returned by parser.
    Contains either a successful AST or a structured failure.
    """
    
    def __init__(
        self,
        success: bool,                        # True if parsing succeeded, False if failed
        ast_node: Optional[ast.ASTNode] = None,  # AST node if success=True, None otherwise
        error: Optional[FailureObject] = None    # Error object if success=False, None otherwise
    ):
        # Store parse result - either success with AST or failure with error
        # This follows the Result pattern: exactly one of (ast_node, error) should be set
        self.success = success
        self.ast_node = ast_node
        self.error = error
    
    def __repr__(self):
        """String representation for debugging"""
        # Show either the AST (if success) or the error (if failure)
        if self.success:
            return f"ParseResult(success=True, ast={self.ast_node})"
        else:
            return f"ParseResult(success=False, error={self.error})"
    
    @staticmethod
    def success_result(ast_node: ast.ASTNode):
        """Create a successful parse result"""
        # Factory method for creating a successful parse result
        # Used by parser when AST is successfully built
        return ParseResult(success=True, ast_node=ast_node, error=None)
    
    @staticmethod
    def failure_result(error: FailureObject):
        """Create a failed parse result"""
        # Factory method for creating a failed parse result
        # Used by parser when an error occurs during parsing
        return ParseResult(success=False, ast_node=None, error=error)


def create_lexical_failure(token: str, position: int, context: str, suggestion: str = None) -> FailureObject:
    """Helper to create lexical failure objects"""
    # Convenience function for creating lexical errors
    # Lexical failures occur when a token/keyword is not recognized by the lexer
    # Example: "foobar" is not a valid keyword in the language
    return FailureObject(
        error_type=FailureObject.ERROR_LEXICAL,
        token=token,
        position=position,
        message=f"Unknown keyword '{token}'",
        suggestion=suggestion,
        context=context
    )


def create_semantic_failure(token: str, position: int, context: str, suggestion: str = None) -> FailureObject:
    """Helper to create semantic failure objects"""
    # Convenience function for creating semantic errors
    # Semantic failures occur when syntax is valid but operation meaning is unknown
    # Example: "median" has valid syntax but isn't in SEMANTIC_MAP
    return FailureObject(
        error_type=FailureObject.ERROR_SEMANTIC,
        token=token,
        position=position,
        message=f"Unknown operation '{token}'",
        suggestion=suggestion or "This operation is not currently supported",
        context=context
    )


def create_syntax_failure(expected: str, got: str, position: int, context: str) -> FailureObject:
    """Helper to create syntax error objects"""
    # Convenience function for creating syntax errors
    # Syntax failures occur when token sequence doesn't match grammar rules
    # Example: Missing closing bracket, unexpected token, etc.
    return FailureObject(
        error_type=FailureObject.ERROR_SYNTAX,
        token=got,
        position=position,
        message=f"Expected {expected}, got {got}",
        suggestion=None,  # Syntax errors typically don't have suggestions
        context=context
    )
