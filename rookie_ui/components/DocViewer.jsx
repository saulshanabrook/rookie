"use strict";
/*
Doc viewer
*/

var React = require('react');
var Story = require('./Story.jsx');
var _ = require('lodash');
var moment = require('moment');
var Panel = require('react-bootstrap/lib/Panel');

module.exports = React.createClass({

    render: function(){
        console.log(docs.length);
        let docs = _.filter(this.props.docs, function(d) {
            return moment(d.pubdate) > moment(this.props.start_selected, "YYYY-MM-DD") &&
                   moment(d.pubdate) < moment(this.props.end_selected, "YYYY-MM-DD")
        }, this);
        docs = _.sortBy(docs, function(d){
            return moment(d.pubdate);
        });
        if (docs.length < 1){
            return <div></div>;
        }
        let f = this.props.f;
        var markup = function(doc) {
           return {__html: doc.snippet};
        };
        let props = this.props;

        let rowStyle = {
            width:"100%",
            overflow:"hidden"
        };

        return(
            <div style={rowStyle}>
                {docs.map(function(doc, n) {
                    return <div key={n} style={rowStyle}>
                                <Story url={doc.url}
                                pubdate={doc.pubdate}
                                snippet={doc.snippet.htext}/>
                           </div>;
                })}
           </div>
        );
       }
});
