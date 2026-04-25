from parser import get_detailed_structure, read_file


def test_get_detailed_structure():
    """Test the get_detailed_structure function (functions AND classes with line numbers)"""
    
    print("=" * 60)
    print("TEST 1: Testing get_detailed_structure() with sample code")
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
    
    result = get_detailed_structure(sample_code)
    print(f"\nFound {len(result['functions'])} top-level functions:")
    for func in result['functions']:
        print(f"  - {func['name']} (lines {func['line_start']}-{func['line_end']})")
    
    print(f"\nFound {len(result['classes'])} top-level classes:")
    for cls in result['classes']:
        print(f"  - {cls['name']} (lines {cls['line_start']}-{cls['line_end']})")
    
    # Verify the results - just check names for now
    function_names = [f['name'] for f in result['functions']]
    class_names = [c['name'] for c in result['classes']]
    
    expected_functions = ["hello", "add", "goodbye"]
    expected_classes = ["Person", "Calculator"]
    
    assert function_names == expected_functions, \
        f"Expected functions {expected_functions}, but got {function_names}"
    assert class_names == expected_classes, \
        f"Expected classes {expected_classes}, but got {class_names}"
    
    print("✓ Test 3 passed!")
    
    # Test 2: Test with test_sample.py file
    print("\n" + "=" * 60)
    print("TEST 2: Testing get_detailed_structure() with test_sample.py")
    print("=" * 60)
    
    test_file_path = "test_sample.py"
    
    try:
        content = read_file(test_file_path)
        print(f"\nRead {len(content)} characters from {test_file_path}")
        
        result = get_detailed_structure(content)
        print(f"\nFound {len(result['functions'])} top-level functions:")
        for func in result['functions']:
            print(f"  - {func['name']} (lines {func['line_start']}-{func['line_end']})")
        
        print(f"\nFound {len(result['classes'])} top-level classes:")
        for cls in result['classes']:
            print(f"  - {cls['name']} (lines {cls['line_start']}-{cls['line_end']})")
        
        # Verify the results - just check names for now
        function_names = [f['name'] for f in result['functions']]
        class_names = [c['name'] for c in result['classes']]
        
        expected_functions = ["calculate_sum", "calculate_difference", "helper_function"]
        expected_classes = ["Calculator", "DataProcessor"]
        
        assert function_names == expected_functions, \
            f"Expected functions {expected_functions}, but got {function_names}"
        assert class_names == expected_classes, \
            f"Expected classes {expected_classes}, but got {class_names}"
        
        print("✓ Test 2 passed!")
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    test_get_detailed_structure()
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
