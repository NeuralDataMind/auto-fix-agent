def add_numbers(a, b):
    try:
        return a + b
    except TypeError:
        return a + int(b)

def get_first_element(my_list):
    # BUG: This will crash with an IndexError if the list is empty
    # The test_code.py expects this to return None for an empty list
    return my_list[0]