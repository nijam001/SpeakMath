# llm_layer.py
import os
import json
import re
import concurrent.futures
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional, Dict, Union
from .semantic_map import SYNONYM_MAP, SEMANTIC_MAP

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    pass


def parse_llm_json_response(response_text: str) -> Optional[Dict[str, str]]:
    """
    Helper function to parse LLM JSON response with error handling.
    
    Args:
        response_text: Raw text response from LLM
        
    Returns:
        Dictionary with 'operator' and 'reasoning' keys, or None if parsing fails
    """
    if not response_text or not response_text.strip():
        return None
    
    try:
        # Try to parse as JSON
        parsed = json.loads(response_text.strip())
        
        # Validate structure
        if not isinstance(parsed, dict):
            return None
            
        # Ensure required keys exist
        if "operator" not in parsed:
            return None
            
        return {
            "operator": parsed.get("operator"),
            "reasoning": parsed.get("reasoning", "")
        }
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                return {
                    "operator": parsed.get("operator"),
                    "reasoning": parsed.get("reasoning", "")
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to find operator in plain text
        valid_ops = list(set(list(SEMANTIC_MAP.values())))
        for op in valid_ops:
            if op in response_text:
                return {
                    "operator": op,
                    "reasoning": "Extracted from fallback parsing"
                }
        
        return None


def validate_operator(operator: str, valid_operators: list) -> bool:
    """
    Helper function to validate that an operator is in the valid set.
    
    Args:
        operator: Operator string to validate
        valid_operators: List of valid operator strings
        
    Returns:
        True if operator is valid, False otherwise
    """
    return operator in valid_operators or operator == "UNKNOWN"

def resolve_phrase(phrase: str) -> str:
    """
    Resolve a verb phrase to a canonical operator token.
    First check direct mapping, then synonym map; otherwise use Gemini API.
    """
    key = phrase.lower().strip()
    
    # 1. Direct Lookup
    if key in SEMANTIC_MAP:
        return SEMANTIC_MAP[key]
    
    # 2. Synonym Lookup
    if key in SYNONYM_MAP:
        return SYNONYM_MAP[key]
    
    # 3. Heuristic / Pattern Matching (Legacy)
    if "mean" in key or "average" in key:
        return "OP_MEAN"
    
    # 4. LLM Fallback
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Cannot resolve unknown phrase via LLM.")
        return None
        
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        valid_ops = list(set(list(SEMANTIC_MAP.values())))
        
        prompt = f"""
        You are a semantic mapper for the "SpeakMath" language.
        Map the user's natural language phrase to one of the following valid operators:
        {valid_ops}
        
        Return a JSON object with:
        - "operator": The valid operator name (e.g., "OP_SUM"), or "UNKNOWN" if no match.
        - "reasoning": A brief explanation of why you chose this operator.
        
        Examples:
        Phrase: "tally up the numbers" -> {{"operator": "OP_SUM", "reasoning": "Tally up implies addition."}}
        Phrase: "where is UM?" -> {{"operator": "UNKNOWN", "reasoning": "This is a question about location, not a math operation."}}
        
        Phrase: "{phrase}"
        """
        
        def call_gemini():
             return model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(call_gemini)
                response = future.result(timeout=5)
        except concurrent.futures.TimeoutError:
            print("\n(LLM is not available: Request timed out > 5s)")
            return None
            
        # Use helper function for JSON parsing
        parsed = parse_llm_json_response(response.text)
        if parsed:
            op = parsed.get("operator")
            if op and validate_operator(op, valid_ops) and op != "UNKNOWN":
                return parsed
            # Return with None operator if UNKNOWN or invalid
            return {"operator": None, "reasoning": parsed.get("reasoning", "No match found")}
        
        return None
        
    except concurrent.futures.TimeoutError:
        print("\n(LLM is not available: Request timed out > 5s)")
        return None
    except Exception as e:
        # Catch network errors, auth errors, API errors, etc.
        error_msg = str(e)
        if "API key" in error_msg.lower() or "authentication" in error_msg.lower():
            print(f"\n(LLM authentication error: Please check your GEMINI_API_KEY)")
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            print(f"\n(LLM quota/rate limit exceeded: {error_msg})")
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            print(f"\n(LLM network error: {error_msg})")
        else:
            print(f"\n(LLM is not available: {error_msg})")
        return None
