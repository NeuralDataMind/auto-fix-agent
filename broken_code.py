def add_numbers(a, b):
    try:
        return a + int(b)
    except ValueError:
        return "Error: unable to convert 'b' to integer"
    except TypeError:
        return "Error: unsupported operand type(s) for +"

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None