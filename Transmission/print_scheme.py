def print_function(direction, data_to_print):
    data = None

    if direction is 'OUT':
        print(data_to_print, end='')

    elif direction is 'IN':
        data = input(data_to_print)

    return data
