#!/usr/bin/python
import re
import nltk
import sys
import getopt
import os
import string
import bisect

from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
stemmer = PorterStemmer()

with open('stopwords.txt') as f:
    stopwords = set(map(lambda ln: ln.strip(), f.readlines()))

def do_indexing(documents_directory, dictionary_file, postings_file):
    dictionary = set()
    postings = {}
    seen = {}
    for root, directories, files in os.walk(documents_directory):
        for posting in files:
            with open(os.path.join(root, posting)) as f:
                text = get_preprocessed(f.read())
                dictionary.update(text)
                for word in text:
                    posting = int(posting)
                    if word not in postings:
                        postings[word] = [posting]
                        seen[word] = set((posting,))
                    else:
                        if posting not in seen[word]:
                            bisect.insort(postings[word], posting)
                            seen[word].add(posting)
    print(postings)

'''
Preprocess a text string in the following order:
    1. Sentence tokenize via sent_tokenize
    2. Word tokenize via word_tokenize and remove duplicates via set()
    3. Do case folding on each token
    4. Filter out punctuations, non-alphabetical words, and stopwords from the tokens
    5. Stem the remaining words
    6. Return a flattened set of stemmed words
'''
def get_preprocessed(text):
    sentences = map(
        lambda sentence: list(map(
            lambda nonstopword: stemmer.stem(nonstopword),
            filter(
                lambda word: word not in string.punctuation and word.isalpha() and word not in stopwords,
                map(
                    lambda token: token.lower(),
                    set(word_tokenize(sentence))
                )))),
        sent_tokenize(text))
    return set((word for words in sentences for word in words))

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
