import { Container, Table, Icon, Popup } from "semantic-ui-react";
import React, { useState, useEffect } from "react";

const Annotation = (parentState) => {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [items, setItems] = useState([]);

  // Note: the empty deps array [] means
  // this useEffect will run once
  // similar to componentDidMount()
  useEffect(() => {
    // api.fetchData();
    const url = process.env.REACT_APP_API_URL;
    let wiki_url = window.location.href;
    if (process.env.NODE_ENV === "development") {
      wiki_url = wiki_url.replace(
        "localhost:3000",
        process.env.REACT_APP_DEBUG_DOMAIN
      );
    }
    
    fetch(`${url}/v1/page_annotation/?url=${wiki_url}`)
    .then((res) => res.json())
    .then(
        (result) => {
          setIsLoaded(true);
          setItems(result.text);
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
    console.log(parentState)
    return <PreLoad />;
  } else {
    return <MainAnnotation items={items} />;
  }
  
};

const MainAnnotation = ({ items }) => {
  return (
    <Table.Body>
      {items.map((item, index) => (
        <Table.Row className="table-row-users" key={`#${index + 1}`}>
          <Table.Cell width="5">
            <ul className="annotation-users">
              {item.users.map((element, index) => (
                <li
                  key={`idontunderstandreact${item.annotated_text.revid}/${element}`}
                >
                  {element}
                </li>
              ))}
            </ul>
          </Table.Cell>
          <Table.Cell width="1" className="annotation-line-number">
            {index + 1}
          </Table.Cell>
          <Table.Cell className="annotation-text code">
            {item.annotated_text.map((element, index) => (
              <Popup
                key={`revision#${element[1].revid}/index:${index}`}
                content={`${element[1].user}:${element[1].revid}`}
                trigger={<div className="annotation-word">{element[0]}</div>}
                position="top center"
              />
            ))}
          </Table.Cell>
        </Table.Row>
      ))}
    </Table.Body>
  );
};
const PreLoad = () => (
  <Table.Body>
    <Table.Row>
      <Table.Cell width="5">
        <Icon loading name="spinner" />
        {"user1, user2, user3"}
      </Table.Cell>
      <Table.Cell width="1" className="annotation-line-number">
        1
      </Table.Cell>
      <Table.Cell>
        <Icon loading name="wait" />
        loading navigation...
      </Table.Cell>
    </Table.Row>
  </Table.Body>
);

const annotation = (parentState) => (
  <Container id="annotation">
    <Table celled fixed  compact='very'>
      <Annotation parentState={parentState} />
    </Table>
  </Container>
);

export default annotation;
