#!/usr/bin/python
import nltk
import sys
import getopt

import pickle

from skip_list import SkipList

dictionary = {}
offsets = {}

operators = ['or', 'and', 'not']
precedences = {operator: precedence for (precedence, operator) in enumerate(operators)}

def load_next(dictionary_file_object, postings_file_object):
    global dictionary
    stem = dictionary_file_object.readline().strip()
    postings = SkipList()
    try:
        postings = pickle.load(postings_file_object)
    except EOFError:
        pass
    dictionary[stem] = (postings.get_length(), postings)

def load_stem(stem, postings_file_object):
    postings_file_object.seek(offsets[stem])
    return pickle.load(postings_file_object)

def tokenize(expression):
    final_tokens = []
    for token in expression.split(' '):
        inner_tokens = []
        if token[0] == '(':
            if token[-1] == ')':
                inner_tokens = ['(', token[1:-1], ')']
            else:
                inner_tokens = ['(', token[1:]]
        elif token[-1] == ')':
            inner_tokens = [token[:-1], ')']
        else:
            inner_tokens = [token]
        final_tokens.extend(inner_tokens)
    return final_tokens

def merge(skip_list_a, skip_list_b):
    merged_skip_list_data = []
    node_a = skip_list_a.get_head()
    node_b = skip_list_b.get_head()
    while node_a is not None and node_b is not None:
        data_a = node_a.get_data()
        data_b = node_b.get_data()
        if data_a == data_b:
            merged_skip_list_data.append(data_a)
            node_a = node_a.get_next()
            node_b = node_b.get_next()
        else:
            if data_a < data_b:
                skip_node_a = node_a.get_skip()
                if skip_node_a is not None and skip_node_a.get_data() <= data_b:
                    node_a = skip_node_a
                else:
                    node_a = node_a.get_next()
            else: # data_b < data_a
                skip_node_b = node_b.get_skip()
                if skip_node_b is not None and skip_node_b.get_data() <= data_a:
                    node_b = skip_node_b
                else:
                    node_b = node_b.get_next()
    merged_skip_list = SkipList()
    merged_skip_list.build_from(merged_skip_list_data)
    print(merged_skip_list_data)
    return merged_skip_list

def union(skip_list_a, skip_list_b):
    pass

def negate(skip_list):
    pass

def peek(stack, error='Peek from empty stack'):
    if not stack:
        sys.exit(error)
    return stack[-1]

def shunting_yard(expression):
    tokens = tokenize(expression)
    output_queue = []
    operator_stack = []
    for token in tokens:
        if token == '(':
            operator_stack.append('(')
        elif token == ')':
            last_operator = peek(operator_stack, error='Mismatched parentheses in expression')
            while last_operator != '(':
                output_queue.append(operator_stack.pop())
                last_operator = peek(operator_stack, error='Mismatched parentheses in expression')
            operator_stack.pop()
        elif token in operators:
            while operator_stack:
                last_operator = peek(operator_stack)
                if (last_operator != '('
                    and precedences[last_operator] >= precedences[token]):
                    output_queue.append(operator_stack.pop())
                else:
                    break
            operator_stack.append(token)
        else:
            output_queue.append(token)
    while operator_stack:
        last_operator = peek(operator_stack)
        if last_operator == '(':
            sys.exit('Mismatched parentheses in expression')
        output_queue.append(operator_stack.pop())
    return output_queue

def parse_query(query_string):
    return shunting_yard(query_string)

def do_searching(dictionary_file_name, postings_file_name, queries_file_name, output_file_name):
    with open(dictionary_file_name) as d, open(postings_file_name, 'rb') as p, \
        open(queries_file_name) as q, open(output_file_name, 'w') as o:
        for line in d:
            stem, offset = line.rstrip().split(',')
            offsets[stem] = int(offset)
        for line in q:
            query = line.rstrip().lower()
            postfix_query = parse_query(query)
            print(postfix_query)
        merge(load_stem('cocoa', p), load_stem('trade', p))
        # Resolve queries here
        '''
        if dictionary[stem] is None:
            load_stem(stem, p)
        '''

def usage():
    print('Usage: ' + sys.argv[0] + ' -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results')

input_file_d = input_file_p = input_file_q = output_file_o = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except (getopt.GetoptError, err) as e:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-d':
        input_file_d = a
    elif o == '-p':
        input_file_p = a
    elif o == '-q':
        input_file_q = a
    elif o == '-o':
        output_file_o = a
    else:
        assert False, 'Unhandled option'
if input_file_d == None or input_file_p == None or input_file_q == None or output_file_o == None:
    usage()
    sys.exit(2)

do_searching(input_file_d, input_file_p, input_file_q, output_file_o)
