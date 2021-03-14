import React from "react";
import { Container } from 'semantic-ui-react';
import Header from './components/layouts/Header';

export default class App extends React.Component {
  render() {
    return (
    <Container fluid>
      <Header />
      <div className='Content'>
        <p>42 is the answer to everything...</p>
      </div>

    </Container>

    );
  }
}
