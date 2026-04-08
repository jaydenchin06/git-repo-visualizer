from parser import get_top_level_functions, get_top_level_items, read_file


def test_get_top_level_functions():
    """Test the get_top_level_functions function"""
    
    # Test 1: Test with a simple code string
    print("=" * 60)
    print("TEST 1: Testing get_top_level_functions() with sample code")
    print("=" * 60)
    
    sample_code = """
def hello():
    print("Hello!")

def add(a, b):
    return a + b

class MyClass:
    def method(self):
        pass

def goodbye():
    print("Goodbye!")
"""
    
    print("Sample code:")
    print(sample_code)
    
    functions = get_top_level_functions(sample_code)
    print(f"\nFound {len(functions)} top-level functions:")
    for func_name in functions:
        print(f"  - {func_name}")
    
    # Verify the results
    expected = ["hello", "add", "goodbye"]
    assert functions == expected, f"Expected {expected}, but got {functions}"
    print("✓ Test 1 passed!")
    
    # Test 2: Test with a real file
    print("\n" + "=" * 60)
    print("TEST 2: Testing with test_sample.py file")
    print("=" * 60)
    
    test_file_path = "test_sample.py"
    
    try:
        content = read_file(test_file_path)
        print(f"\nRead {len(content)} characters from {test_file_path}")
        
        functions = get_top_level_functions(content)
        print(f"\nFound {len(functions)} top-level functions in {test_file_path}:")
        for func_name in functions:
            print(f"  - {func_name}")
        
        # Verify the results
        expected = ["calculate_sum", "calculate_difference", "helper_function"]
        assert functions == expected, f"Expected {expected}, but got {functions}"
        print("✓ Test 2 passed!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


def test_get_top_level_items():
    """Test the get_top_level_items function (functions AND classes)"""
    
    print("\n" + "=" * 60)
    print("TEST 3: Testing get_top_level_items() with sample code")
    print("=" * 60)
    
    sample_code = """
import os

def hello():
    print("Hello!")

class Person:
    def __init__(self, name):
        self.name = name

def add(a, b):
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y

def goodbye():
    print("Goodbye!")
"""
    
    print("Sample code:")
    print(sample_code)
    
    result = get_top_level_items(sample_code)
    print(f"\nFound {len(result['functions'])} top-level functions:")
    for func_name in result['functions']:
        print(f"  - {func_name}")
    
    print(f"\nFound {len(result['classes'])} top-level classes:")
    for class_name in result['classes']:
        print(f"  - {class_name}")
    
    # Verify the results
    expected_functions = ["hello", "add", "goodbye"]
    expected_classes = ["Person", "Calculator"]
    
    assert result['functions'] == expected_functions, \
        f"Expected functions {expected_functions}, but got {result['functions']}"
    assert result['classes'] == expected_classes, \
        f"Expected classes {expected_classes}, but got {result['classes']}"
    
    print("✓ Test 3 passed!")
    
    # Test 4: Test with test_sample.py file
    print("\n" + "=" * 60)
    print("TEST 4: Testing get_top_level_items() with test_sample.py")
    print("=" * 60)
    
    test_file_path = "test_sample.py"
    
    try:
        content = read_file(test_file_path)
        print(f"\nRead {len(content)} characters from {test_file_path}")
        
        result = get_top_level_items(content)
        print(f"\nFound {len(result['functions'])} top-level functions:")
        for func_name in result['functions']:
            print(f"  - {func_name}")
        
        print(f"\nFound {len(result['classes'])} top-level classes:")
        for class_name in result['classes']:
            print(f"  - {class_name}")
        
        # Verify the results
        expected_functions = ["calculate_sum", "calculate_difference", "helper_function"]
        expected_classes = ["Calculator", "DataProcessor"]
        
        assert result['functions'] == expected_functions, \
            f"Expected functions {expected_functions}, but got {result['functions']}"
        assert result['classes'] == expected_classes, \
            f"Expected classes {expected_classes}, but got {result['classes']}"
        
        print("✓ Test 4 passed!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    test_get_top_level_functions()
    test_get_top_level_items()
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
