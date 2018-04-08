#!/usr/bin/python
import nltk
import sys
import getopt

import pickle
import string
import sqlite3

from collections import Counter
from math import log10
from time import time

from nltk.lemma import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from constants import lengths_file_name, print_time, database_file_name, zones_table_name
from skip_list import SkipList

conn = sqlite3.connect(database_file_name)
c = conn.cursor()

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
            lemma, offset = line.rstrip().split(',')
            offsets[lemma] = int(offset)
        # Load the following data from the lengths file:
        # 1. Total number of documents in the collection
        # 2. Length of each document (key is the doc_id)
        N = pickle.load(l)
        lengths_by_document = pickle.load(l)
        # Process each query one-by-one but with the same resources
        # I.e. Duplicate lemmas are loaded only once
        for line in q:
            # TODO: Integrate zones and query expansion
            lemmas, tokens_for_blr, tokens_for_vsm = get_parsed_query(line)
            candidate_length, candidate_skip_list = boolean_retrieve(tokens_for_blr, p)
            query_tfs = Counter(tokens_for_vsm) # list of tokens -> {token: frequency}
            tfidf_by_document_upp = {}
            tfidf_by_document_low = {}
            if candidate_length:
                for lemma_index, lemma in enumerate(lemmas):
                    query_tfidf = get_tfidf_weight(query_tfs[lemma])
                    df, postings = load_lemma(lemma, p)
                    # BEGIN procedure
                    # "merge" boolean retrieved postings with postings by term
                    # Documents which exist in both skip lists will be considered in the upper rankings
                    # while those which exist only in the term skip list are moved to the lower rankings
                    node_a = candidate_skip_list.get_head() # i.e. first node of skip list
                    node_b = postings.get_head()
                    while node_a is not None and node_b is not None:
                        data_a = node_a.get_data()
                        data_b = node_b.get_data()
                        doc_id, doc_tf = data_b
                        if data_a != data_b:
                            tfidf_by_document_low[doc_id] = get_tfidf_weight(doc_tf, df, N) * query_tfidf
                            if data_a < data_b:
                                skip_node_a = node_a.get_skip()
                                if skip_node_a is not None and skip_node_a.get_data() <= data_b:
                                    node_a = skip_node_a
                                else:
                                    node_a = node_a.get_next()
                            elif data_b < data_a:
                                skip_node_b = node_b.get_skip()
                                if skip_node_b is not None and skip_node_b.get_data() <= data_a:
                                    node_b = skip_node_b
                                else:
                                    node_b = node_b.get_next()
                        else:
                            tfidf_by_document_upp[doc_id] = get_tfidf_weight(doc_tf, df, N) * query_tfidf
                            node_a = node_a.get_next()
                            node_b = node_b.get_next()
                    # END procedure
            else:
                # Pure vector space model because boolean retrieved postings is empty
                # Similar procedure to slide 38 of w7 lecture
                for lemma_index, lemma in enumerate(lemmas):
                    query_tfidf = get_tfidf_weight(query_tfs[lemma])
                    df, postings = load_lemma(lemma, p)
                    node_b = postings.get_head()
                    while node_b is not None:
                        doc_id, doc_tf = node_b.get_data()
                        tfidf_by_document_upp[doc_id] = get_tfidf_weight(doc_tf, df, N) * query_tfidf
                        node_b = node_b.get_next()
            most_relevant_docs = sorted(tfidf_by_document_upp.items(),
                key=lambda id_tfidf_tuple: id_tfidf_tuple[1], reverse=True)
            less_relevant_docs = sorted(tfidf_by_document_low.items(),
                key=lambda id_tfidf_tuple: id_tfidf_tuple[1], reverse=True)
            most_relevant_docs.extend(less_relevant_docs)
            o.write(' '.join(most_relevant_docs))
            o.write('\n')
            break # because 1 query per file

'''
Boolean retrieval routine (AND only)
Accepts a list of tokens and returns:
    tuple(postings length, postings skip list)
where data of skip list node (i.e. node.get_data()) is:
    tuple(doc id, term frequency)
'''
def boolean_retrieve(tokens, p):
    if not tokens:
        return (0, SkipList())
    skip_lists = list(map(
        lambda token: load_lemma(token, p), # (df, postings)
        tokens
        )
    )
    merged_skip_list = reduce(
        lambda skip_list_a, skip_list_b: skip_list_a.merge(skip_list_b),
        sorted(skip_lists)) # sorted by lowest to highest df
    return (merged_skip_list.get_length(), merged_skip_list)

'''
Accepts a line and returns:
    (set of lemmas, lemmas for boolean retrieval, lemmas for vector space model)
Lemmas for boolean retrieval remains as []
    if there are no 'AND' case-sensitive substrings in the line
'''
def get_parsed_query(line):
    operands = line.rstrip().split(and_operator_name.upper()) # assumes boolean operator is only 'AND'
    tokens_for_blr = []
    tokens_for_vsm = []
    if len(operands) > 1:
        operands = map(
            lambda operand: map(
                lambda token: lemmatizer.lemmatize(token),
                filter(
                    lambda token: is_significant_token(token),
                    operand.strip(string.punctuation).lower().split(' ')
                    )
                ),
            operands)
        for tokens in operands:
            tokens_for_blr.extend(tokens)
        tokens_for_vsm = tokens_for_blr
    else: # no boolean operators found (i.e. do pure vector space model retrieval)
        tokens_for_vsm = operands
    return (set(tokens_for_vsm), tokens_for_blr, tokens_for_vsm)

def is_significant_token(token):
    return token not in string.punctuation and token.isalpha() and token not in stopwords

# Accepts a lemma, a postings file handle, and
# Returns the loaded postings skip list while storing it in memory
def load_lemma(lemma, postings_file_object):
    global dictionary
    if lemma in dictionary:
        return dictionary[lemma]
    postings = SkipList()
    if lemma in offsets:
        postings_file_object.seek(offsets[lemma])
        postings.build_from(pickle.load(postings_file_object))
    dictionary[lemma] = (postings.get_length(), postings)
    return dictionary[lemma]

def get_tfidf_weight(tf, df=0, N=0):
    tf_weight = 0
    idf_weight = 1
    if tf:
        tf_weight = 1 + log10(tf)
    if df:
        idf_weight = log10(N / df)
    return tf_weight * idf_weight

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
