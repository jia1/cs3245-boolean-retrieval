#!/usr/bin/python
import nltk
import sys
import getopt

import pickle
import string
import sqlite3

from collections import Counter
from functools import reduce
from math import log10
from time import time

from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from constants import (
    lengths_file_name,
    nltk_offsets_file_name,
    nltk_texts_file_name,
    database_file_name,
    zones_table_name,
    and_operator_name,
    print_time
    )
from skip_list import SkipList
from nltk_context_index import ContextIndex

# Database for zones
'''
conn = sqlite3.connect(database_file_name)
c = conn.cursor()
'''

start_time = time()

dictionary = {}         # { lemma: postings skip list}
postings_offsets = {}   # { lemma: postings offset }
nltk_texts = {}         # { doc_id: nltk.Text }
nltk_offsets = {}       # { doc_id: nltk text offset }

# Variables made global because they are read across functions
N = 0
lengths_by_document = {}

with open('stopwords.txt') as f:
    stopwords = set(map(lambda ln: ln.strip(), f.readlines()))

# MAIN function for search.py
def do_searching(dictionary_file_name, postings_file_name, queries_file_name, output_file_name):
    global N
    global lengths_by_document
    with open(dictionary_file_name, errors='ignore') as d, \
        open(postings_file_name, 'rb') as p, \
        open(queries_file_name) as q, \
        open(output_file_name, 'w') as o, \
        open(lengths_file_name, 'rb') as l, \
        open(nltk_offsets_file_name) as i, \
        open(nltk_texts_file_name, 'rb') as t:
        # Build the offsets dictionaries for seeking later
        for line in d:
            lemma, postings_offset = line.rstrip().split(',')
            postings_offsets[lemma] = int(postings_offset)
        for line in i:
            doc_id, nltk_text_offset = line.rstrip().split(',')
            nltk_offsets[doc_id] = int(nltk_text_offset)
        # Load the following data from the lengths file:
        # 1. Total number of documents in the collection
        # 2. Length of each document (key is the doc_id)
        N = pickle.load(l)
        lengths_by_document = pickle.load(l)
        # Process each query one-by-one but with the same resources
        # I.e. Duplicate lemmas and nltk.Text are loaded only once
        for line in q:
            lemmas, tokens_for_blr, tokens_for_vsm = get_parsed_query(line)

            # Get all synonyms for each query lemma
            synonyms_by_lemma = { lemma: list(filter(
                lambda synonym: synonym != lemma and '_' not in synonym,
                set(sum(
                    map(
                        lambda synset: list(map(str.lower, synset.lemma_names())),
                        wn.synsets(lemma)),
                    [])
                )))
            for lemma in lemmas }

            # Do boolean retrieval first to separate high list (retrieved) from low list
            blr_length, blr_skip_list = boolean_retrieve(tokens_for_blr, p)
            query_tfs = Counter(tokens_for_vsm) # list of tokens -> {token: frequency}

            # Get ranked high and low lists via vector space model
            most_relevant_docs, less_relevant_docs = get_relevant_docs(
                blr_skip_list, lemmas, query_tfs,  p)

            # BEGIN procedure for query expansion
            if most_relevant_docs:
                relevant_docs = most_relevant_docs
            else:
                relevant_docs = less_relevant_docs

            # Manual thesaurus-based query expansion: Synonym lookup via WordNet
            # query_expansion = set(sum(synonyms_by_lemma.values(), []))

            # Semi-automatic thesaurus-based query expansion:
            # Synonym lookup via WordNet + co-occurrence filter on synonyms
            # query_expansion may contain terms already in the original query, hence we call .difference
            query_expansion = get_query_expansion(relevant_docs)
            tokens_for_vsm.extend(query_expansion.difference(tokens_for_vsm))
            query_tfs = Counter(tokens_for_vsm)
            # END procedure

            # Get ranked high and low lists via vector space model, and expanded query
            most_relevant_docs, less_relevant_docs = get_relevant_docs(
                blr_skip_list, lemmas, query_tfs,  p)

            most_relevant_docs.extend(less_relevant_docs)
            o.write(' '.join(most_relevant_docs))
            o.write('\n')
            break # because 1 query per file

'''
This is a procedure after boolean retrieval
    (abstracted into a function because re-run is needed for query expansion)
- If there are zero documents from boolean retrieval of query terms,
    resort to pure vector space model
- Else assign the returned documents to the high-list and
    do vector space model on them for ranking
- Low-list contains documents ranked by vector space model,
    but fail to be retrieved via boolean retrieval
    (i.e. one or more query terms not existing in the document)
'''
def get_relevant_docs(blr_skip_list, lemmas, query_tfs, p):
    tfidf_by_document_upp = {}
    tfidf_by_document_low = {}
    if blr_skip_list.get_length():
        for lemma_index, lemma in enumerate(lemmas):
            query_tfidf = get_tfidf_weight(query_tfs[lemma])
            df, postings = load_lemma(lemma, p)
            # BEGIN procedure
            # "merge" boolean retrieved postings with postings by term
            # Documents which exist in both skip lists will be considered in the upper rankings
            # while those which exist only in the term skip list are moved to the lower rankings
            node_a = blr_skip_list.get_head() # i.e. first node of skip list
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
    # Normalization
    tfidf_by_document_upp = { doc_id: tfidf / lengths_by_document[doc_id] \
        for doc_id, tfidf in tfidf_by_document_upp.items() }
    tfidf_by_document_low = { doc_id: tfidf / lengths_by_document[doc_id] \
        for doc_id, tfidf in tfidf_by_document_low.items() }
    # Sort dictionary by descending normalized tfidf, and return lists of doc_id
    most_relevant_docs = list(map(
        lambda id_tfidf_tuple: str(id_tfidf_tuple[0]),
        sorted(
            tfidf_by_document_upp.items(),
            key=lambda id_tfidf_tuple: id_tfidf_tuple[1],
            reverse=True)
        )
    )
    less_relevant_docs = map(
        lambda id_tfidf_tuple: str(id_tfidf_tuple[0]),
        sorted(
            tfidf_by_document_low.items(),
            key=lambda id_tfidf_tuple: id_tfidf_tuple[1],
            reverse=True)
        )
    return (most_relevant_docs, less_relevant_docs)

# Document this function
def get_query_expansion(relevant_docs, synonyms_by_lemma):
    query_expansion = set()
    for lemma, synonyms in synonyms_by_lemma.items():
        for doc_id in relevant_docs:
            nltk_text = load_nltk_text(doc_id, t)
            sim_words = set(get_similar(nltk_text, lemma))
            query_expansion.update(sim_words.intersection(synonyms))
    return query_expansion

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
    sorted_skip_lists = map(
        lambda df_postings_tuple: df_postings_tuple[1],
        sorted(
            list(map(
                lambda token: load_lemma(token, p),
                tokens
            )))
        )
    merged_skip_list = reduce(
        lambda skip_list_a, skip_list_b: skip_list_a.merge(skip_list_b),
        sorted_skip_lists)
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
    if operands:
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
            tokens_for_vsm = operands[0].split(' ')
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
    if lemma in postings_offsets:
        postings_file_object.seek(postings_offsets[lemma])
        postings.build_from(pickle.load(postings_file_object))
    dictionary[lemma] = (postings.get_length(), postings)
    return dictionary[lemma]

# Accepts a doc_id, a nltk text file handle, and
# Returns the loaded nltk.Text while storing it in memory
def load_nltk_text(doc_id, nltk_texts_file_object):
    global nltk_texts
    if doc_id in nltk_texts:
        return nltk_texts[doc_id]
    text = ''
    if doc_id in nltk_offsets:
        nltk_texts_file_object.seek(nltk_offsets[doc_id])
        text = pickle.load(nltk_texts_file_object)
    nltk_texts[doc_id] = text
    return nltk_texts[doc_id]

def get_tfidf_weight(tf, df=0, N=0):
    tf_weight = 0
    idf_weight = 1
    if tf:
        tf_weight = 1 + log10(tf)
    if df:
        idf_weight = log10(N / df)
    return tf_weight * idf_weight

# Adapted from: http://www.nltk.org/_modules/nltk/text.html
def get_similar(nltk_text, word, num=20):
    """
    Distributional similarity: find other words which appear in the
    same contexts as the specified word; list most similar words first.

    :param word: The word used to seed the similarity search
    :type word: str
    :param num: The number of words to generate (default=20)
    :type num: int
    :seealso: ContextIndex.similar_words()
    """
    if '_word_context_index' not in nltk_text.__dict__:
        nltk_text._word_context_index = ContextIndex(
        nltk_text.tokens, filter=lambda x: x.isalpha(), key=lambda s: s.lower())
    word = word.lower()
    wci = nltk_text._word_context_index._word_to_contexts
    if word in wci.conditions():
        contexts = set(wci[word])
        fd = Counter(w for w in wci.conditions() for c in wci[w] if c in contexts and not w == word)
        return [w for w, _ in fd.most_common(num)]
    return []

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
# conn.close()
