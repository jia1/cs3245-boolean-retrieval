#!/usr/bin/python
import nltk
import sys
import getopt

import pickle
import string

from collections import Counter
from math import log10
from time import time

from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

from constants import lengths_file_name, peek, print_time
from skip_list import SkipList
from parse_tree import ParseTree

start_time = time()

dictionary = {}
offsets = {}

with open('stopwords.txt') as f:
    stopwords = set(map(lambda ln: ln.strip(), f.readlines()))

# MAIN function for search.py
def do_searching(dictionary_file_name, postings_file_name, queries_file_name, output_file_name):
    with open(dictionary_file_name) as d, open(postings_file_name, 'rb') as p, \
        open(queries_file_name) as q, open(output_file_name, 'w') as o, \
        open(lengths_file_name, 'rb') as l:
        # Build the offsets dictionary for seeking later
        for line in d:
            stem, offset = line.rstrip().split(',')
            offsets[stem] = int(offset)
        # Load the following data from the lengths file:
        # 1. Total number of documents in the collection
        # 2. Length of each document (key is the doc_id)
        N = pickle.load(l)
        lengths_by_document = pickle.load(l)
        # Process each query one-by-one but with the same resources
        # I.e. Duplicate stems are loaded only once
        for line in q:
            stems, query = get_parsed_query(line) # string to list in postfix form

            # Boolean retrieval (AND only)
            parse_tree = build_tree(query, p) # list to parse tree
            while root_node is not None and root_node.is_operator():
                operand_nodes = parse_tree.get_sorted_operands(comparator=lambda node: node.get_data())
                # Recall that node.data is (number of postings, postings skip list) and as such the
                # comparator compares nodes by the number of postings (tuple comparison is done by
                # comparing the first element unless otherwise specified)
                index = 0
                while index < len(operand_nodes): # a loop to evaluate the smallest operand possible
                    operand_node = operand_nodes[index]
                    operator_node = operand_node.get_parent()
                    operator = operator_node.get_data()
                    # As specified in Assignment 4, always AND operator (binary operator)
                    operand_node_a = operator_node.get_left()
                    operand_node_b = operator_node.get_right()
                    if operand_node_a.is_operator() or operand_node_b.is_operator():
                        # The other operand is unevaluated (i.e. not a leaf, and still a subtree
                        # with an operator as root) so we should look at the next operand with the
                        # smallest number of postings
                        index += 1
                        continue
                    key_a, operand_a = operand_node_a.get_data() # key_* is the document frequency
                    key_b, operand_b = operand_node_b.get_data()
                    operation = binary_operations[operator] # i.e. AND
                    skip_list = operation(operand_a, operand_b)
                    # Mutate the subtree root (an operator) into the new evaluated operand (a leaf)
                    operator_node.set_data((skip_list.get_length(), skip_list))
                    operator_node.set_left(None)
                    operator_node.set_right(None)
                    break
            if root_node is not None: # is an operand
                final_length, final_skip_list = root_node.get_data()
                final_postings_list = map(str, final_skip_list.to_list())
                o.write(' '.join(final_postings_list))
            o.write('\n')

            # TODO: Integrate this into post-boolean retrieval for ranking
            # Vector space model
            # Similar procedure as slide 38 of w7 lecture
            query_tfs = Counter(query) # list of tokens -> {token: frequency}
            tfidf_by_document = {}
            for stem_index, stem in enumerate(stems):
                query_tfidf = get_tfidf_weight(query_tfs[stem])
                df, postings = load_stem(stem, p) # {term: (length of skip list, skip list itself)}
                node = postings.get_head() # i.e. first node of skip list
                while node is not None:
                    doc_id, doc_tf = node.get_data()
                    tfidf_by_document[doc_id] = get_tfidf_weight(doc_tf, df, N) * query_tfidf
                    node = node.get_next()
            most_relevant_docs = sorted(tfidf_by_document.items(),
                key=lambda id_tfidf_tuple: id_tfidf_tuple[1], reverse=True)
            o.write(' '.join(most_relevant_docs))
            o.write('\n')

def get_tfidf_weight(tf, df=0, N=0):
    tf_weight = 0
    idf_weight = 1
    if tf:
        tf_weight = 1 + log10(tf)
    if df:
        idf_weight = log10(N / df)
    return tf_weight * idf_weight

# Accepts line and returns (set of stems, query in stemmed, postfix list form)
def get_parsed_query(line):
    stemmed_tokens = tokenize_by_parentheses(get_stemmed_tokens(line), is_string=False)
    stemmed_postfix_tokens = shunting_yard(stemmed_tokens)
    stems = set(filter(
        lambda token: True # token not any of ['and', '(', ')']
        postfix_query))
    return (stems, stemmed_postfix_tokens)

'''
Accepts a line and returns (set of stems, preprocessed line):
    0. Trim and case-fold
    1. Tokenize by space
    2. Strip punctuation from tokens
    3. Filter out non-alphabetical tokens
        (stopwords are kept because AND, NOT, OR are stopwords)
    4. Stem the remaining tokens
'''
def get_stemmed_tokens(line):
    return list(map(
        lambda token: stemmer.stem(token),
        filter(
            lambda token: token not in string.punctuation and token.isalpha(),
            line.rstrip().lower().split(' ')
            )
        )
    )

# Accepts a string and returns a list of tokens where parentheses are tokenized into separate tokens
def tokenize_by_parentheses(expression, is_string=True):
    final_tokens = []
    query = is_string ? expression.split(' ') : expression
    for token in query:
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

# Accepts a list of tokens and returns a list of tokens in postfix form
def shunting_yard(tokens):
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

# Accepts a stem, a postings file handle, and
# Returns the loaded postings skip list while storing it in memory
def load_stem(stem, postings_file_object):
    global dictionary
    if stem in dictionary:
        return dictionary[stem]
    postings = SkipList()
    if stem in offsets:
        postings_file_object.seek(offsets[stem])
        postings.build_from(pickle.load(postings_file_object))
    dictionary[stem] = (postings.get_length(), postings)
    return dictionary[stem]

def usage():
    print('Usage: ' + sys.argv[0] + ' -d dictionary-file -p postings-file -q query-file -o output-file-of-results')

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

stop_time = time()

print_time(start_time, stop_time)
