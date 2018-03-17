This is the README file for A0136070R's submission

Contact email: e0005572@u.nus.edu

== Python Version ==

I'm using Python Version 3.6.4 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

The indexing script is largely similar to Assignment 2's. However, I also store N, the total number of documents in the Reuters collection, and the document length for each document (the key is the doc id). We need N to calculate the idf value (given by log10(N / df)), and we need the length of each document to do length normalization on the dot product of the tfidf of document and query. Without normalization, very long documents will become the most relevant documents by default.

I also allow repeated stems in each document. This is done by removing the set() calls in the text preprocessing function. (In the boolean retrieval model, I removed duplicates because we were only concerned about presence versus absence.) This allows the tf to be retrieved in search.py. As such, instead of {term: (df, skip list where data=doc_id)}, we have {term: (df, skip list where data=(doc_id, tf))}.

As for search.py, the main steps are as follows:

1. Load the dictionary into memory. The variable is "offsets" and its format is {indexed stem: byte offset in postings.txt}.
2. Load N, the total number of documents in the Reuters collection, and the lengths of each document into memory. The variable name for N is "N", and the document lengths are stored as lengths_by_document. The format for lengths_by_document is {document id: document length}. Note that the document length indexed here is equivalent to the total number of indexed stems from the document, and does not include the number of non-alphabetical expressions, stopwords, etc.
3. For each query:
    a. Process it into the form {stem: frequency} to get the tfidf values of the query.
    b. Iterate through each stem in the query, and increment the dot product part of the document's tfidf and the query's tfidf. This is done by going through the entire postings skip list for each stem and storing the accumulated tfidf values in a separate dictionary (i.e. tfidf_by_document)
    c. Negate and normalize the tfidf values from (b) accordingly. Negation is required because the heap built-in functionality for Python only allows min-heap, but we want highest tfidf first.
    d. Heapify and pop up to top_n times (top_n is currently set to 10 in constants.py).
    e. Write document ids to file

The tfidf values are derived from a function. This function accepts tf, optional df, and optional N. The function first checks for the value of tf. If tf = 0, then tf_weight remains 0. Otherwise, tf = 1 + log10(1 + tf) as specified in w7 lecture. Then, the function will check for the df value. If df is not given, or if it is 0, the idf_weight remains 0 because df is a denominator in the idf formula and cannot be 0. Otherwise, idf = log10(N / df) where N is the total number of documents in the collection.

For the query, the df argument is not supplied as it is equal to N (the collection is just the query itself). In addition, there is no need to normalize the query tfidf value as all other document tfidf values have this same multiplier. As we are more concerned about the ranking (relative rather than absolute), we only need to do: cosine_similarity(q, d) = tf(q) * tfidf(d) / len(d)

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. index.py: Script to index documents into {term: (df, postings)}. Also stores additional information (i.e. total number of documents in collection, document lengths) for the vector space model.
2. search.py: Script to do ranked retrieval by calculating the tfidf values of each document and their cosine similarities w.r.t query.
3. skip_list.py: A module which contains the SkipList and SkipListNode classes. SkipList can contain a SkipListNode, which can be linked with more SkipListNode.
4. constants.py: A module which contains constants (e.g. magic numbers and strings) that are shared across source files. An examples would be the file name of file storing the document lengths.
6. cli_output.txt: A sample log file of the command line output.

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

I did this assignment by myself code-wise, but I consulted the following sources for formulae and API:

- [CS3245 Lecture Notes](http://www.comp.nus.edu.sg/~zhaojin/cs3245_2018/syllabus.html) for the tfidf formulae and the cosineScore(q) algorithm
- [Python 3.6.4 documentation](https://docs.python.org/3/) for general built-in function help and also on the collections.Counter and heapq libraries
- [NumPy reference](https://docs.scipy.org/doc/numpy/reference/index.html) but afterwards I realized I no longer needed matrix operations as it is more space-saving to evaluate values while iterating instead of accumulating them into a matrix
