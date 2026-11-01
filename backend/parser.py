import ast
import os
from typing import List, Dict, Optional



def get_detailed_structure(code: str) -> Dict:
    """
    Parses Python code and returns detailed information about functions and classes,
    including their line numbers and source code.
    
    Args:
        code: A string containing Python code
        
    Returns:
        A dictionary with two keys:
            - "functions": list of dictionaries with function details
            - "classes": list of dictionaries with class details
        Each item contains: name, line_start, line_end, code
        
    Raises:
        SyntaxError: If the code has invalid Python syntax
    """
    # Parse the code string into an Abstract Syntax Tree (AST)
    tree = ast.parse(code)
    
    # Split the code into lines so we can extract specific line ranges
    lines = code.split('\n')
    
    # Create empty lists to store detailed function and class information
    functions_list = []
    classes_list = []
    
    # Loop through each item in the tree's body (top-level statements)
    for node in tree.body:
        # Check if this node is a function definition
        if isinstance(node, ast.FunctionDef):
            # Extract the source code for this function
            # Line numbers start at 1, but list indices start at 0
            function_code = '\n'.join(lines[node.lineno - 1 : node.end_lineno])
            
            # Create a dictionary with function details
            function_info = {
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "code": function_code
            }
            # Add to our functions list
            functions_list.append(function_info)
            
        # Check if this node is a class definition
        elif isinstance(node, ast.ClassDef):
            # Create an empty list to store methods inside this class
            methods = []
            
            # Loop through items inside the class's body
            for item in node.body:
                # Check if this item is a method (function inside a class)
                if isinstance(item, ast.FunctionDef):
                    # Extract the source code for this method
                    method_code = '\n'.join(lines[item.lineno - 1 : item.end_lineno])
                    
                    # Create a dictionary with method details
                    method_info = {
                        "name": item.name,
                        "line_start": item.lineno,
                        "line_end": item.end_lineno,
                        "code": method_code
                    }
                    # Add the method to our methods list
                    methods.append(method_info)
            
            # Extract the source code for this class
            class_code = '\n'.join(lines[node.lineno - 1 : node.end_lineno])
            
            # Create a dictionary with class details, including methods
            class_info = {
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
                "code": class_code,
                "methods": methods
            }
            # Add to our classes list
            classes_list.append(class_info)
    
    # Return a dictionary with both lists
    return {
        "functions": functions_list,
        "classes": classes_list
    }


def read_file(file_path: str) -> str:
    """
    Reads the contents of a file and returns it as a string.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        The contents of the file as a string
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")


def parse_python(code: str) -> List[Dict]:
    """
    Parses Python code into a list of symbols (classes, functions, methods).
    Unlike get_detailed_structure, this also finds nested symbols, such as
    functions defined inside functions or classes defined inside classes.

    Args:
        code: A string containing Python code

    Returns:
        A list of symbol dictionaries. Each one has: name, type ("class",
        "function" or "method"), line_start, line_end and children (a list of
        symbols defined inside it, in the same shape)

    Raises:
        SyntaxError: If the code has invalid Python syntax
    """
    tree = ast.parse(code)
    return _python_symbols(tree.body, inside_class=False)


def _python_symbols(body: list, inside_class: bool) -> List[Dict]:
    """Turns the statements in an AST body into symbols, recursing into each one."""
    symbols = []
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # A function directly inside a class is a method
            symbol_type = "method" if inside_class else "function"
        elif isinstance(node, ast.ClassDef):
            symbol_type = "class"
        else:
            continue

        # Start at the first decorator (like @property) so it shows up with the code
        line_start = min([node.lineno] + [d.lineno for d in node.decorator_list])

        symbols.append({
            "name": node.name,
            "type": symbol_type,
            "line_start": line_start,
            "line_end": node.end_lineno,
            "children": _python_symbols(node.body, inside_class=(symbol_type == "class")),
        })
    return symbols


# Maps a file extension to the language name and the function that parses it.
# To support a new language, write a function that takes the code as a string and
# returns a list of symbols in the same shape as parse_python, then add it here.
PARSERS = {
    ".py": ("python", parse_python),
}

# Languages we can recognise (for display and for the AI) but can't parse yet
LANGUAGE_NAMES = {
    ".js": "javascript", ".jsx": "javascript", ".ts": "typescript", ".tsx": "typescript",
    ".java": "java", ".c": "c", ".h": "c", ".cpp": "cpp", ".cs": "csharp",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift",
    ".kt": "kotlin", ".html": "html", ".css": "css", ".json": "json",
    ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", ".sh": "bash", ".sql": "sql",
}


def get_language(filename: str) -> Optional[str]:
    """Returns the language name for a filename based on its extension, or None."""
    extension = os.path.splitext(filename)[1].lower()
    if extension in PARSERS:
        return PARSERS[extension][0]
    return LANGUAGE_NAMES.get(extension)


def parse_code(code: str, filename: str) -> Dict:
    """
    Parses a file with whichever parser matches its extension.

    Args:
        code: The file contents
        filename: The file name, used to pick the parser (e.g. "main.py")

    Returns:
        A dictionary with: language (or None), symbols (empty if there is no
        parser for this language) and error (a message if parsing failed, else None)
    """
    extension = os.path.splitext(filename)[1].lower()
    if extension not in PARSERS:
        return {"language": get_language(filename), "symbols": [], "error": None}

    language, parse = PARSERS[extension]
    try:
        return {"language": language, "symbols": parse(code), "error": None}
    except SyntaxError as e:
        # Don't fail the whole repo because of one broken file
        return {"language": language, "symbols": [], "error": f"Syntax error on line {e.lineno}: {e.msg}"}


if __name__ == "__main__":
    # Quick demo of the functions
    sample_code = """
def example_function():
    pass
"""

    print("Demo: Extracting top-level functions")
    print(f"Functions found: {get_detailed_structure(sample_code)['functions']}")
    print("\nFor full tests, run: python -m pytest backend")
