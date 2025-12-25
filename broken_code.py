def add_numbers(a, b):
    try:
        return a + int(b)
    except ValueError:
<<<<<<< HEAD
        try:
            return float(a) + float(b)
        except ValueError:
            try:
                return complex(a) + complex(b)
            except ValueError:
                raise TypeError("Unsupported operand type(s) for +")
=======
        return "Error: unable to convert 'b' to integer"
    except TypeError:
        return "Error: unsupported operand type(s) for +"
>>>>>>> ee2e8c19f1b53176a1fe8fddae528faf697d2548

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None