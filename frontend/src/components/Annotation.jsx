import { Container, Table, Icon, Popup } from "semantic-ui-react";
import React, { useState, useEffect } from "react";

const POLL_INTERVAL_MS = 5000;

const Annotation = (parentState) => {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [items, setItems] = useState([]);
  const [needRefresh, setNeedRefresh] = useState(false);
  const [lastEdited, setLastEdited] = useState(null);

  useEffect(() => {
    let pollTimer = null;

    const fetchAnnotation = () => {
      const url = import.meta.env.VITE_API_URL;
      let wiki_url = window.location.href;
      if (import.meta.env.MODE === "development") {
        wiki_url = wiki_url.replace(
          "localhost:3000",
          import.meta.env.VITE_DEBUG_DOMAIN
        );
      }

      fetch(`${url}/v1/page_annotation/?url=${wiki_url}`)
        .then((res) => res.json())
        .then(
          (result) => {
            setIsLoaded(true);
            setItems(result.text);
            setNeedRefresh(result.need_refresh);
            setLastEdited(result.last_edited || null);
            if (result.need_refresh) {
              pollTimer = setTimeout(fetchAnnotation, POLL_INTERVAL_MS);
            }
          },
          (error) => {
            setIsLoaded(true);
            setError(error);
          }
        );
    };

    fetchAnnotation();
    return () => { if (pollTimer) clearTimeout(pollTimer); };
  }, []);

  if (error) {
    return <div>Error: {error.message}</div>;
  } else if (!isLoaded) {
    return <PreLoad />;
  } else {
    return <MainAnnotation items={items} needRefresh={needRefresh} lastEdited={lastEdited} />;
  }
};

const UsersCell = ({ users }) => {
  const joined = users.join(", ");
  return (
    <Table.Cell width="3" style={{ maxWidth: 0, overflow: "hidden" }}>
      <Popup
        content={joined}
        disabled={users.length <= 1}
        trigger={
          <div style={{
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            cursor: users.length > 1 ? "help" : "default",
          }}>
            {joined}
          </div>
        }
        position="top center"
      />
    </Table.Cell>
  );
};

const MainAnnotation = ({ items, needRefresh, lastEdited }) => {
  return (
    <>
      {needRefresh && (
        <Table.Body>
          <Table.Row>
            <Table.Cell colSpan="3" textAlign="center">
              <Icon loading name="spinner" /> Loading more history… this may take a moment.{lastEdited && ` Current revision date: ${lastEdited}`}
            </Table.Cell>
          </Table.Row>
        </Table.Body>
      )}
      <Table.Body>
      {items.map((item, index) => (
        <Table.Row className="table-row-users" key={`#${index + 1}`}>
          <Table.Cell width="1" className="annotation-line-number">
            {index + 1}
          </Table.Cell>
          <UsersCell users={item.users} />
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
    </>
  );
};

const PreLoad = () => (
  <Table.Body>
    <Table.Row>
      <Table.Cell width="1" className="annotation-line-number">
        1
      </Table.Cell>
      <Table.Cell width="3" style={{ maxWidth: 0, overflow: "hidden" }}>
        <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          <Icon loading name="spinner" />
          user1, user2, user3
        </div>
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
    <Table celled fixed compact='very'>
      <Annotation parentState={parentState} />
    </Table>
  </Container>
);

export default annotation;
