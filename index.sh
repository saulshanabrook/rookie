#!/bin/bash
# This script builds all of the indexes rookie needs: whoosh, the meta data file and the db

python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus lens
python getting_and_processing_corpora/corpus_proc.py --nlpjar ~/research/nytweddings/stanford-corenlp-full-2015-04-20/ --corpus gawk
dropdb 'rookie' --if-exists
createdb -O rookie rookie
py getting_and_processing_corpora/setupdb.py
# python webapp/classes.py
python getting_and_processing_corpora/load_to_whoosh.py --corpus lens
python getting_and_processing_corpora/load_to_whoosh.py --corpus gawk
python facets/build_sparse_matrix.py --corpus lens
python facets/build_sparse_matrix.py --corpus gawk
