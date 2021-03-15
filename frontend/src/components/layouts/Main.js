import {
  Container,
  Segment,
  Dimmer,
  Loader,
  Grid,
  Placeholder,
  Table,
  Icon,
} from "semantic-ui-react";
// import { Button, Divider, Form, Grid, Segment } from 'semantic-ui-react'


const main = () => (
  <Container id="main">
    <Segment raised>
      <PreLoad />
    </Segment>
  </Container>
);


const PreLoad = () => (
  <Table celled fixed>
    <Table.Header>
      <Table.Row>
        <Table.HeaderCell colSpan='3'> <Icon loading name='spinner' />{'page_name'}</Table.HeaderCell>
      </Table.Row>
    </Table.Header>

    <Table.Body>
      <Table.Row className='annotation_text'>
        <Table.Cell width="1">
        <Icon loading name='spinner' />{'user1, user2, user3'}
        </Table.Cell>
        <Table.Cell>1</Table.Cell>
        <Table.Cell>
        <Icon loading name='wait' />wiki_content
        </Table.Cell>
      </Table.Row>
      {/* <Table.Row>
        <Table.Cell>
          <Icon name='folder' /> test
        </Table.Cell>
        <Table.Cell>Initial commit</Table.Cell>
        <Table.Cell textAlign='right'>10 hours ago</Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          <Icon name='folder' /> build
        </Table.Cell>
        <Table.Cell>Initial commit</Table.Cell>
        <Table.Cell textAlign='right'>10 hours ago</Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          <Icon name='file outline' /> package.json
        </Table.Cell>
        <Table.Cell>Initial commit</Table.Cell>
        <Table.Cell textAlign='right'>10 hours ago</Table.Cell>
      </Table.Row>
      <Table.Row>
        <Table.Cell>
          <Icon name='file outline' /> Gruntfile.js
        </Table.Cell>
        <Table.Cell>Initial commit</Table.Cell>
        <Table.Cell textAlign='right'>10 hours ago</Table.Cell>
      </Table.Row> */}
    </Table.Body>
  </Table>
)

export default main;
