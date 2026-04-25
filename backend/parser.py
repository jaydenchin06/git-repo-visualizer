import ast
from typing import List, Dict



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


if __name__ == "__main__":
    # Quick demo of the functions
    sample_code = """
def example_function():
    pass
"""
    
    print("Demo: Extracting top-level functions")
    print(f"Functions found: {get_top_level_functions(sample_code)}")
    print("\nFor full tests, run: python test_parser.py")
