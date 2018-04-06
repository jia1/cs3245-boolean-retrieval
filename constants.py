database_file_name = 'zones.db'
zones_table_name = 'zones'

lengths_file_name = 'lengths.txt'
and_operator_name = 'and'

identity = lambda x: x

def is_operator(operator_name):
    return operator_name == and_operator_name

# Accepts a stack (list type) and returns the last element (also last-in)
def peek(stack, error='Peek from empty stack'):
    if not stack:
        sys.exit(error)
    return stack[-1]

def print_time(start_time, stop_time):
    print('Time taken: {0:.5f} seconds'.format(stop_time - start_time))
