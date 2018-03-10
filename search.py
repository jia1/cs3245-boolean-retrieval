#!/usr/bin/python
import nltk
import sys
import getopt

import math
import numpy as np
import pickle
import string

from collections import Counter
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
            query_counter = Counter(stemmed_query)
            query_tfidfs = []
            for stem in stems:
                tf = query_counter[stem]
                query_tfidfs.append(get_tfidf_weight(tf))
            query_tfidfs = np.array(query_tfidfs)
            query_tfidfs = np.divide(query_tfidfs, np.linalg.norm(query_tfidfs))
            tfidf_by_document = {}
            number_of_terms = len(stems)
            for stem_index, stem in enumerate(stems):
                df, postings = load_stem(stem, p) 
                node = postings.get_head()
                while node is not None:
                    doc_id, tf = node.get_data()
                    if doc_id not in tfidf_by_document:
                        tfidf_by_document[doc_id] = np.array([0 for i in stems])
                    else:
                        tfidf_by_document[doc_id][stem_index] = get_tfidf_weight(tf, df, N)
            similarity_by_document = {doc_id: get_cosine_similarity(doc_tfidfs,
                query_tfidfs, b_is_unit=True) for doc_id, doc_tfidfs in tfidf_by_document.items()}
            relevant_doc_tuples = sorted(similarity_by_document.items(), key=lambda t: t[1], reverse=True)
            o.write(' '.join(map(lambda t: str(t[0]), relevant_doc_tuples[:top_n])))
            o.write('\n')

def get_tfidf_weight(tf, df=1, N=10):
    tf_weight = 0
    if tf:
        tf_weight = 1 + math.log10(tf)
    idf_weight = math.log10(N / df)
    return tf_weight * idf_weight

def get_cosine_similarity(np_array_a, np_array_b, a_is_unit=False, b_is_unit=False):
    cos_value = np.dot(np_array_a, np_array_b)
    if not a_is_unit:
        cos_value /= np.linalg.norm(np_array_a)
    if not b_is_unit:
        cos_value /= np.linalg.norm(np_array_b)
    return math.acos(cos_value)

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
