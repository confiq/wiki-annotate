import {
  Container,
  Segment,
  Table,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React, { useState, useEffect } from "react";

function Main() {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [items, setItems] = useState([]);

  // Note: the empty deps array [] means
  // this useEffect will run once
  // similar to componentDidMount()
  useEffect(() => {
    fetch("http://localhost:3000/demo_data.json")
      .then((res) => res.json())
      .then(
        (result) => {
          setIsLoaded(true);
          setItems(result);
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      );
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  } else if (!isLoaded) {
    return PreLoad;
  } else {
    
    return (
      <Table.Body>
        {items.map((item) => (
              <Table.Row>
              <Table.Cell width="5">
                {item.users}
              </Table.Cell>
              <Table.Cell width="1">1</Table.Cell>
              <Table.Cell>
                {items.item.forEach(element => {
                  console.log(element)
                })}
              </Table.Cell>
            </Table.Row>
          // <li key={item.id}>
          //   {item.name} {item.price}
          // </li>
        )
        )}
      </Table.Body>
    );
  }
}
const content = () => (
  <Container id="main">
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
    <Table celled fixed id="annotation">
      <Main />
    </Table>
  </Container>
);

const PreLoad = () => (
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
      <Table.Cell>user2</Table.Cell>
      <Table.Cell>2</Table.Cell>
      <Table.Cell>[table]</Table.Cell>
    </Table.Row>
    <Table.Row>
      <Table.Cell>user2</Table.Cell>
      <Table.Cell>3</Table.Cell>
      <Table.Cell>hello world</Table.Cell>
    </Table.Row>
    <Table.Row>
      <Table.Cell>user3</Table.Cell>
      <Table.Cell>4</Table.Cell>
      <Table.Cell></Table.Cell>
    </Table.Row>
    <Table.Row>
      <Table.Cell>user2</Table.Cell>
      <Table.Cell>5</Table.Cell>
      <Table.Cell>[/table]</Table.Cell>
    </Table.Row>
  </Table.Body>
);

export default content;
