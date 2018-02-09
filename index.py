#!/usr/bin/python
import re
import nltk
import sys
import getopt

def do_indexing(documents_directory, dictionary_file, postings_file):
    pass

def usage():
    print('Usage: ' + sys.argv[0] + ' -i directory-of-documents -d dictionary-file -p postings-file')

input_directory_d = output_file_d = output_file_p = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'b:t:o:')
except (getopt.GetoptError, err):
    usage()
    sys.exit(2)
for o, a in opts:
    if o == '-i':
        input_directory_d = a
    elif o == '-d':
        output_file_d = a
    elif o == '-p':
        output_file_p = a
    else:
        assert False, 'Unhandled option'
if input_directory_d == None or output_file_d == None or output_file_p == None:
    usage()
    sys.exit(2)

do_indexing(input_directory_d, output_file_d, output_file_p)
