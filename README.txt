This is the README file for A0136070R's submission

Contact email: e0005572@u.nus.edu

== Python Version ==

I'm using Python Version 3.6.4 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

First, I do indexing. For each text file, I preprocess the entire text. Preprocessing consists of the following steps:

1. Sentence tokenization (text string -> list of sentence strings)
2. Case-folding, word tokenization, and remove duplicate word tokens via set() for each sentence (each sentence string -> set of word tokens)
3. Filter out punctuations, non-alphabetical words, and stopwords (shrink each word token set)
4. Stem the remaining words, and remove duplicate stems (shrink each word token set)
5. Return the flattened set of stemmed words (list of sets -> set)

The preprocessing is done in this particular order to save as much computation time as possible.

After converting the text into a set of stems, I construct a dictionary of {stem: [posting]}. "stem" is the stem string, and [posting] is a list of document ids (integer). Insertion of document id is done via binary search (bisect module).

I then write the stems to dictionary.txt and the postings to postings.txt. In dictionary.txt, each line follows the format "stem,integer" where integer represents the offset from the first byte of the postings file. On the other hand, postings.txt is a binary file that can be saved or loaded to via pickle.dump and pickle.load respectively.

The indexing step is complete.

Next, I do searching. Searching consists of the following steps:

1. Load stem dictionary (without the postings) and the corresponding file byte offset
2. Parse each query string into postfix form, and gather the set of stems that appeared in the query
3. Load only the postings for the relevant stems
4. Transform the postfix form of the query into a parse tree
5. Recursively resolve the parse tree leaves, starting from the smallest postings skip list
6. Write the final postings skip list to the output file

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

1. index.py: Accepts a directory of text files and two output files: dictionary.txt where each line follows the format "stem,integer" where integer represents the offset from the first byte of the postings file, and postings.txt, a binary file which contains the postings (i.e. file name) which the stems are present in (after preprocessing the text).
2. search.py: Reads a query file, parses and resolve the query such that the postings for the relevant stems are fetched and put together to answer the query.
3. skip_list.py: A module which contains the SkipList and SkipListNode classes. SkipList can contain a SkipListNode, which can be linked with more SkipListNode.
4. parse_tree.py: A module which contains the ParseTree and ParseTreeNode classes. ParseTree can contain a ParseTreeNode, which can be linked with more ParseTreeNode.
5. constants.py: A module which contains constants (e.g. magic numbers and strings) that are shared across source files. Examples include the operator list, and their precedences.
6. command_line_output.txt: A sample log file of the command line output.

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
