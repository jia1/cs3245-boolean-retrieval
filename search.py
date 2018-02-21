#!/usr/bin/python
import nltk
import sys
import getopt

import pickle

from skip_list import SkipList

dictionary = {}
offsets = {}

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

def parse_query(query_string):
    pass

def do_searching(dictionary_file_name, postings_file_name, queries_file_name, output_file_name):
    with open(dictionary_file_name) as d, open(postings_file_name, 'rb') as p, \
        open(queries_file_name) as q, open(output_file_name, 'w') as o:
        for line in d:
            stem, offset = line.rstrip().split(',')
            offsets[stem] = int(offset)
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
