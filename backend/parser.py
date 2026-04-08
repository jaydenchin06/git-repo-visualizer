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


def get_top_level_items(code: str) -> Dict[str, List[str]]:
    """
    Parses Python code and returns the names of top-level functions and classes.
    
    Args:
        code: A string containing Python code
        
    Returns:
        A dictionary with two keys:
            - "functions": list of function names
            - "classes": list of class names
        
    Raises:
        SyntaxError: If the code has invalid Python syntax
    """
    # Parse the code string into an Abstract Syntax Tree (AST)
    tree = ast.parse(code)
    
    # Create empty lists to store function and class names
    function_names = []
    class_names = []
    
    # Loop through each item in the tree's body (top-level statements)
    for node in tree.body:
        # Check if this node is a function definition
        if isinstance(node, ast.FunctionDef):
            # Add the function's name to our function list
            function_names.append(node.name)
        # Check if this node is a class definition
        elif isinstance(node, ast.ClassDef):
            # Add the class's name to our class list
            class_names.append(node.name)
    
    # Return a dictionary with both lists
    return {
        "functions": function_names,
        "classes": class_names
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
