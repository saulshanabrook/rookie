"use strict";
/*
Main Rookie UI
*/

var React = require('react');
var ReactDOM = require('react-dom');
var _ = require('lodash');
var moment = require('moment');
require('moment-round');

var DocViewer = require('./DocViewer_baseline.jsx');
var SparklineStatus = require('./SparklineStatus.jsx');
var Chart = require('./Chart.jsx');
var ChartTitle = require('./ChartTitle.jsx');
var Question = require('./Question.jsx');
var SparklineGrid = require('./SparklineGrid.jsx');
var QueryBar = require('./QueryBar.jsx');
var SummaryStatus_tut = require('./SummaryStatus_tut.jsx');
var $ = require('jquery');
var Modal = require('./Modal.jsx');
var Modal_success = require('./Modal_success.jsx');
var Panel = require('react-bootstrap/lib/Panel');
var Button = require('react-bootstrap/lib/Button');
var Modal_doc = require('./Modal_doc.jsx');



let q_color = "#0028a3";
let f_color = "#b33125";

module.exports = React.createClass({

  set_width: function(){
    var width = $(window).width();
    var height = $(window).height();
    this.setState({width: width, height: height});
  },



  componentDidMount: function () {
    this.set_width();
    window.addEventListener("resize", this.set_width);
    window.addEventListener("keydown", this.handleKeyDown);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");

  },

  getInitialState(){
    //Notes.
    //convention: -1 == null
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    return {drag_r: false, drag_l:false, mouse_down_in_chart: false,
           mouse_is_dragging: false, width: 0, height: 0, click_tracker: -1,
           chart_mode: "intro",
           all_results: sents,
           start_selected:min,
           end_selected:max,
           summary_page:0,
           selected_doc:-1,
           selectedheadline: "",
           selectedsents: [],
           selectedpubdate: "",
           f_counts:this.props.f_counts,
           f: this.props.f,
           still_looking: true,
           f_list: this.props.f_list,
           startdisplay: 0, //rank of first facet to display... i.e offset by?
           //current_bin_position: -1,
           kind_of_doc_list: "summary_baseline",
           facet_datas: this.props.facet_datas,
           mode:"docs"};
  },

  //do you show a little x in the summary box status?
  show_x_for_t_in_sum_status: function(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    if (this.state.start_selected == min && this.state.end_selected == max){
      return false;
    }else{
      return true;
    }
  },

  resetT: function(){
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    min = min.format("YYYY-MM");
    max = max.format("YYYY-MM");
    this.setState({start_selected: min,
                  end_selected: max,
                  chart_mode: "intro"});

  },

  resultsToDocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list;
    }
    let start = moment(this.state.start_selected, "YYYY-MM");
    let end = moment(this.state.end_selected, "YYYY-MM");
    let out_results =  _.filter(results, function(value, key) {
        //dates come from server as YYYY-MM
        if (moment(value.pubdate, "YYYY-MM").isAfter(start) || moment(value.pubdate, "YYYY-MM").isSame(start)){
          if (moment(value.pubdate, "YYYY-MM").isBefore(end) || moment(value.pubdate, "YYYY-MM").isSame(end)){
            return true;
          }
        }
        return false;
    });
    return out_results;

  },

  n_fdocs: function(results){
    if (this.state.f != -1){
        results = this.state.f_list;
        return results.length;
    }else{
      return 0;
    }
  },

  mouse_move_in_chart: function(p){
    if (this.state.mouse_down_in_chart){
      if (this.state.drag_l == false && this.state.drag_r == false){
        let start = moment(p).format("YYYY-MM");
        let end = moment(p).format("YYYY-MM");
        if (start === end)
        this.setState({mouse_is_dragging: true,
                      drag_l: false,
                      drag_r: true,
                      mode: "docs",
                      start_selected: start,
                      end_selected: end});
      }
    }
  },

  /**
  * This function will fire on mousedown if chart is in rectangle mode
  */
  mouse_down_in_chart_true: function(d){
    this.setState({
      mouse_down_in_chart: true, mouse_is_dragging: true}, function(){
        if (this.state.drag_l == false && this.state.drag_r == false){
          this.set_dates(d, d);
        }
      });
  },

  /**
  * This function will fire on mouseup if chart is in rectangle mode
  */
  mouse_up_in_chart: function(e_page_X_adjusted){
    if (this.state.start_selected == -1 && this.state.end_selected == -1){
      let s = moment(e_page_X_adjusted).add(-1, 'month');
      let e = moment(e_page_X_adjusted).add(1, 'month');
      s = s.format("YYYY-MM");
      e = e.format("YYYY-MM");

      this.setState({start_selected:s,end_selected:e});
    }else{
      let url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + this.state.end_selected;

      let max = this.props.chart_bins[this.props.chart_bins.length - 1];


      if(this.state.start_selected === this.state.end_selected){
        if (moment(max) > moment(this.state.end_selected, "YYYY-MM")){
          let e = moment(this.state.end_selected, "YYYY-MM");
          e.add(1, "months");
          this.setState({end_selected:e.format("YYYY-MM")});
          url = this.props.base_url + "get_facets_t?q=" + this.props.q + "&corpus=" + this.props.corpus + "&startdate=" + this.state.start_selected + "&enddate=" + e.format("YYYY-MM");
        }
      }


    }

    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, mouse_is_dragging: false});
  },

  turnoff_drag: function(){
    this.setState({drag_l: false, drag_r: false,
                   mouse_down_in_chart: false, mouse_is_dragging: false});
  },

  /**
  * The chart will now have drag_l is true
  */
  toggle_drag_start_l: function(){
    this.setState({drag_l : true, mouse_is_dragging: true});
  },

  /**
  * The chart will now have drag_r is true
  */
  toggle_drag_start_r: function(){
    this.setState({drag_r : true, mouse_is_dragging: true});
  },

  /**
  * Set one of the dates: a start or end
  */
  set_date: function (date, start_end) {
    let d = moment(date);

    if (start_end == "start"){
      let end = moment(this.state.end_selected, "YYYY-MM");
      let min = moment(this.props.chart_bins[0]);
      if ((d < end) &  (d>min)){

        this.setState({start_selected:d.format("YYYY-MM")});

      }
    }
    if (start_end == "end"){
      let start = moment(this.state.start_selected, "YYYY-MM");

      let max = moment(this.props.chart_bins[this.props.chart_bins.length -1]);

      if (d > start & d < max){
         this.setState({end_selected:d.format("YYYY-MM")});
      }
    }
  },

  /**
  * Set both dates at once: start and end
  */
  set_dates: function (start_date, end_date) {
    let s = moment(start_date);
    let e = moment(end_date);
    let min = moment(this.props.chart_bins[0]);
    let max = moment(this.props.chart_bins[this.props.chart_bins.length - 1]);
    if (s <= e  & s > min & e < max & !(s.format("YYYY-MM") === e.format("YYYY-MM"))) {
      this.setState({start_selected:s.format("YYYY-MM"),
                     end_selected:e.format("YYYY-MM")});


    }else if (s <= e  & s > min & e < max & s.format("YYYY-MM") === e.format("YYYY-MM")){
        // dates are equal
        e.add(1, "months");
        if (e < max){
          this.setState({start_selected:s.format("YYYY-MM"),
                     end_selected:e.format("YYYY-MM")});
        }
    }else{
      //console.log("skip");
    }
  },

  /**
  * A clickhandler for sparkline tile
  */
  clickTile: function (e) {
    let url = this.props.base_url + "get_sents?q=" + this.props.q + "&f=" + e + "&corpus=" + this.props.corpus;
        let minbin = _.head(this.props.chart_bins);
        let maxbin = _.last(this.props.chart_bins);

  },

  /**
  * A handler for when user clicks the X by Q. Requery with F equal to Q
  */
  qX: function(){

  },

  /**
  * A handler for when user clicks the X by F. Adjust state so f=-1
  */
  fX: function(){

  },

  turn_on_rect_mode: function(p){
    this.setState({chart_mode:"rectangle",
                  start_selected:-1,
                  end_selected:-1,
                  mouse_down_in_chart:true,
                  mode: "docs"});
  },

  /**
  * Handle key press in the whole UI.

  TODO: QueryBar.jsx has its own click handler for enter key. should probably be moved here
  */
  handleKeyDown: function(e){
    if (this.state.start_selected != -1 && this.state.end_selected != -1){
      let new_end, new_start;
      let granularity = "weeks"; //TODO: this won't scale if span changes
      if (e.keyIdentifier == "Right" || e.keyIdentifier == "Left"){
          if(e.keyIdentifier == "Right"){
            new_start = moment(this.state.start_selected).add(1, granularity).format("YYYY-MM");
            new_end = moment(this.state.end_selected).add(1, granularity).format("YYYY-MM");
          }
          if(e.keyIdentifier == "Left"){
            new_start = moment(this.state.start_selected).subtract(1, granularity).format("YYYY-MM");
            new_end = moment(this.state.end_selected).subtract(1, granularity).format("YYYY-MM");
          }
          this.setState({start_selected:new_start, end_selected: new_end});




      }
    }
  },

  requery: function (arg) {

  },


  pageupdate: function(param){
      let tmp = param + this.state.summary_page;
      this.setState({summary_page:tmp});
  },

  /**
  make the status bar for the summary box
  */
  summary_status: function(){
    let docs = this.resultsToDocs(this.state.all_results);
    let show_x_for_t_in_sum_status = this.show_x_for_t_in_sum_status();
    let out = <SummaryStatus_tut resetT={this.resetT}
                                          show_x = {show_x_for_t_in_sum_status}
                                          kind_of_doc_list={this.state.kind_of_doc_list}
                                          ndocs={docs.length}
                                          q={this.props.q}
                                          f={this.state.f}
                                          q_color={q_color}
                                          f_color={f_color}
                                          static_mode={true}
                                          page={this.state.summary_page}
                                          pageupdate={this.pageupdate}
                                          turnOnSummary={() => this.setState({kind_of_doc_list: "summary_baseline"})}
                                          turnOnDoclist={() => this.setState({kind_of_doc_list: "no_summary"})}
                                          start_selected={this.state.start_selected}
                                          end_selected={this.state.end_selected}/>
    return out;
  },

  /**
  make the status bar for the sparkline panel
  */
  sparkline_status: function(){
      let backbutton = "";
      if (this.state.startdisplay > 0){
          backbutton = <span bsSize="xsmall">back</span>
      }
      let moresubjects = "";
       if ((this.state.startdisplay/this.props.sparkline_per_panel + 1) < (Math.floor(global_facets.length/this.props.sparkline_per_panel) + 1)){
          moresubjects = "more subjects"
      }
      return <div>
                     <SparklineStatus fX={this.fX} qX={this.qX}
                     ndocs={this.props.total_docs_for_q}
                     {...this.props}/>

                     <div style={{float:"right", marginTop: "-5px"}}>
                      <div style={{ height:"50%"}}>
                          <span style={{ float:"left",  height: "50%"}}>
                            {backbutton}
                          </span>
                          <span bsSize="xsmall">

                          </span>

                      </div>

                      </div>
                     </div>
  },

  close: function(){
    this.setState({still_looking: false});
  },


  onsubmit: function(e){
    window.location = "/staticr?current=task_screening&runid=" + this.props.runid + "&q=rookie&answer=NA"
  },
  update_selected_doc: function(d, pd){
    var url = "doc?corpus=" + this.props.corpus + "&docid=" + d;

    $.ajax({
                url: url,
                dataType: 'json',
                cache: true,
                method: 'GET',
                success: function(d) {
                  this.setState({selected_doc: d.docid,
                                selectedheadline: d.headline,
                                selectedpubdate: pd,
                                selectedsents: d.sents});

                }.bind(this),
                error: function(xhr, status, err) {
                  console.error(this.props.url, status, err.toString());
                }.bind(this)
    });
  },
  render: function() {
    {Modal}
    let docs = this.resultsToDocs(this.state.all_results);
    let docs_ignoreT = this.n_fdocs(this.state.all_results);
    let y_scroll = {
        overflowY: "scroll",
        height:this.props.height
    };
    let binned_facets = _.sortBy(this.props.binned_facets, function(item) {
        return parseInt(item.key);
    });
    let selected_binned_facets;

    let row_height = Math.floor(this.props.height/binned_facets.length);

    let main_panel;

    let chart_bins = this.props.chart_bins;
    let summary_status = this.summary_status();
    if (this.props.total_docs_for_q == 0 ){
        summary_status = "";
    }
    let chart_height = this.state.width / this.props.w_h_ratio;
    let query_bar_height = 50;
    let lower_h = (this.state.height - chart_height - query_bar_height)/2.5;

    let sparkline_h = this.sparkline_status();
    let end_facet_no = this.state.startdisplay + this.props.sparkline_per_panel


    main_panel = <Panel header={sparkline_h}>
                                   <SparklineGrid startdisplay={this.state.startdisplay}
                                   enddisplay={end_facet_no}
                                   width={this.state.width/2}
                                   height={lower_h}
                                   f={this.state.f}
                                   w_h_ratio={this.props.w_h_ratio}
                                   clickTile={this.clickTile}
                                   q_data={q_data} col_no={1}
                                   facet_datas={this.state.facet_datas}/>
                   </Panel>
    let chart;
    let docviewer = <DocViewer kind_of_doc_list={this.state.kind_of_doc_list}
                                height={lower_h + 50}
                                f={this.state.f}
                                mode={this.state.mode}
                                handleBinClick={this.handleBinClick}
                                start_selected={this.state.start_selected}
                                end_selected={this.state.end_selected}
                                all_results={this.state.all_results}
                                docs={docs}
                                runid={runid}
                                static_mode={true}
                                select={this.update_selected_doc}
                                page={this.state.summary_page}
                                per_page={this.props.docsperpage}
                                bins={binned_facets}/>
    if (this.props.total_docs_for_q > 0){
      let buffer = 5;
      chart = <Chart
               tooltip_width="160"
               turn_on_rect_mode={this.turn_on_rect_mode}
               mouse_move_in_chart={this.mouse_move_in_chart}
               f={this.state.f}
               q={this.props.q}
               turnoff_drag={this.turnoff_drag}
               handle_mouse_up_in_rect_mode={this.handle_mouse_up_in_rect_mode}
               toggle_both_drags_start={() => this.setState({drag_l: true, drag_r: true}) }
               toggle_drag_start_l={this.toggle_drag_start_l}
               toggle_drag_start_r={this.toggle_drag_start_r}
               drag_l={this.state.drag_l}
               drag_r={this.state.drag_r}
               w={this.state.width - this.props.y_axis_width - buffer}
               buffer={buffer}
               y_axis_width={this.props.y_axis_width}
               mode={this.state.mode}
               mouse_up_in_chart={this.mouse_up_in_chart}
               mouse_down_in_chart_true={this.mouse_down_in_chart_true}
               chart_mode={this.state.chart_mode}
               qX={this.qX} set_date={this.set_date}
               set_dates={this.set_dates}
               start_selected={this.state.start_selected}
               end_selected={this.state.end_selected}
               q_data={this.props.q_data}
               f_data={this.state.f_counts}
               belowchart="50"
               height={chart_height}
               keys={chart_bins}/>

    }else{
      chart = "";
    }
    let show_success;
    let question = "";
      let answers = ["In 1994, like in much of the 1990s, the United States encouraged Cubans to flee the communist government of President Fidel Castro for the U.S.",
                    "In 1994, the United States worked with the communist government of President Fidel Castro in Cuba to stop Cubans from leaving the island for the U.S.",
                    "I can't answer this from the resources provided."];
    if (this.state.start_selected === "1994-01" && this.state.end_selected === "1995-01" && this.state.drag_l === false && this.state.drag_r === false && this.state.still_looking){
        show_success = true;
    }else{
        show_success = false;
    }

    if (this.state.start_selected === "1994-01" && this.state.end_selected === "1995-01" && this.state.drag_l === false && this.state.drag_r === false){
        question = <Question start={this.props.start} onsubmit={this.onsubmit} answers={answers}/>
    }
    let selected_doc = '';
    if (this.state.selected_doc != -1){
        selected_doc = <Modal_doc show={true}
                        close={()=> this.setState({selected_doc: -1})}
                        headline={this.state.selectedheadline}
                        pubdate={this.state.selectedpubdate}
                        sents={this.state.selectedsents}/>
    }
    return(
        <div>
         <Modal show={this.state.show_2nd}/>
         {selected_doc}
         <Modal_success close={this.close} show={show_success}/>
       <Panel style={{'fontWeight': 'bold'}}>Use the slider to select January 1994 to January 1995</Panel>
             <Panel>
             <ChartTitle f_docs={docs_ignoreT}
                         q_color={q_color}
                         f_color={f_color}
                         chartMode={this.state.chart_mode}
                         fX={this.fX}
                         qX={this.qX}
                         static_mode={true}
                         ndocs={this.props.total_docs_for_q}
                         f={this.state.f}
                         requery={this.requery}
                         unf={this.fX}
                         mode={this.state.mode}
                         q={this.props.q}/>
             </Panel>
             {chart}
            <div style={{float:"left", width:(this.state.width-5)/2 }}>
              {question}
            </div>
            <div style={{float:"right", width:(this.state.width-5)/2 }}>
              <Panel header={summary_status}>
                <div>
                  {docviewer}
                </div>
              </Panel>
            </div>
       </div>
        );
  }
});
