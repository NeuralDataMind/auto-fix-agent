def add_numbers(a, b):
    if isinstance(a, str) and a.isdigit():
        a = int(a)
    if isinstance(b, str) and b.isdigit():
        b = int(b)
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both inputs must be numbers")
    return a + b

def get_first_element(my_list):
    if not my_list:
        return None
    return my_list[0]