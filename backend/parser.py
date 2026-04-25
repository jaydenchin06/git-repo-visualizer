import ast
from typing import List, Dict


def get_top_level_functions(code: str) -> List[str]:
    """
    Parses Python code and returns the names of all top-level functions.
    
    Args:
        code: A string containing Python code
        
    Returns:
        A list of function names (strings) that are defined at the top level
        
    Raises:
        SyntaxError: If the code has invalid Python syntax
    """
    # Parse the code string into an Abstract Syntax Tree (AST)
    tree = ast.parse(code)
    
    # Create an empty list to store function names
    function_names = []
    
    # Loop through each item in the tree's body (top-level statements)
    for node in tree.body:
        # Check if this node is a function definition
        if isinstance(node, ast.FunctionDef):
            # Add the function's name to our list
            function_names.append(node.name)
    
    # Return the list of function names
    return function_names


def get_detailed_structure(code: str) -> Dict:
    """
    Parses Python code and returns detailed information about functions and classes,
    including their line numbers.
    
    Args:
        code: A string containing Python code
        
    Returns:
        A dictionary with two keys:
            - "functions": list of dictionaries with function details
            - "classes": list of dictionaries with class details
        Each item contains: name, line_start, line_end
        
    Raises:
        SyntaxError: If the code has invalid Python syntax
    """
    # Parse the code string into an Abstract Syntax Tree (AST)
    tree = ast.parse(code)
    
    # Create empty lists to store detailed function and class information
    functions_list = []
    classes_list = []
    
    # Loop through each item in the tree's body (top-level statements)
    for node in tree.body:
        # Check if this node is a function definition
        if isinstance(node, ast.FunctionDef):
            # Create a dictionary with function details
            function_info = {
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno
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
                    # Create a dictionary with method details
                    method_info = {
                        "name": item.name,
                        "line_start": item.lineno,
                        "line_end": item.end_lineno
                    }
                    # Add the method to our methods list
                    methods.append(method_info)
            
            # Create a dictionary with class details, including methods
            class_info = {
                "name": node.name,
                "line_start": node.lineno,
                "line_end": node.end_lineno,
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


if __name__ == "__main__":
    # Quick demo of the functions
    sample_code = """
def example_function():
    pass
"""
    
    print("Demo: Extracting top-level functions")
    print(f"Functions found: {get_top_level_functions(sample_code)}")
    print("\nFor full tests, run: python test_parser.py")
