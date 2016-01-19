'''
The main web app for rookie
'''
import ipdb
import pylru
import time
import json
import math
from dateutil.parser import parse
from experiment.models import make_dataframe, results_to_json_hierarchy, get_keys, get_val_from_df, bin_dataframe
from flask import Flask
from rookie.rookie import Rookie
from flask import request
from facets.query import get_facets_for_q
from experiment.views import Views
from collections import defaultdict
from experiment.models import Models, Parameters
from experiment import IP, ROOKIE_JS, ROOKIE_CSS
from experiment import log
from whooshy.reader import query_subset
from experiment.models import get_doc_metadata

app = Flask(__name__)

views = Views(IP, ROOKIE_JS, ROOKIE_CSS)

print views.rookie_css

cache = pylru.lrucache(1000)

# BTO: this is problematic. assumes shared memory for all request processes.
# flask individual file reloading breaks this assumption. so does certain types of python parallelism.
# better to use cache in outside storage. e.g. redis/memcached. but psql might be more convenient for us.
# or, could lrucache decorator be used instead?
# alias_table = defaultdict(lambda : defaultdict(list))

# AH: TODO check w/ brendan.

@app.route("/post_for_docs", methods=['GET'])
def get_doc_list():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    aliases = [] # cache[params.q + "##" + params.detail]
    
    results = Models.f_occurs_filter(results, facet=params.f, aliases=aliases)

    doc_list = Models.get_doclist(results, params, aliases=aliases)

    print [i["pubdate"] for i in doc_list]

    return json.dumps(doc_list)


def date_filter(results, start, end):
    '''
    TODO delete 
    '''
    if start is not None and end is not None:
        md = lambda r: get_doc_metadata(r)
        return [r for r in results if parse(md(r)["pubdate"]) > start and parse(md(r)["pubdate"]) < end]
    else:
        return results

@app.route('/medviz', methods=['GET'])
def medviz():

    params = Models.get_parameters(request)

    results = Models.get_results(params)

    binned_facets = get_facets_for_q(params.q, results, 9)

    #for f in facets:
    #    cache[params.q + "##" + f] = aliases[f]
    #    alias_table[params.q][f] = aliases[f]

    aliases = defaultdict(list) # TODO

    doc_list = Models.get_doclist(results, params)

    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    binsize = "month"

    df = make_dataframe(params, binned_facets['g'], results, q_pubdates, aliases)

    df = bin_dataframe(df, binsize)

    try:
        start = min(q_pubdates)
        stop = max(q_pubdates)
        keys = get_keys(start, stop, binsize)
    except ValueError:
        keys = []

    if binsize == "month":
        q_data = [str(params.q)] + [get_val_from_df(params.q, key, df, binsize) for key in keys]

    facet_datas = {}
    for f in binned_facets['g']:
        start_time = time.time()
        facet_datas[f] = [str(f)] + [get_val_from_df(f, key, df, binsize) for key in keys]
        # fresults = Models.f_occurs_filter(results, facet=params.detail, aliases=aliases)
        # fdoc_list = Models.get_doclist(results, params, PAGE_LENGTH, aliases=aliases)
        # print "[*] getting facets took {}".format(start_time - time.time())

    keys = ["x"] + [k + "-1" for k in keys] # hacky addition of date to keys

    display_bins = []
    for key in binned_facets:
        if key != "g":
            tmp = {}
            tmp["key"] = key
            tmp["facets"] = binned_facets[key]
            display_bins.append(tmp)

    view = views.get_q_response_med(params, doc_list, facet_datas, keys, q_data, len(results), binsize, display_bins, binned_facets['g'])

    return view


if __name__ == '__main__':
    app.run(debug=True, port=5000)
