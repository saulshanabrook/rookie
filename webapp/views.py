import ipdb
from flask import render_template

class Views(object):

    def __init__(self, IP, ROOKIE_JS, ROOKIE_CSS):
        '''
        Initalize the views
        '''
        self.ip = IP
        self.js = ROOKIE_JS
        self.rookie_css = ROOKIE_CSS


    def get_q_response_med(self, params, results, q_and_t, chart_bins, q_datas, len_results, binsize, binned_facets, g_facets):
        '''
        return medviz view
        '''
        if self.ip == "localhost":
            baseurl = "http://localhost:5000/"
        else:
            baseurl = "" #TODO: why this should be blank for an IP address?
        response = render_template(
            'medviz.html',
            query=params.q,
            f_counts=q_and_t,
            chart_bins=chart_bins,
            q_datas=q_datas,
            g_facets=g_facets,
            doc_list=results,
            len_results=len_results,
            detail=binsize,
            len_keys=len(chart_bins),
            binned_facets=binned_facets,
            IP=self.ip,
            baseurl=baseurl,
            ROOKIE_JS=self.js,
            ROOKIE_CSS=self.rookie_css
        )

        return response