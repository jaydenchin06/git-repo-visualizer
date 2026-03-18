def calculate_sum(a, b):
    return a + b


def calculate_difference(a, b):
    return a - b


class Calculator:
    def __init__(self):
        self.result = 0
    
    def multiply(self, x, y):
        return x * y
    
    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y


class DataProcessor:
    def process_data(self, data):
        return [item.upper() for item in data]
    
    def filter_data(self, data, condition):
        return [item for item in data if condition(item)]


def helper_function():
    pass
