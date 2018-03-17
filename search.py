#!/usr/bin/python
import nltk
import sys
import getopt

import pickle
import string

from collections import Counter
from heapq import heapify, heappop
from math import log10
from time import time

from nltk.stem import PorterStemmer
stemmer = PorterStemmer()

from constants import lengths_file_name, top_n, print_time
from skip_list import SkipList

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
        N = pickle.load(l)
        lengths_by_document = pickle.load(l)
        # Process each query one-by-one but with the same resources
        # I.e. Duplicate stems are loaded only once
        for line in q:
            stems, stemmed_query = get_preprocessed_query(line)
            query_tfs = Counter(stemmed_query)
            tfidf_by_document = {}
            for stem_index, stem in enumerate(stems):
                query_tfidf = get_tfidf_weight(query_tfs[stem])
                df, postings = load_stem(stem, p)
                node = postings.get_head()
                while node is not None:
                    doc_id, doc_tf = node.get_data()
                    if doc_id not in tfidf_by_document:
                        tfidf_by_document[doc_id] = 0
                    else:
                        tfidf_by_document[doc_id] -= get_tfidf_weight(doc_tf, df, N) * query_tfidf
                    node = node.get_next()
            docs_to_pop = min(len(tfidf_by_document), top_n)
            most_relevant_docs = [-1 for i in range(docs_to_pop)]
            relevant_docs = [(doc_tfidfs / lengths_by_document[doc_id], doc_id) \
                for doc_id, doc_tfidfs in tfidf_by_document.items()]
            heapify(relevant_docs)
            for i in range(docs_to_pop):
                most_relevant_docs[i] = str(heappop(relevant_docs)[1])
            o.write(' '.join(most_relevant_docs))
            o.write('\n')

def get_tfidf_weight(tf, df=0, N=0):
    tf_weight = 0
    if tf:
        tf_weight = 1 + log10(tf)
    if df:
        idf_weight = log10(N / df)
    else:
        idf_weight = 1
    return tf_weight * idf_weight

# Accepts a line and returns (set of stems, preprocessed line):
# 1. Tokenize
# 2. Strip punctuation from tokens
# 3. Filter out non-alphabetical or stopword tokens
# 4. Stem the remaining tokens
def get_preprocessed_query(line):
    query_tokens = map(
        lambda token: token.strip(string.punctuation),
        line.rstrip().lower().split(' '))
    stemmed_query = list(map(
        lambda token: stemmer.stem(token),
        filter(
            lambda token: token.isalpha() and token not in stopwords,
            query_tokens)))
    return (set(stemmed_query), stemmed_query)

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

stop_time = time()

print_time(start_time, stop_time)
