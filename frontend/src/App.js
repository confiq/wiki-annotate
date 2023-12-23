import React from "react";
import { Container, Message } from 'semantic-ui-react';
import Annotation from "./components/Annotation";
import Header from './components/layouts/Header';
import Nav from './components/layouts/Nav'


export default class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      error: null,
      isLoaded: false,
      pageData: {}
    };
  }

  componentDidMount() {
    // TODO: this should be function
    // const url = process.env.REACT_APP_API_URL
    // let wiki_url = window.location.href
    // if (process.env.NODE_ENV === 'development') {
    //   wiki_url = wiki_url.replace('localhost:3000', process.env.REACT_APP_DEBUG_DOMAIN)
    // }
    // fetch(`${url}/v1/page_info/?url=${wiki_url}`)
    //   .then(res => res.json())
    //   .then(
    //     (result) => {
    //       this.setState({
    //         isLoaded: true,
    //         pageData: result
    //       });
    //     },
    //     // Note: it's important to handle errors here
    //     // instead of a catch() block so that we don't swallow
    //     // exceptions from actual bugs in components.
    //     (error) => {
    //       this.setState({
    //         isLoaded: true,
    //         error
    //       })
    //     }
    //   )
    };

  render() {
    return (
    <Container fluid>
      <Header />
       {/* when we use router, move continer to somewhere else */}
       <Container id='container_annotation'>
       <Message hidden>You can't see me</Message>
        <Nav pageName={this.state.pageData.page_title} isLoaded={this.state.isLoaded} />        
        <Annotation parentState={this.state} />
      </Container>
      <Container>
      <div style={{ textAlign: "center"}}>
        <p>Made with ❤️ and 😓. See how you can help: <a href="https://github.com/confiq/wiki-annotate">wiki-annotate</a> </p>
      </div>
      </Container>
    </Container>

    );
  }
}
