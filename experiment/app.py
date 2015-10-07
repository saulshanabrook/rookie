import pdb
import pickle
from dateutil.parser import parse
from flask import Flask
from flask import render_template
from flask import request
from experiment import log
from experiment.views import Views
from experiment.models import Models, Parameters
from snippets.prelim import DocFetcher
from rookie import page_size
from experiment import LENS_CSS, BANNER_CSS
from rookie import (
    log
)

app = Flask(__name__)


@app.route('/')
def index():
    log.info("index routing")
    return render_template('index.html',
                           lens_css=LENS_CSS,
                           banner_css=BANNER_CSS)


@app.route('/old/results', methods=['GET'])
def results_old():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params)

    log.debug('got results and tops')

    results = [r for r in results]

    pages = Models.get_pages(len(results), page_size)

    log.debug('got pages')

    message = Models().get_message(params, pages, len(results))

    log.debug('got message')

    # page_results = results[params.page * 10:params.page * 10+10]

    page_results = results
    results.sort(key=lambda x: parse(x['fields']['pubdate']))
    view = Views().get_results2_page(params.q, page_results, tops, len(results), message, pages, LENS_CSS, BANNER_CSS)

    return view


@app.route('/results', methods=['GET'])
def results():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params, snippets=True)

    log.debug('got results and tops')

    # turn into a mutable list. was tuples for for caching
    results = [r for r in results]
    tops = [o for o in tops]

    pdb.set_trace()
    view = Views().get_results_page_relational(params.q, tops, LENS_CSS, BANNER_CSS)

    return view


@app.route('/testing', methods=['GET'])
def testing():

    log.debug('/search/ data:')

    params = Models.get_parameters(request)

    log.debug('got params')

    results, tops = Models().search(params, snippets=True)

    log.debug('got results and tops')

    # turn into a mutable list. was tuples for for caching
    results = [r for r in results]
    tops = [o for o in tops]

    p = Parameters()
    p.q = "coastal restoration"
    p.term = "bobby jindal"
    p.termtype = "people"

    # df = DocFetcher()
    # docs = df.search_for_documents(p)
    # pdb.set_trace()
    # docs = df.search_for_documents(p)
    coastal = pickle.load(open("coastal.tmp", "r"))

    for docno, doc in enumerate(coastal['docs']):
        for sentenceno in doc['sentences']:
            sentence_tokens = doc['sentences'][sentenceno]['tokens']
            sentence = ""
            for token in sentence_tokens:
                sentence = sentence + " " + sentence_tokens[token]
            pdb.set_trace()

    coastaljindal = pickle.load(open("coastaljindal.p", "r"))
    pdb.set_trace()
    view = Views().get_results_page_relational(params.q, tops, LENS_CSS, BANNER_CSS)

    return view

if __name__ == '__main__':
    app.run(debug=True)
