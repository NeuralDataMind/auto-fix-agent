def add_numbers(a, b):
    try:
        return a + b
    except TypeError:
        return a + int(b)

def get_first_element(my_list):
    if not my_list:
        return None
    return my_list[0]