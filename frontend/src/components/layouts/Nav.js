import {
  Container,
  Segment,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React from "react";

class Navigation extends React.Component {
  
render() {
  const pageName = <><Icon loading name="spinner" />loading...</>
  return (
  <Container id="navigation">
    <Segment.Group horizontal id="header-diff">
      <Segment textAlign="left">
        <Icon name="file" />
        <span className="page_title">{pageName}</span>
      </Segment>
      <Segment textAlign="right">
        <Button>source</Button>
        <Button disabled>rendered</Button>
        <Label color="grey" floating size="tiny">
          TODO
        </Label>
      </Segment>
    </Segment.Group>
  </Container>
  )}
  }



export default Navigation;
