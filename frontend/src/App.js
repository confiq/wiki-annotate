import React from "react";
import { Container } from 'semantic-ui-react';
import Annotation from "./components/Annotation";
import Header from './components/layouts/Header';
import Nav from './components/layouts/Nav'


export default class App extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      page_info: {
        firstUser: 'wtf',
        isLoaded: true
      }
    }
  }
  render() {
    return (
    <Container fluid>
      <Header />
       {/* when we use router, move continer to somewhere else */}
       <Container id='container_annotation'>
        <Nav pageName={this.state.page_info.firstUser} isLoading={this.state.page_info.isLoaded}/>
        <Annotation />
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
