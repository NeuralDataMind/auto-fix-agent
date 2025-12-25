def add_numbers(a, b):
    # Intentional Bug: We are not handling cases where 'b' might be a string number like "5"
    return a + b 

def get_first_element(my_list):
    if len(my_list) > 0:
        return my_list[0]
    else:
        return None 