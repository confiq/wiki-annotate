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
          <Button disabled>rendered</Button><Label color="grey" floating size="tiny">TODO</Label>
        </Segment>
      </Segment.Group>
      <PreLoad />
  </Container>
);

const PreLoad = () => (
  <Table celled fixed id="annotation">

    <Table.Body>
      <Table.Row>
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
      <Table.Row>
        <Table.Cell>
          user2
        </Table.Cell>
        <Table.Cell>2</Table.Cell>
        <Table.Cell>[table]</Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          user2
        </Table.Cell>
        <Table.Cell>3</Table.Cell>
        <Table.Cell>hello world</Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          user3
        </Table.Cell>
        <Table.Cell>4</Table.Cell>
        <Table.Cell></Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          user2
        </Table.Cell>
        <Table.Cell>5</Table.Cell>
        <Table.Cell >[/table]</Table.Cell>
      </Table.Row>
    </Table.Body>
  </Table>
);

export default main;
