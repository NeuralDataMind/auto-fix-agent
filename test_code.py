import pytest
from broken_code import add_numbers, get_first_element

def test_add_string_number():
    # This test passes an integer and a string. 
    # Standard Python will crash with TypeError: unsupported operand type(s) for +: 'int' and 'str'
    assert add_numbers(10, "5") == 15

def test_index_error():
    data = []
    assert get_first_element(data) is None