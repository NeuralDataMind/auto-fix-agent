def add_numbers(a, b):
    try:
        return a + int(b)
    except ValueError:
        try:
            return float(a) + float(b)
        except ValueError:
            try:
                return complex(a) + complex(b)
            except ValueError:
                raise TypeError("Unsupported operand type(s) for +")

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None