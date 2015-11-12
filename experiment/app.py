import pdb
import datetime
import threading
import pylru
from flask import Flask
from flask import request
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import get_snippet
from experiment import LENS_CSS, BANNER_CSS
from experiment import (
     log
)
from whooshy.reader import query_whoosh
from whooshy.reader import query_subset
from collections import OrderedDict

app = Flask(__name__)

cache = pylru.lrucache(100)


def tokens_to_sentence(sentence_tokens):
    sentence = ""
    for token in sentence_tokens:
        sentence = sentence + " " + sentence_tokens[token]['word']
    return sentence.strip(" ")


def worker(queue, snippets_dict):
    for index, q_item in enumerate(queue):
        key = q_item[0][0] + "-" +  q_item[1]
        sentences = []
        for item in q_item[2]:
            pubd = item[1]['pubdate']
            docid = item[0]
            for sentence in item[1]['sentences']:
                sentences.append((sentence, pubd, item[0], docid))
         
        # snippet returns:
        # tokens, datetime, article_id, ?, qtokenindex, ftokenindex)
        cache[key] = get_snippet(q_item[0][0], q_item[1], sentences, q_item[3].q)
        print "got snippet {}|{}|{}".format(q_item[0][0], q_item[1], q_item[3].q)


@app.route('/', methods=['GET'])
def index():
    log.info("index routing")
    return Views().get_start_page(LENS_CSS, BANNER_CSS)


@app.route('/get_snippet_post', methods=['POST'])
def get_snippet_post():
    term = request.args.get('term')
    termtype = request.args.get('termtype')
    query = request.args.get('q')
    key = term + "-" + termtype
    try:
        snippet = cache.peek(key) # TODO: handle cache failures
        snippet = list([list(i) for i in snippet])
        for s in snippet:
            s[0] = list(s[0])
        for s_index, sentence in enumerate(snippet):
            tokens = [i for i in sentence[0] if i != ","]  #TODO this is only one sentence
            qtoks = set(query.split(" ")).intersection(set(tokens))
            ftoks = set(term.split(" ")).intersection(set(tokens))
            qftoks = qtoks.union(ftoks)
            left = []
            box_l = []
            center = []
            box_r = []
            right = []
            slots = [left, box_l, center, box_r, right]
            slots_index = 0
            place_keeper = 0
            i = 0
            looking_for_qf = False
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i += 1
            slots_index += 1
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            slots_index += 1
            while tokens[i] not in qftoks and i < len(tokens) - 1:
                slots[slots_index].append(str(tokens[i]))
                i +=1
            
            test = []
            test.append("e")
            snippet[s_index][0] = slots


    except KeyError: # TODO FIX
        snippet = "waiting for cache fix TODO"
    return Views().print_snippet(snippet)


@app.route('/detail', methods=['GET'])
def detail():

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    query_back = query_whoosh(p.q)

    docid = p.docid

    q_and_t = []

    # TODO: this logic should go in query_whoosh
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            q_and_t.append((term[0], termtype))

    dt = Models.get_tokens(docid)

    dt = OrderedDict(sorted(dt.items(), key=lambda t: int(t[0])))

    tokens = [dt[i] for i in dt.keys()]

    headline = Models.get_headline(docid)

    pubdate = Models.get_pub_date(docid)

    view = Views().get_detail_page(p.q, q_and_t, headline, pubdate, tokens, LENS_CSS, BANNER_CSS)

    return view

@app.route('/testing', methods=['GET'])
def testing():

    p = Models.get_parameters(request)

    snippets_dict = defaultdict(str)

    query_back = query_whoosh(p.q)

    q_and_t = []
    queue = []
    for termtype in query_back[1].keys():
        for term in query_back[1][termtype]:
            subset = query_subset(query_back[0], term, termtype)
            queue.append((term, termtype, subset, p,))
            q_and_t.append((term[0], termtype))
    t = threading.Thread(target=worker, args=(queue, snippets_dict))
    t.start()

    view = Views().get_results_page_relational_overview(p.q, q_and_t, LENS_CSS, BANNER_CSS)

    return view


if __name__ == '__main__':
    app.run(debug=True)
