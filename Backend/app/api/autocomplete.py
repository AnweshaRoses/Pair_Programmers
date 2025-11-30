# app/api/autocomplete.py
from fastapi import APIRouter
from pydantic import BaseModel
import re

router = APIRouter()

class AutocompleteRequest(BaseModel):
    code: str
    cursorPosition: int
    language: str = "python"

class AutocompleteResponse(BaseModel):
    suggestion: str

# Common Python imports
COMMON_IMPORTS = [
    "os", "sys", "json", "datetime", "random", "math", "collections",
    "itertools", "functools", "operator", "re", "pathlib", "typing"
]

# Common Python patterns
PATTERNS = {
    "import ": COMMON_IMPORTS[0],  # Default to first common import
    "from ": "module import ",
    "def ": "function_name():\n    pass",
    "class ": "ClassName:\n    def __init__(self):\n        pass",
    "if ": "condition:\n    pass",
    "elif ": "condition:\n    pass",
    "else:": "\n    pass",
    "for ": "item in iterable:\n    pass",
    "while ": "condition:\n    pass",
    "try:": "\n    pass\nexcept Exception as e:\n    pass",
    "with ": "open('file.txt') as f:\n    pass",
    "async def ": "function_name():\n    return",
    "lambda ": "x: x",
    "@": "decorator\n",
    "# ": "",  # Comment - no suggestion
}

def get_line_context(code: str, cursor: int) -> tuple[str, str, int]:
    """Extract the current line and context around cursor."""
    lines = code[:cursor].split('\n')
    current_line = lines[-1] if lines else ""
    before_lines = '\n'.join(lines[:-1]) if len(lines) > 1 else ""
    line_number = len(lines) - 1
    return current_line, before_lines, line_number

def get_indentation(line: str) -> str:
    """Get the indentation string for a line."""
    return re.match(r'^(\s*)', line).group(1) if line else ""

def detect_context(before_cursor: str, current_line: str) -> str:
    """Detect what the user is trying to write based on context."""
    stripped = current_line.rstrip()
    
    # Check for incomplete statements
    if stripped.endswith("(") and not stripped.endswith("()"):
        return ")"  # Complete parentheses
    
    if stripped.endswith("[") and not stripped.endswith("[]"):
        return "]"  # Complete brackets
    
    if stripped.endswith("{") and not stripped.endswith("{}"):
        return "}"  # Complete braces
    
    # Check for string quotes
    if stripped.count('"') % 2 == 1 and not stripped.endswith('\\"'):
        return '"'
    if stripped.count("'") % 2 == 1 and not stripped.endswith("\\'"):
        return "'"
    
    # Check for common patterns
    for pattern, suggestion in PATTERNS.items():
        if stripped.endswith(pattern) or stripped == pattern.rstrip():
            return suggestion
    
    # Check for incomplete function calls
    if re.search(r'\w+\([^)]*$', stripped):
        return ")"
    
    # Check for incomplete list/dict comprehensions
    if re.search(r'\[.*for.*$', stripped):
        return " in iterable]"
    if re.search(r'\{.*for.*$', stripped):
        return " in iterable}"
    
    # Check for incomplete operators
    if stripped.endswith("=") and not stripped.endswith("==") and not stripped.endswith("!="):
        return " value"
    
    # Check for incomplete comparisons
    if stripped.endswith("and ") or stripped.endswith("or "):
        return "condition"
    
    # Check for incomplete return/yield
    if stripped.endswith("return ") or stripped.endswith("yield "):
        return "value"
    
    # Check for incomplete raise
    if stripped.endswith("raise "):
        return "Exception('message')"
    
    # Check for incomplete assert
    if stripped.endswith("assert "):
        return "condition, 'message'"
    
    # Check for incomplete with statement
    if stripped.endswith("with ") and "as" not in stripped:
        return "open('file.txt') as f:"
    
    # Check for incomplete try/except
    if stripped.endswith("try:"):
        return "\n    pass\nexcept Exception as e:\n    pass"
    
    # Check for incomplete if/elif
    if stripped.endswith("if ") or stripped.endswith("elif "):
        return "condition:\n    pass"
    
    # Check for incomplete for loop
    if stripped.endswith("for "):
        return "item in iterable:\n    pass"
    
    # Check for incomplete while loop
    if stripped.endswith("while "):
        return "condition:\n    pass"
    
    # Check for incomplete class definition
    if stripped.endswith("class "):
        return "ClassName:\n    def __init__(self):\n        pass"
    
    # Check for incomplete function definition
    if stripped.endswith("def ") or stripped.endswith("async def "):
        return "function_name():\n    pass"
    
    # Check for incomplete import
    if stripped.endswith("import "):
        return COMMON_IMPORTS[0]
    
    if stripped.endswith("from "):
        return "module import "
    
    # Check for decorator
    if stripped.endswith("@"):
        return "decorator\n"
    
    return None

def get_smart_suggestion(code: str, cursor: int) -> str:
    """Generate a smart suggestion based on code context."""
    before_cursor = code[:cursor]
    current_line, before_lines, line_num = get_line_context(code, cursor)
    indentation = get_indentation(current_line)
    
    # Try to detect context
    suggestion = detect_context(before_cursor, current_line)
    
    if suggestion:
        # Apply indentation if suggestion spans multiple lines
        if '\n' in suggestion:
            lines = suggestion.split('\n')
            indented_lines = [lines[0]] + [indentation + line for line in lines[1:]]
            return '\n'.join(indented_lines)
        return suggestion
    
    # Fallback: analyze the last few words
    words = current_line.strip().split()
    if not words:
        # Empty line - suggest common patterns
        if line_num == 0:
            return "def main():\n    pass\n\nif __name__ == '__main__':\n    main()"
        return "# Add your code here"
    
    last_word = words[-1].lower()
    
    # Keyword-based suggestions
    keyword_suggestions = {
        "if": " condition:\n    pass",
        "elif": " condition:\n    pass",
        "else": ":",
        "for": " item in iterable:\n    pass",
        "while": " condition:\n    pass",
        "def": " function_name():\n    pass",
        "class": " ClassName:\n    def __init__(self):\n        pass",
        "try": ":",
        "except": " Exception as e:\n    pass",
        "finally": ":",
        "with": " open('file.txt') as f:\n    pass",
        "import": " os",
        "from": " module import ",
        "return": " value",
        "yield": " value",
        "raise": " Exception('message')",
        "assert": " condition, 'message'",
    }
    
    if last_word in keyword_suggestions:
        suggestion = keyword_suggestions[last_word]
        if '\n' in suggestion:
            lines = suggestion.split('\n')
            indented_lines = [lines[0]] + [indentation + line for line in lines[1:]]
            return '\n'.join(indented_lines)
        return suggestion
    
    # Default: no suggestion
    return ""

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(req: AutocompleteRequest):
    """Enhanced autocomplete with context-aware suggestions."""
    code = req.code or ""
    cursor = req.cursorPosition or len(code)
    
    suggestion = get_smart_suggestion(code, cursor)
    
    # If no suggestion found, provide a helpful default
    if suggestion and suggestion.strip() != "":
        return {"suggestion": suggestion}
    
    # Otherwise, return empty string (no suggestion)
    return {"suggestion": ""}
