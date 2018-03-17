This is the README file for A0136070R's submission

Contact email: e0005572@u.nus.edu

== Python Version ==

I'm using Python Version 3.6.4 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

The indexing script is largely similar to Assignment 2's. However, I also store N, the total number of documents in the reuters collection, and the document length for each document (the key is the doc id). We need N to calculate the idf value (given by log10(N / df)), and we need the length of each document to do length normalization on the dot product of the tfidf of document and query. Without normalization, very long documents will become the most relevant documents by default.

I also allow repeated stems in each document. This is done by removing the set() calls in the text preprocessing function. (In the boolean retrieval model, I removed duplicates because we were only concerned about presence versus absence.) This allows the tf to be retrieved in search.py. As such, instead of {term: (df, skip list where data=doc_id)}, we have {term: (df, skip list where data=(doc_id, tf))}.

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
