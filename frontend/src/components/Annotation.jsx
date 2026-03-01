import { Container, Table, Icon, Popup, Message } from "semantic-ui-react";
import React, { useState, useEffect } from "react";

const POLL_INTERVAL_MS = 5000;

// Deterministic color from author name — used for the blame gutter strip
const AUTHOR_COLORS = [
  "#e57373", "#f06292", "#ba68c8", "#9575cd",
  "#7986cb", "#64b5f6", "#4fc3f7", "#4dd0e1",
  "#4db6ac", "#81c784", "#aed581", "#dce775",
  "#ffd54f", "#ffb74d", "#ff8a65", "#a1887f",
];

function authorColor(name) {
  if (!name) return "#ccc";
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return AUTHOR_COLORS[Math.abs(hash) % AUTHOR_COLORS.length];
}



const WordTooltip = ({ author, revid, onEnter, onLeave }) => (
  <div
    onMouseEnter={onEnter}
    onMouseLeave={onLeave}
    onClick={e => e.stopPropagation()}
    style={{
      position: "fixed",
      zIndex: 200,
      background: "#222",
      color: "#fff",
      borderRadius: 6,
      padding: "8px 12px",
      fontSize: "0.82em",
      lineHeight: 1.6,
      minWidth: 180,
      maxWidth: 260,
      boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
      pointerEvents: "all",
      whiteSpace: "normal",
      transform: "translate(-50%, calc(-100% - 8px))",
    }}
    ref={el => {
      if (el && window.__wordTooltipPos) {
        el.style.left = window.__wordTooltipPos.x + "px";
        el.style.top = window.__wordTooltipPos.y + "px";
      }
    }}
  >
    <strong>{author || "Unknown"}</strong>
    <div style={{ color: "#aaa", fontSize: "0.9em", marginTop: 2 }}>revision {revid}</div>
    {revid && (
      <div style={{ marginTop: 6 }}>
        <a
          href={`https://en.wikipedia.org/w/index.php?diff=${revid}`}
          target="_blank"
          rel="noreferrer"
          style={{ color: "#90caf9" }}
        >
          View diff →
        </a>
      </div>
    )}
  </div>
);

const revCache = {};

const WordSpan = ({ text, author, revid, color }) => {
  const [pos, setPos] = useState(null);
  const [revInfo, setRevInfo] = useState(null);
  const hideTimer = React.useRef(null);

  const fetchRevInfo = (id) => {
    if (!id || revCache[id] !== undefined) {
      setRevInfo(revCache[id] || null);
      return;
    }
    revCache[id] = null; // mark as fetching
    fetch(`https://en.wikipedia.org/w/api.php?action=query&revids=${id}&prop=revisions&rvprop=comment|timestamp&format=json&origin=*`)
      .then(r => r.json())
      .then(data => {
        const pages = data?.query?.pages || {};
        const page = Object.values(pages)[0];
        const rev = page?.revisions?.[0];
        const info = rev ? { comment: rev.comment, timestamp: rev.timestamp } : {};
        revCache[id] = info;
        setRevInfo(info);
      })
      .catch(() => { revCache[id] = {}; setRevInfo({}); });
  };

  React.useEffect(() => () => clearTimeout(hideTimer.current), []);

  const show = (e) => {
    clearTimeout(hideTimer.current);
    setPos({ x: e.clientX, y: e.clientY });
    fetchRevInfo(revid);
  };
  const hide = () => {
    hideTimer.current = setTimeout(() => setPos(null), 150);
  };
  const cancelHide = () => clearTimeout(hideTimer.current);

  return (
    <>
      <span
        className="annotation-word"
        onMouseEnter={show}
        onMouseMove={show}
        onMouseLeave={hide}
        style={{
          borderBottom: `2px solid ${color}`,
          backgroundColor: pos ? `${color}33` : "transparent",
          transition: "background-color 0.1s",
          cursor: "default",
        }}
      >{text}</span>
      {pos && (
        <div
          style={{ position: "fixed", left: pos.x, top: pos.y - 8, zIndex: 200, transform: "translate(-50%, -100%)", pointerEvents: "none" }}
        >
          <div style={{ pointerEvents: "all" }} onMouseEnter={cancelHide} onMouseLeave={hide}>
            <div style={{
              background: "#1e1e1e",
              color: "#fff",
              borderRadius: 6,
              padding: "8px 12px",
              fontSize: "0.82em",
              lineHeight: 1.5,
              width: 260,
              boxShadow: "0 4px 16px rgba(0,0,0,0.4)",
              whiteSpace: "normal",
            }}>
              {/* arrow */}
              <div style={{
                position: "absolute", bottom: -6, left: "50%", transform: "translateX(-50%)",
                width: 0, height: 0,
                borderLeft: "6px solid transparent",
                borderRight: "6px solid transparent",
                borderTop: "6px solid #1e1e1e",
              }} />
              <div style={{ fontWeight: "bold", color: color }}>{author || "Unknown"}</div>
              {revInfo?.timestamp && (
                <div style={{ color: "#888", fontSize: "0.88em" }}>
                  {new Date(revInfo.timestamp).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
                </div>
              )}
              {revInfo?.comment
                ? <div style={{ marginTop: 5, color: "#ccc", fontStyle: "italic", wordBreak: "break-word" }}>"{revInfo.comment.replace(/<[^>]+>/g, "").trim()}"</div>
                : <div style={{ color: "#555", marginTop: 4 }}>Loading…</div>
              }
              {revid && (
                <div style={{ marginTop: 7 }}>
                  <a href={`https://en.wikipedia.org/w/index.php?diff=${revid}`} target="_blank" rel="noreferrer" style={{ color: "#90caf9" }} onClick={e => e.stopPropagation()}>View diff →</a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const GUTTER_STYLE = {
  width: "3em",
  textAlign: "right",
  backgroundColor: "#f5f5f5",
  color: "#999",
  fontFamily: "monospace",
  userSelect: "none",
};

const AnnotationRow = ({ item, index }) => {
  const [expanded, setExpanded] = useState(false);
  const loading = !item;
  const users = loading
    ? ["user1, user2, user3"]
    : (item.users || []).map(u => (u == null || String(u).trim() === "" ? "Unknown" : String(u).trim())).sort((a, b) => a.localeCompare(b));
  const joined = users.join(", ");

  const primaryAuthor = loading ? null : (users[0] || null);
  const color = authorColor(primaryAuthor);

  // Collect unique, non-null revids for this line
  const revids = loading ? [] : item.annotated_text.map(e => e[1].revid).filter(r => r != null);
  const uniqueRevids = [...new Set(revids)];
  const revCount = uniqueRevids.length;
  const latestRevid = uniqueRevids.length > 0 ? Math.max(...uniqueRevids.map(r => Number(r))) : null;


  const [tooltipVisible, setTooltipVisible] = useState(false);
  const hideTimer = React.useRef(null);

  React.useEffect(() => () => clearTimeout(hideTimer.current), []);

  const showTooltip = () => {
    clearTimeout(hideTimer.current);
    setTooltipVisible(true);
  };
  const hideTooltip = () => {
    hideTimer.current = setTimeout(() => setTooltipVisible(false), 150);
  };

  return (
    <Table.Row className="table-row-users">
      <Table.Cell
        className="annotation-line-number"
        style={{ ...GUTTER_STYLE, borderLeft: `3px solid ${color}`, padding: 0, position: "relative", cursor: loading ? "default" : "help" }}
        onMouseEnter={!loading ? showTooltip : undefined}
        onMouseLeave={!loading ? hideTooltip : undefined}
      >
        <div style={{ padding: "2px 2px 2px 0" }}>
          {loading ? <Icon loading name="spinner" /> : index + 1}
        </div>
        {tooltipVisible && !loading && (
          <div
            onMouseEnter={showTooltip}
            onMouseLeave={hideTooltip}
            style={{
              position: "absolute",
              left: "calc(100% + 10px)",
              top: 0,
              zIndex: 100,
              background: "#222",
              color: "#fff",
              borderRadius: 6,
              padding: "8px 12px",
              fontSize: "0.82em",
              lineHeight: 1.6,
              minWidth: 180,
              maxWidth: 260,
              boxShadow: "0 4px 16px rgba(0,0,0,0.35)",
              pointerEvents: "all",
              whiteSpace: "normal",
            }}
          >
            {/* Arrow pointing left */}
            <div style={{
              position: "absolute",
              left: -6,
              top: 8,
              width: 0,
              height: 0,
              borderTop: "6px solid transparent",
              borderBottom: "6px solid transparent",
              borderRight: "6px solid #222",
            }} />
            <div style={{ color: "#aaa", fontSize: "0.85em", marginBottom: 4 }}>Line {index + 1}</div>
            <div><strong>{users.length > 1 ? `${users.length} authors` : primaryAuthor}</strong></div>
            {users.length > 1 && <div style={{ color: "#aaa", fontSize: "0.9em" }}>{joined}</div>}
            <div style={{ marginTop: 4 }}>{revCount} revision{revCount !== 1 ? "s" : ""} on this line</div>
            {latestRevid && (
              <div style={{ marginTop: 6 }}>
                <a
                  href={`https://en.wikipedia.org/w/index.php?diff=${latestRevid}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: "#90caf9" }}
                  onClick={e => e.stopPropagation()}
                >
                  View revision →
                </a>
              </div>
            )}
          </div>
        )}
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
      <Table.Cell
        className="annotation-text code"
        onClick={() => !loading && setExpanded(e => !e)}
        style={{ cursor: loading ? "default" : "pointer", position: "relative" }}
      >
        {loading
          ? <><Icon loading name="wait" /> loading…</>
          : <div style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              ...(!expanded && {
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
                overflow: "hidden",
              }),
            }}>
              {item.annotated_text.map((element, idx) => {
                const wordAuthor = element[1].user;
                const wordRevid = element[1].revid;
                const wordColor = authorColor(wordAuthor);
                return (
                  <WordSpan
                    key={`revision#${wordRevid}/index:${idx}`}
                    text={element[0]}
                    author={wordAuthor}
                    revid={wordRevid}
                    color={wordColor}
                  />
                );
              })}
            </div>
        }
      </Table.Cell>
    </Table.Row>
  );
};

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
        .then(async (res) => {
          if (!res.ok) {
            const json = await res.json().catch(() => ({}));
            throw new Error(json.error || json.detail || `HTTP ${res.status}`);
          }
          return res.json();
        })
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
        )
        .catch((err) => {
           setIsLoaded(true);
           setError(err);
        });
    };

    fetchAnnotation();
    return () => { if (pollTimer) clearTimeout(pollTimer); };
  }, []);

  const rows = !isLoaded
    ? Array.from({ length: 20 }, (_, i) => <AnnotationRow key={"preload-" + i} item={null} index={i} />)
    : (items || []).map((item, index) => <AnnotationRow key={`#${index + 1}`} item={item} index={index} />);

  return (
    <Container id="annotation">
      {error && <Message negative>Error: {error.message || String(error)}</Message>}
      {needRefresh && (
        <div style={{ position: "sticky", top: 0, zIndex: 10 }}>
          <Message icon info style={{ margin: 0, borderRadius: 0 }}>
            <Icon name="spinner" loading />
            <Message.Content>
              Loading more history… this may take a moment.
              {lastEdited && ` Current revision date: ${lastEdited}`}
            </Message.Content>
          </Message>
        </div>
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

export default Annotation;
