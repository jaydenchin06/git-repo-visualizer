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
    test_file_path = "test_sample.py"
    
    try:
        content = read_file(test_file_path)
        print("File contents:")
        print("-" * 50)
        print(content)
        print("-" * 50)
        print(f"\nSuccessfully read {len(content)} characters from {test_file_path}")
    except Exception as e:
        print(f"Error: {e}")
