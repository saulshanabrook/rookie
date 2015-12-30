import datetime
import threading
import itertools
import pylru
import json
import time
import math
import ujson
import datetime as dt
import ipdb
from dateutil.parser import parse
from experiment.models import make_dataframe
from flask import Flask
from rookie.rookie import Rookie
from flask import request
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from snippets.prelim import get_snippet
from experiment import LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS
from experiment import log
from experiment import PAGE_LENGTH
from experiment import PAGE_LENGTH
from whooshy.reader import query_whoosh
from whooshy.reader import query_subset
from collections import OrderedDict
from experiment.models import get_pubdate_index, get_doc_metadata

app = Flask(__name__)

cache = pylru.lrucache(100)

views = Views(LENS_CSS, BANNER_CSS, IP, ROOKIE_JS, ROOKIE_CSS)

PI = get_pubdate_index()

alias_table = defaultdict(lambda : defaultdict(list))

@app.route('/', methods=['GET'])
def index():
    log.info("index routing")
    return views.get_start_page()

@app.route("/get_doc_list", methods=['POST'])
def get_doc_list():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    status = Models.get_status(params)

    if params.detail == params.q:
        # the user wants date detail for Q
        results = Models.date_filter(results, params)
    else:
        results = Models.date_filter(results, params)
        results = Models.f_occurs_filter(results, params, alias_table[params.q][params.detail])
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)
    return views.get_doc_list(doc_list, params, status, [params.detail])


def log_scale(p):
    return math.log(p + 1)


@app.route('/facets', methods=['GET'])
def testing():

    log.debug('facets')

    global alias_table

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    log.debug('got results')

    facets, aliases = Models.get_facets(params, results, 9)

    for f in facets:
        alias_table[params.q][f] = aliases[f]

    log.debug('got bins and facets')

    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f).replace("_", " ")] + [log_scale(p) for p in list(df[f])])

    datas = [str(params.q).replace(" ", "_")] + [log_scale(p) for p in list(df[params.q])]
    keys = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_q_response(params, doc_list, facet_datas, keys, datas, status, len(results))

    return view

def pad(i):
    if len(i) == 1:
        return "0" + str(i)
    return i

@app.route('/medviz', methods=['GET'])
def medviz():

    log.debug('facets')

    global alias_table

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    with open(params.q.replace(" ", "_") + ".query", "w") as outf:
        for r in results:
            outf.write(r  + "\n")

    log.debug('got results')

    facets, aliases = Models.get_facets(params, results, 9)

    with open(params.q.replace(" ", "_") + "_aliases.json", "w") as outf:
        json.dump(aliases, outf)

    with open(params.q.replace(" ", "_") + ".facets", "w") as outf:
        for f in facets:
            outf.write(f  + "\n")

    for f in facets:
        alias_table[params.q][f] = aliases[f]

    log.debug('got bins and facets')

    start_time = time.time()
    doc_list = Models.get_doclist(results, params, PAGE_LENGTH)
    print "[*] building the doc list took {}".format(start_time - time.time())

    status = Models.get_message(len(results), params, len(doc_list), PAGE_LENGTH)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    binsize = "month"
    start_time = time.time()
    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    if binsize == "year":
        df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    elif binsize == "month":
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month)]).sum().unstack(0).fillna(0)
    else:
        assert binsize == "day"
        df = df.groupby([df['pd'].map(lambda x: x.year), df['pd'].map(lambda x: x.month), df['pd'].map(lambda x: x.day)]).sum().unstack(0).fillna(0)
    print "[*] building the data frames took {}".format(start_time - time.time())

    #df["NORA"][2010][11]
    start_time = time.time()
    if binsize == "year":
        keys = [str(i) for i in df[params.q].axes[0]]
    if binsize == "month":
        keys = itertools.product(*[[p for p in df[params.q].axes[0]], [p for p in df[params.q].axes[1]]])
        keys = [pad(str(i[0])) + "-" + str(i[1]) for i in keys]
        keys.sort(key=lambda x:(int(x.split("-")[1]), int(x.split("-")[0])))
    print "[*] getting the keys took {}".format(start_time - time.time())

    datas = [str(params.q).replace("_", " ")] + [df[params.q][int(key.split("-")[1])][int(key.split("-")[0])] for key in keys]

    facet_datas = []
    for f in facets:
        facet_datas.append([str(f).replace(" ", "_")] + [df[f][int(key.split("-")[1])][int(key.split("-")[0])] for key in keys])

    keys = ["x"] + [str(int(i.split("-")[1])) + "-" + str(int(i.split("-")[0])) + "-1" for i in keys]

    view = views.get_q_response_med(params, doc_list, facet_datas, keys, datas, status, len(results), binsize)

    return view


@app.route('/bigviz', methods=['GET'])
def bigviz():

    log.debug('facets')

    global alias_table

    params = Models.get_parameters(request)

    start_time = time.time()
    results = Models.get_results(params)
    print "getting results took {}".format(start_time - time.time())
    print "got results"

    start_time = time.time()
    facets, aliases = Models.get_facets(params, results, 3)
    print "getting facets took {}".format(start_time - time.time())
    print "got facets"

    for f in facets:
        alias_table[params.q][f] = aliases[f]

    print "got metadata"
    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]
    print "parsed dates"
    # df = make_dataframe(params, facets, results, q_pubdates, aliases)

    df = make_dataframe(params, facets, results, q_pubdates, aliases)
    df = df.groupby([df['pd'].map(lambda x: x.year)]).sum().unstack(0).fillna(0)
    
    facet_datas = []
    for f in facets:
        facet_datas.append([str(f)] + list(df[f]))

    datas = [str(params.q)] + list(df[params.q])
    labels = ["x"] + [str(i) + "-01-01" for i in df[params.q].axes[0]]

    view = views.get_big_viz(params, labels, facet_datas, datas)

    return view

if __name__ == '__main__':
    app.run(debug=True)
