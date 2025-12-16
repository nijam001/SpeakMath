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
        error_type: str,
        token: str,
        position: int,
        message: str,
        suggestion: Optional[str] = None,
        context: Optional[str] = None
    ):
        self.error_type = error_type
        self.token = token
        self.position = position
        self.message = message
        self.suggestion = suggestion
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "error_type": self.error_type,
            "token": self.token,
            "position": self.position,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context
        }
    
    def __repr__(self):
        return f"FailureObject({self.error_type}: {self.message} at pos {self.position})"
    
    def format_error(self) -> str:
        """Format error for user-friendly display"""
        lines = []
        lines.append(f"❌ {self.error_type.replace('_', ' ').title()}")
        lines.append(f"   Token: '{self.token}' at position {self.position}")
        lines.append(f"   {self.message}")
        
        if self.suggestion:
            lines.append(f"   💡 Suggestion: {self.suggestion}")
        
        if self.context:
            lines.append(f"   Context: \"{self.context}\"")
        
        return "\n".join(lines)


class ParseResult:
    """
    Result object returned by parser.
    Contains either a successful AST or a structured failure.
    """
    
    def __init__(
        self,
        success: bool,
        ast_node: Optional[ast.ASTNode] = None,
        error: Optional[FailureObject] = None
    ):
        self.success = success
        self.ast_node = ast_node
        self.error = error
    
    def __repr__(self):
        if self.success:
            return f"ParseResult(success=True, ast={self.ast_node})"
        else:
            return f"ParseResult(success=False, error={self.error})"
    
    @staticmethod
    def success_result(ast_node: ast.ASTNode):
        """Create a successful parse result"""
        return ParseResult(success=True, ast_node=ast_node, error=None)
    
    @staticmethod
    def failure_result(error: FailureObject):
        """Create a failed parse result"""
        return ParseResult(success=False, ast_node=None, error=error)


def create_lexical_failure(token: str, position: int, context: str, suggestion: str = None) -> FailureObject:
    """Helper to create lexical failure objects"""
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
    return FailureObject(
        error_type=FailureObject.ERROR_SYNTAX,
        token=got,
        position=position,
        message=f"Expected {expected}, got {got}",
        suggestion=None,
        context=context
    )
