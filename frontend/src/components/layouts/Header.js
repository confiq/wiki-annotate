import React from "react";
import "./Headers.css";

import { Container, Icon, Menu } from "semantic-ui-react";

const header = () => (
  <Container>
    <Menu inverted color="grey">
      <Container>
        <Menu.Item as="a" header href="/">
        <Icon name='plus' color='black'/>
          <Icon.Group >
        <Icon disabled name='plus' color='black'/>
        <Icon disabled name='minus' color='red'/>
        </Icon.Group>
        <Icon disabled name='minus' color='red'/>
          <b>wiki blame</b>
        </Menu.Item>
        <Menu.Item as="a" href="/">
          Home 🏚
        </Menu.Item>
        <Menu.Item as="a" href="/about">
          About 📡
        </Menu.Item>
      </Container>
    </Menu>
  </Container>
);

export default header;
