import unittest
import json
import pdb
import glob
import itertools

from rookie.utils import dedupe_people
from rookie import processed_location
from rookie.classes import Document
from rookie.classes import Coreferences
from rookie.classes import N_Grammer
from rookie.classes import propagate_first_mentions
from rookie.utils import stop_word, get_gramner


class GenericTestCase(unittest.TestCase):

    def test_make_document(self):
        with open("data/sample_wrapper_output.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        self.assertTrue(len(doc.sentences) > 0)

    def test_find_entities(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        ner = doc.sentences[0].ner[0]
        self.assertEqual(ner.type, "ORGANIZATION")
        org_name = " ".join([i.raw for i in ner.tokens])
        self.assertEqual(org_name, "New Orleans Civil Service Commission")

    def test_create_ngrams(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grams = N_Grammer()
        gram_total = len([(i[0].raw, i[1].raw) for i in
                         grams.get_ngrams(sentence.tokens)])
        self.assertEqual(gram_total, 52)

    def test_filter_ngrams(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        grammer = N_Grammer()
        bigrams = grammer.get_syntactic_ngrams(sentence.tokens, 2)[0]
        self.assertTrue(all(bigram[0].is_noun() or
                            bigram[0].is_adjective()) for b in bigrams)
        trigrams = grammer.get_syntactic_ngrams(sentence.tokens, 3)[1]
        self.assertTrue(all(bigram[0].is_noun() or
                        bigram[0].is_adjective()) for b in trigrams)

    def test_find_window(self):
        with open("data/sample_wrapper_output_2.json", "r") as to_read:
            py_wrapper_output = json.loads(to_read.read())
        doc = Document(py_wrapper_output)
        sentence = doc.sentences[0]
        window = Window()
        out = window.get_window(sentence.tokens, sentence.ner[3].tokens, 1)
        out = " ".join([i.raw for i in out])
        target = "Mayor Mitch Landrieus Great"
        self.assertEqual(out, target)

    def test_strip_stop_words2(self):
        self.assertTrue(stop_word("NEW ORLEANS"))

if __name__ == '__main__':
    unittest.main()
