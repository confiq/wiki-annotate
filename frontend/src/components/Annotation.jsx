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
    return <AnnotationBody items={null} />;
  } else {
    return <AnnotationBody items={items} needRefresh={needRefresh} lastEdited={lastEdited} />;
  }
};

const AnnotationRow = ({ item, index }) => {
  const loading = !item;
  const users = loading ? ["user1, user2, user3"] : item.users;
  const joined = users.join(", ");

  return (
    <Table.Row className="table-row-users" key={loading ? "preload" : `#${index + 1}`}>
      <Table.Cell width="1" className="annotation-line-number" style={{ width: "3em" }}>
        {loading ? <Icon loading name="spinner" /> : index + 1}
      </Table.Cell>
      <Table.Cell width="3" style={{ maxWidth: 0, overflow: "hidden", width: "15%" }}>
        <Popup
          content={joined}
          disabled={loading || users.length <= 1}
          trigger={
            <div style={{
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
              cursor: !loading && users.length > 1 ? "help" : "default",
            }}>
              {joined}
            </div>
          }
          position="top center"
        />
      </Table.Cell>
      <Table.Cell className="annotation-text code">
        {loading
          ? <><Icon loading name="wait" /> loading…</>
          : item.annotated_text.map((element, index) => (
              <Popup
                key={`revision#${element[1].revid}/index:${index}`}
                content={`${element[1].user}:${element[1].revid}`}
                trigger={<div className="annotation-word">{element[0]}</div>}
                position="top center"
              />
            ))
        }
      </Table.Cell>
    </Table.Row>
  );
};

const AnnotationBody = ({ items, needRefresh, lastEdited }) => {
  const rows = items ? items.map((item, index) => (
    <AnnotationRow key={`#${index + 1}`} item={item} index={index} />
  )) : [<AnnotationRow key="preload" item={null} index={0} />];

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
        {rows}
      </Table.Body>
    </>
  );
};

const annotation = (parentState) => (
  <Container id="annotation">
    <Table celled fixed compact='very'>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell style={{ width: "3em" }}>#</Table.HeaderCell>
          <Table.HeaderCell style={{ width: "15%" }}>Authors</Table.HeaderCell>
          <Table.HeaderCell>Content</Table.HeaderCell>
        </Table.Row>
      </Table.Header>
      <Annotation parentState={parentState} />
    </Table>
  </Container>
);

export default annotation;
