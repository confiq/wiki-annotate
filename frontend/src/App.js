import React from "react";
import { Container } from 'semantic-ui-react';
import Header from './components/layouts/Header';
import Main from './components/layouts/Main'
export default class App extends React.Component {
  render() {
    return (
    <Container fluid>
      <Header />
      <Main />
      <div>
        <p>42 is the answer to everything...</p>
      </div>

    </Container>

    );
  }
}
