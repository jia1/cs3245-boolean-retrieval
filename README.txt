This is the README file for A0136070R's submission

Contact email: e0005572@u.nus.edu

== Python Version ==

I'm using Python Version 3.6.4 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

I assume the reader has sufficient knowledge about my boolean retrieval and vector space model
systems back from Assignment 2 and 3.

For Assignment 4, the general procedure is this:

1. Index the document_id and content columns of CSV file
  - Each line of dictionary.txt is: (term),(byte offset in postings.txt)
  - postings.txt contains skip lists of (doc_id, term frequency)
  - lengths.txt contains an integer N, total number of documents in the collection, and
    lengths_by_document, with the format { doc_id: number of significant tokens }
    Significant tokens are tokens which are non-punctuation, fully alphabetical, and non-stopword
  - Each line of offsets.txt is: (doc_id),(byte offset in texts.txt)
  - texts.txt contains nltk.Text of every document that is pre-processed with
    nltk.tokenize.word_tokenize only (non-significant tokens remain inside)
  - Note that my terms are uni-lemma (not bi-word, not stem, etc)
2. Parse the query
  - If query contains 'AND' (case-sensitive) then it is a boolean retrieval query and will
    undergo boolean retrieval
  - Boolean retrieval queries with phrases are treated the same way as:
    (phrase word 1) AND (phrase word 2) AND ...
  - Otherwise the query will be fed into the vector space retrieval model directly
  - Queries that undergo boolean retrieval will yield a single postings skip list that is unranked,
    these documents will be fed into the vector space retrieval model for ranking
3. What if boolean retrieval yields an empty postings skip list?
  - In my system, the documents which are fetched via boolean retrieval are assigned to the "high"
    list. Those that are not fetched are relegated to the "low" list. The documents in these two
    lists are then ranked separately. The output is currently set to be "high" + "low" list.
  - Note that the documents in the "high" list are always considered to be more relevant than
    every document in the "low" list.
  - As such, there will always be documents returned.
4. Pseudo relevance feedback + query expansion
  - Please refer to the BONUS document for more information
  - Semi-automatic query expansion is switched on
5. Zones
    - title, date_posted, and court are indexed into a local sqlite database
      (need to un-comment the database connection, execution and commit code)
    - However, queries for these should follow a special format, out of scope of this assignment
      E.g. title:(some title) instead of the normal word and phrasal queries
    - As such, I have not created the database fetch queries

In trying to gain as much precision as possible, under the assumption that the true ranking and computed ranking are of similar distribution, I added magic number limits on the returning document list. These limits
also reduce the runtime. A possible improvement to such magic numbers would be to construct some function
out of the number of documents in the collection (log N for example).

The score for this system on the leaderboard is currently 0 due to runtime errors on the leaderboard machine.

Score was 0.3 when indexing was to be done online, it then dropped to 0.22 when indexing was to be done offline. The score dropped to 0.12 after some amendments to the leaderboard system, but I was already plagued
with a lot of runtime errors online ):

A suggestion would be to accept answer files instead, but this also means people can copy the answers...

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. index.py: Script to index documents into {term: (df, postings)}.
  - Also stores additional information (i.e. total number of documents in collection,
    document lengths) for the vector space model.
2. search.py: Script to do boolean retrieval + ranked retrieval in succession
  - Applicable if the former returns non-empty postings skip list
  - Otherwise, just pure vector space retrieval
3. skip_list.py: A module which contains the SkipList and SkipListNode classes.
  - SkipList can contain a SkipListNode, which can be linked with more SkipListNode.
4. constants.py: A module which contains constants (e.g. magic numbers and strings) shared
    across source files E.g. file name of file storing the document lengths
5. nltk_context_index.py: A nltk.Text dependency that was edited by myself to return values
    instead of printing the values out (99% from nltk.Text)
6. stopwords.txt: File containing one stopword per line
7. cli_output.txt: A sample log file of the command line output.
8. BONUS.docx: For bonus
9. BONUS.pdf: BONUS.docx exported as PDF

Indexes such as dictionary.txt, postings.txt, lengths.txt are on https://github.com/jia1/cs3245-information-retrieval too

== Statement of individual work ==

Please initial one of the following statements.

[LJY] I, A0136070R, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0136070R, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>

I did this assignment by myself code-wise for the indexing and retrieval parts, but I consulted the
following sources for formulae, API, and adaptation of code for debugging / NLP tasks:

- [CS3245 Lecture Notes](http://www.comp.nus.edu.sg/~zhaojin/cs3245_2018/syllabus.html)
  for the tfidf formulae and the cosineScore(q) algorithm
- [Debugging _csv.Error: field larger than field limit](https://stackoverflow.com/a/15063941)
- [Reading, using, and copying code from nltk.Text for adaptation]
  (http://www.nltk.org/_modules/nltk/text.html)
