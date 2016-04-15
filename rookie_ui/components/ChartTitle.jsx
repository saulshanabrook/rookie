"use strict";
/*
Chart title
*/

var React = require('react');
var _ = require('lodash');
var moment = require('moment');
var ClickableQF = require('./ClickableQF.jsx');

module.exports = React.createClass({

    getStoryPhrase: function (argument) {
        if ((this.props.ndocs) == 1) {
            return "document";
        } else{
            return "documents";
        }   
    },

    getOtherTopics: function(){
        if (this.props.f == -1 & this.props.mode == "docs"){
            return <span><span style={{color:"#b33125", textDecoration: "underline", cursor: "pointer"}} onClick={this.props.toggleIntro}>subjects related</span> to <span style={{color: "#0028a3", fontWeight: "bold"}}>{this.props.q} </span> </span>;
        }else{
            return "";
        }
    },

    render: function() {
        
        let text_dec = "none";
        let on_click_f = "";
        if (this.props.mode == "overview"){
            text_dec = "underline";
            on_click_f = this.props.turnOnDocMode;   
        }
        let status_start = <span>Found {this.props.ndocs} <span onClick={on_click_f} style={{textDecoration: text_dec}}>{this.getStoryPhrase()}</span> for </span>;
            
        let otherTopics = this.getOtherTopics();
        let q_color = "#0028a3";
        let f_color = "#b33125";
        let f = this.props.f;
        let show = (f != -1 & f != undefined);
        let tot_f_docs = _.size(this.props.f_docs);
        if (this.props.f != -1){
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/> — <span style={{fontWeight: "bold"}}>{tot_f_docs}</span> mention <ClickableQF showX={true} xHandler={this.props.fX} color={f_color} text={this.props.f}/> </span>
        } else {
            return <span><span>{status_start}</span><ClickableQF showX={show} xHandler={this.props.qX} color={q_color} text={this.props.q}/> <span style={{float: "right"}}>{otherTopics}</span></span>
        }
    }
});
