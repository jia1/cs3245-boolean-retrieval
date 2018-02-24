universal_stem = '*'

unary_operators = ['not']
binary_operators = ['or', 'and']
operators = binary_operators + unary_operators
precedences = {operator: precedence for (precedence, operator) in enumerate(operators)}

identity = lambda x: x

# Accepts an operator string (e.g. 'not', 'or', 'and') and
# Returns True only if the operator is a binary operator (i.e. 'or', 'and')
def is_binary_operator(operator):
    return operator in binary_operators

# Accepts a stack (list type)
# And returns the last element (also last-in)
def peek(stack, error='Peek from empty stack'):
    if not stack:
        sys.exit(error)
    return stack[-1]

def print_time(start_time, stop_time):
    print('Time taken: {0:.5f} seconds'.format(stop_time - start_time))
