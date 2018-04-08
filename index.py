#!/usr/bin/python
import nltk
import sys
import getopt

import os
import string
import bisect
import pickle
import sqlite3

from collections import Counter
from time import time

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.lemma import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from constants import lengths_file_name, print_time, database_file_name, zones_table_name
from skip_list import SkipList

conn = sqlite3.connect(database_file_name)
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS ?', zones_table_name)
c.commit()
c.execute('CREATE TABLE ? (document_id INTEGER, title TEXT, date_posted TEXT, court TEXT)', zones_table_name)
c.commit()

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
    seen_postings_by_lemma = {}
    with open(csv_file_path, 'r') as f:
        reader = csv.reader(f)
        # Get column headers and move read pointer
        # filter(None) helps remove falsey columns (e.g. blank)
        # columns expected value = ['document_id', 'title', 'content', 'date_posted', 'court']
        columns = list(filter(None, next(reader)))
        for csv_row in reader:
            document_id, title, content, date_posted, court = csv_row
            document_id = int(document_id)
            # TODO: Index content here
            c.execute('INSERT INTO ? VALUES (?, ?, ?, ?)',
                (zones_table_name, document_id, title, date_posted, court))
    c.commit()
    with open(dictionary_file_name, 'w') as d, open(postings_file_name, 'wb') as p:
        for lemma in dictionary:
            d.write('{lemma},{offset}\n'.format(lemma=lemma, offset=p.tell()))
            postings = dictionary[lemma]
            pickle.dump(postings, p)
    with open(lengths_file_name, 'wb') as l:
        pickle.dump(N, l)
        pickle.dump(lengths_by_document, l)

'''
Preprocess a text string in the following order:
    1. (L77) Do sentence tokenization
    2. (L75) For each sentence, do case-folding, word tokenization
    3. (L73) Filter out punctuations, non-alphabetical words, and stopwords
    4. (L72) Lemmatize the remaining words
    5. (L78) Return a Counter of lemmatized words (i.e. {lemma: frequency})
'''
def get_preprocessed(text):
    sentences = map(
        lambda sentence: list(map(
            lambda word: lemmatizer.lemmatize(word),
            filter(
                lambda token: token not in string.punctuation and token.isalpha() and token not in stopwords,
                word_tokenize(sentence.lower())
                ))),
        sent_tokenize(text))
    return Counter((lemma for lemmas in sentences for lemma in lemmas))

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
