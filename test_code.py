import pytest
from broken_code import add_numbers, get_first_element

def test_add():
    assert add_numbers(2, 3) == 5

def test_index_error():
    data = [1, 2, 3]
    assert get_first_element(data) == 1