This is the README file for A0136070R's submission

== Python Version ==

I'm using Python Version 3.6.4 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. index.py: Accepts a directory of text files and two output files: dictionary.txt where each line follows the format "stem,integer" where integer represents the offset from the first byte of the postings file, and postings.txt, a binary file which contains the postings (i.e. file name) which the stems are present in (after preprocessing the text).
2. search.py: Reads a query file, parses and resolve the query such that the postings for the relevant stems are fetched and put together to answer the query.
3. skip_list.py: A module which contains the SkipList and SkipListNode classes. SkipList can contain a SkipListNode, which can be linked with more SkipListNode.

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

I did this assignment by myself.
