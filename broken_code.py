def add_numbers(a, b):
<<<<<<< HEAD
    try:
        return a + b
    except TypeError:
        try:
            return a + int(b)
        except ValueError:
            try:
                return a + float(b)
            except ValueError:
                return "Error: Unable to add 'a' and 'b'"
=======
    # Intentional Bug: We are not handling cases where 'b' might be a string number like "5"
    return a + b 
>>>>>>> f900985 (broken_code.py)

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None