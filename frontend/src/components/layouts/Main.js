import {
  Container,
  Segment,
  Table,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React, { useState, useEffect } from "react";


const MainComponent = () => {
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
    return (<PreLoad/>);
  } else {    
    return (
      <Table.Body>
        {items.map((item, index) => (
              <Table.Row key={index} className="table-row-users">
              <Table.Cell width="5">
                <ul className="annotation-users">
                {item.users.map(element =>(
                  <li>{element}</li>
                ))}
                </ul>
              </Table.Cell>
              <Table.Cell width="1">{index+1}</Table.Cell>
              <Table.Cell className='annotation-text code'>
                {item.annotated_text.map(((element,index) => (
                  <div key={`revision#${element[1].revid}/index:${index}`} className='annotation-word' user={element[1].user} revid={element[1].revid}>{element[0]}</div>
                )))}
              </Table.Cell>
            </Table.Row>
        )
        )}
      </Table.Body>
    )
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
    <Container id="annotation">
    <Table celled fixed>
      <MainComponent />
    </Table>
    </Container>
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
        loading content...
      </Table.Cell>
    </Table.Row>
  </Table.Body>
);

export default content;
