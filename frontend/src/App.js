import React from "react";
import { Container } from 'semantic-ui-react';
import Header from './components/layouts/Header';
import Nav from './components/layouts/Nav'
import Main from './components/Main'
export default class App extends React.Component {
  render() {
    return (
    <Container fluid>
      <Header />
      <Nav />
      <Main />
      <div>
        <p>42 is the answer to everything...</p>
      </div>

    </Container>

    );
  }
}
