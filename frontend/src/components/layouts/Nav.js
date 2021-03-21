import {
  Container,
  Segment,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React from "react";


const navigation = () => (
  <Container id="navigation">
    <Segment.Group horizontal id="header-diff">
      <Segment textAlign="left">
        <Icon loading name="spinner" />
        <Icon name="file" />
        <b>{"page_name"}</b>
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
);



export default navigation;
