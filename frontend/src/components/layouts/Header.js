import React from "react";
import logo from "./logo.svg";
import "./Headers.css";

import { Container, Image, Menu } from "semantic-ui-react";

const header = () => (
  <Container fluid>
    <Menu inverted color="grey">
      <Container>
        <Menu.Item as="a" header href="/">
          <Image size="mini" src={logo} style={{ marginRight: "1.5em" }} />
          wiki blame
        </Menu.Item>
        <Menu.Item as="a" href="/">
          Home
        </Menu.Item>
        <Menu.Item as="a" href="/about">
          Whatever
        </Menu.Item>
      </Container>
    </Menu>
    <Container>
        TODO: make some nice html here
    </Container>
    {/* <Message icon style={{width: '1127px'}}>
      <Icon name="circle notched" loading />
      <Message.Content>
        <Message.Header>Just one second</Message.Header>
        We're fetching that content for you.
      </Message.Content>
    </Message> */}
  </Container>
);

export default header;
