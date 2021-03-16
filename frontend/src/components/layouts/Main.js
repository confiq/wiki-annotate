import {
  Container,
  Segment,
  Table,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";

const main = () => (
  <Container id="main">
      <Segment.Group horizontal id="header-diff">
        <Segment textAlign="left">
        <Icon loading name="spinner" /><Icon name="file" />
        <b>{"page_name"}</b>
        </Segment>
        <Segment textAlign="right">
          <Button>source</Button>
          <Button disabled>rendered</Button><Label color="yellow" floating size="tiny">todo</Label>
        </Segment>
      </Segment.Group>
      <PreLoad />
  </Container>
);

const PreLoad = () => (
  <Table celled fixed id="annotation">

    <Table.Body>
      <Table.Row className="annotation_text">
        <Table.Cell width="5">
          <Icon loading name="spinner" />
          {"user1, user2, user3"}
        </Table.Cell>
        <Table.Cell width="1">1</Table.Cell>
        <Table.Cell>
          <Icon loading name="wait" />
          wiki_content
        </Table.Cell>
      </Table.Row>
    </Table.Body>
  </Table>
);

export default main;
