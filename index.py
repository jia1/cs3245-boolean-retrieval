#!/usr/bin/python
import re
import nltk
import sys
import getopt
import os

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
stemmer = PorterStemmer()

with open('stopwords.txt') as f:
    stopwords = set(map(lambda ln: ln.strip(), f.readlines()))

def do_indexing(documents_directory, dictionary_file, postings_file):
    for root, directories, files in os.walk(documents_directory):
        for file_name in files:
            with open(os.path.join(root, file_name)) as f:
                text = f.read()
                print(get_preprocessed(text))

'''
Preprocess a text string in the following order:
    1. Sentence tokenize via sent_tokenize
    2. Word tokenize via word_tokenize
    3. Filter out stopwords from tokenized words
    4. Stem the remaining non-stopwords
    5. Return the list of sentences, where each sentence is a list of words
'''
def get_preprocessed(text):
    return list(map(
        lambda sentence: list(map(
            lambda nonstopword: stemmer.stem(nonstopword),
            filter(
                lambda word: word not in stopwords,
                word_tokenize(sentence)))),
        sent_tokenize(text)))

def usage():
    print('Usage: ' + sys.argv[0] + ' -i directory-of-documents -d dictionary-file -p postings-file')

input_directory_d = output_file_d = output_file_p = None
try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except (getopt.GetoptError, err) as e:
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
