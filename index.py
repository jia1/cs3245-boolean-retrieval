#!/usr/bin/python
import sys
import getopt

import os
import string
import bisect
import pickle

import csv
import sqlite3

import codecs # For submitting script as Python 2.7

from collections import Counter
from time import time

from nltk import Text
from nltk.corpus import PlaintextCorpusReader
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from constants import (
    lengths_file_name,
    nltk_offsets_file_name,
    nltk_texts_file_name,
    database_file_name,
    zones_table_name,
    print_time
    )
from skip_list import SkipList

# Database for zones
'''
conn = sqlite3.connect(database_file_name)
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS {}'.format(zones_table_name))
conn.commit()
c.execute('CREATE TABLE {} (document_id INTEGER, title TEXT, date_posted TEXT, court TEXT)'
    .format(zones_table_name))
conn.commit()
'''

# Adapted from: https://stackoverflow.com/a/15063941
max_int = sys.maxsize
should_decrement = True
while should_decrement:
    try:
        csv.field_size_limit(max_int)
        should_decrement = False
    except OverflowError:
        max_int = int(max_int / 2)

start_time = time()

with open('stopwords.txt') as f:
    stopwords = set(map(lambda ln: ln.strip(), f.readlines()))

'''
Create a dictionary[lemma] -> sorted([(doc id, tf)]) and write to the dictionary and postings file
    - dictionary is a dictionary whose keys are lemmas and whose values are sorted posting lists
    - postings will then be converted into a skip list with sqrt(len(postings)) skip pointers 
'''
def do_indexing(csv_file_path, dictionary_file_name, postings_file_name):
    dictionary = {}
    lengths_by_document = {}
    nltk_texts_by_document = {}
    seen_postings_by_lemma = {}
    f = codecs.open(csv_file_path, 'r', errors='ignore')

    reader = csv.reader(f)
    # Get column headers and move read pointer
    # filter(None) helps remove falsey columns (e.g. blank)
    # columns expected value = ['document_id', 'title', 'content', 'date_posted', 'court']
    columns = list(filter(None, next(reader)))
    N = 0
    for csv_row in reader: # Uncomment this line if not testing
    # for i in range(100): # Comment this line if not testing
        # csv_row = next(reader) # Comment this line if not testing
        N += 1
        document_id, title, content, date_posted, court = csv_row
        # BEGIN procedure index content (i.e. vector space model indexing)
        nltk_text, text_counter = get_preprocessed(content)
        posting = int(document_id)
        lengths_by_document[posting] = sum(text_counter.values())
        nltk_texts_by_document[posting] = nltk_text
        for lemma, frequency in text_counter.items():
            posting_frequency_tuple = (posting, frequency)
            if lemma not in dictionary:
                dictionary[lemma] = [posting_frequency_tuple]
                seen_postings_by_lemma[lemma] = set((posting,))
            else:
                if posting not in seen_postings_by_lemma[lemma]:
                    bisect.insort(dictionary[lemma], posting_frequency_tuple)
                    seen_postings_by_lemma[lemma].add(posting)
        # END procedure
        '''
        c.execute('INSERT INTO {} VALUES (?, ?, ?, ?)'.format(zones_table_name),
            (document_id, title, date_posted, court))
    conn.commit()
    '''
    f.close()

    with open(dictionary_file_name, 'w') as d, open(postings_file_name, 'wb') as p:
        for lemma in dictionary:
            d.write('{lemma},{offset}\n'.format(lemma=lemma, offset=p.tell()))
            postings = dictionary[lemma]
            pickle.dump(postings, p)
    with open(lengths_file_name, 'wb') as l:
        pickle.dump(N, l)
        pickle.dump(lengths_by_document, l)
    with open(nltk_offsets_file_name, 'w') as i, open(nltk_texts_file_name, 'wb') as t:
        for doc_id, nltk_text in nltk_texts_by_document.items():
            i.write('{doc_id},{offset}\n'.format(doc_id=doc_id, offset=t.tell()))
            pickle.dump(nltk_text, t)

'''
Preprocess a text string in the following order:
    1. Do word tokenization
    2. Do case-folding
    3. Filter out punctuations, non-alphabetical words, and stopwords
    4. Lemmatize the remaining words
    5. Return a tuple of nltk.Text(output from step 1) and
        Counter of lemmatized words from step 4 (i.e. {lemma: frequency})
'''
def get_preprocessed(text):
    tokens = word_tokenize(text.strip())
    tokens_to_index = map(
        lemmatizer.lemmatize,
        filter(
            lambda token: token not in string.punctuation and token.isalpha() and token not in stopwords,
            map(str.lower, tokens)
            )
        )
    return (Text(tokens), Counter(tokens_to_index))

def usage():
    print('Usage: ' + sys.argv[0] + ' -i dataset-file -d dictionary-file -p postings-file')

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
stop_time = time()
print_time(start_time, stop_time)
# conn.close()
