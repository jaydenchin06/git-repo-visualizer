from parser import get_top_level_functions, read_file


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


if __name__ == "__main__":
    test_get_top_level_functions()
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
