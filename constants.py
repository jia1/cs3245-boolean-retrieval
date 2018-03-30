lengths_file_name = 'lengths.txt'

identity = lambda x: x

# Accepts a stack (list type) and returns the last element (also last-in)
def peek(stack, error='Peek from empty stack'):
    if not stack:
        sys.exit(error)
    return stack[-1]

def print_time(start_time, stop_time):
    print('Time taken: {0:.5f} seconds'.format(stop_time - start_time))
