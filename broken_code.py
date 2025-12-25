def add_numbers(a, b):
    try:
        return a + b
    except TypeError:
        try:
            return a + float(b)
        except ValueError:
            return None

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None