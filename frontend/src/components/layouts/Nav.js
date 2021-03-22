import {
  Container,
  Segment,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React from "react";

class Navigation extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      pageName: <><Icon loading name="spinner" />loading...</>
    }
  }
render() {
  
  return (
  <Container id="navigation">
    <Segment.Group horizontal id="header-diff">
      <Segment textAlign="left">
        <Icon name="file" />
        <span className="wiki_page_title">{this.state.pageName}</span>
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
