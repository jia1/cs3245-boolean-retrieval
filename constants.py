# database_file_name = 'intellex_indexes\\zones.db'
database_file_name = 'zones.db'
zones_table_name = 'zones'

# lengths_file_name = 'intellex_indexes\\lengths.txt'
lengths_file_name = 'lengths.txt'
nltk_offsets_file_name = 'offsets.txt'
nltk_texts_file_name = 'texts.txt'
and_operator_name = 'and'

def print_time(start_time, stop_time):
    print('Time taken: {0:.5f} seconds'.format(stop_time - start_time))
