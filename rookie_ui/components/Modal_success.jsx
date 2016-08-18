"use strict";
/*
A result in a normal IR system 
*/

var React = require('react');

var Modal = require('react-bootstrap/lib/Modal');
var Button = require('react-bootstrap/lib/Button');

module.exports = React.createClass({

getInitialState() {

    let a = this.props.show;
    return { showModal: a };
  },

  close() {
    this.props.close();
  },

  render() {

    return (
      <div >
        <Modal backdrop="static" show={this.props.show} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>You got it!</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            Good job! See how the box in the bottom right of the screen now shows what <span style={{color: "#0028a3", fontWeight: "bold"}}>Hamid Karzai</span> has to do with <span style={{color: "#b33125", fontWeight: "bold"}}>Pervez Musharraf</span> from <b>January 2003</b> to <b>January 2004?</b>

          </Modal.Body>
          <Modal.Footer>
            <Button onClick={this.close}>Yep. I see that in the bottom right of the screen.</Button>
          </Modal.Footer>
        </Modal>
      </div>
    );
  }

});
