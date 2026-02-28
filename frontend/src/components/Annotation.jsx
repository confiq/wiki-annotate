import { Container, Table, Icon, Popup, Message } from "semantic-ui-react";
import React, { useState, useEffect } from "react";

const POLL_INTERVAL_MS = 5000;

const GUTTER_STYLE = {
  width: "3em",
  textAlign: "right",
  backgroundColor: "#f5f5f5",
  color: "#999",
  fontFamily: "monospace",
  userSelect: "none",
};

const AnnotationRow = ({ item, index }) => {
  const loading = !item;
  const users = loading ? ["user1, user2, user3"] : item.users;
  const joined = users.join(", ");

  return (
    <Table.Row className="table-row-users">
      <Table.Cell className="annotation-line-number" style={GUTTER_STYLE}>
        {loading ? <Icon loading name="spinner" /> : index + 1}
      </Table.Cell>
      <Table.Cell style={{ maxWidth: 0, overflow: "hidden", width: "15%" }}>
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
      <Table.Cell className="annotation-text code" style={{ overflow: "hidden" }}>
        {loading
          ? <><Icon loading name="wait" /> loading…</>
          : <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {item.annotated_text.map((element, idx) => (
                <Popup
                  key={`revision#${element[1].revid}/index:${idx}`}
                  content={`${element[1].user}:${element[1].revid}`}
                  trigger={<span className="annotation-word">{element[0]}</span>}
                  position="top center"
                />
              ))}
            </div>
        }
      </Table.Cell>
    </Table.Row>
  );
};

const annotation = (parentState) => {
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
          (err) => {
            setIsLoaded(true);
            setError(err);
          }
        );
    };

    fetchAnnotation();
    return () => { if (pollTimer) clearTimeout(pollTimer); };
  }, []);

  const rows = isLoaded && !error
    ? items.map((item, index) => <AnnotationRow key={`#${index + 1}`} item={item} index={index} />)
    : [<AnnotationRow key="preload" item={null} index={0} />];

  return (
    <Container id="annotation">
      {error && <Message negative>Error: {error.message}</Message>}
      {needRefresh && (
        <Message icon info>
          <Icon name="spinner" loading />
          <Message.Content>
            Loading more history… this may take a moment.
            {lastEdited && ` Current revision date: ${lastEdited}`}
          </Message.Content>
        </Message>
      )}
      <Table celled fixed compact='very'>
        <Table.Header>
          <Table.Row>
            <Table.HeaderCell style={{ ...GUTTER_STYLE, color: "#555" }}>#</Table.HeaderCell>
            <Table.HeaderCell style={{ width: "15%" }}>Authors</Table.HeaderCell>
            <Table.HeaderCell>Content</Table.HeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {rows}
        </Table.Body>
      </Table>
    </Container>
  );
};

export default annotation;
