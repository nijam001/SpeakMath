# llm_layer.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
from .semantic_map import SYNONYM_MAP, SEMANTIC_MAP

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

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
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        import json
        try:
            res = json.loads(response.text.strip())
            op = res.get("operator")
            if op in valid_ops:
                return {"operator": op, "reasoning": res.get("reasoning", "")}
            return {"operator": None, "reasoning": res.get("reasoning", "No match found")}
        except json.JSONDecodeError:
            # Fallback if model fails to output JSON (rare with flash-2.0 + json mode)
            text = response.text.strip()
            if text in valid_ops:
                return {"operator": text, "reasoning": "Fallback parsing"}
            return None
        
    except Exception as e:
        # Silently fail - system will use grammar-only mode
        # (Error details available for debugging if needed)
        return None
