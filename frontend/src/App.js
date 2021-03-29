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
    const url = process.env.REACT_APP_API_URL
    let wiki_url = window.location.href
    if (process.env.NODE_ENV === 'development') {
      wiki_url = wiki_url.replace('localhost:3000', process.env.REACT_APP_DEBUG_DOMAIN)
    }
    fetch(`${url}/v1/page_info/?url=${wiki_url}`)
      .then(res => res.json())
      .then(
        (result) => {
          this.setState({
            isLoaded: true,
            pageData: result
          });
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          this.setState({
            isLoaded: true,
            error
          })
        }
      )
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
      <div>
        <p>42 is the answer to everything...</p>
      </div>

    </Container>

    );
  }
}


//

// const PreLoad = () => (
//   <Table.Body>
//     <Table.Row>
//       <Table.Cell width="5">
//         <Icon loading name="spinner" />
//         {"user1, user2, user3"}
//       </Table.Cell>
//       <Table.Cell width="1" className="annotation-line-number">
//         1
//       </Table.Cell>
//       <Table.Cell>
//         <Icon loading name="wait" />
//         loading navigation...
//       </Table.Cell>
//     </Table.Row>
//   </Table.Body>
// );
