import React, { useState, useEffect } from "react";
import { Container, Message } from 'semantic-ui-react';
import Annotation from "./components/Annotation";
import Header from './components/layouts/Header';
import Nav from './components/layouts/Nav';

export default function App() {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [pageData, setPageData] = useState({});

  useEffect(() => {
    const url = import.meta.env.VITE_API_URL;
    let wiki_url = window.location.href;
    if (import.meta.env.MODE === 'development') {
      wiki_url = wiki_url.replace('localhost:3000', import.meta.env.VITE_DEBUG_DOMAIN);
    }
    fetch(`${url}/v1/page_info/?url=${wiki_url}`)
      .then(res => res.json())
      .then(
        (result) => {
          setIsLoaded(true);
          setPageData(result);
        },
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      );
  }, []);

  return (
    <Container fluid>
      <Header />
      <Container id='container_annotation'>
        <Message hidden>You can't see me</Message>
        <Nav pageName={pageData.page_title} isLoaded={isLoaded} />
        <Annotation error={error} isLoaded={isLoaded} pageData={pageData} />
      </Container>
      <Container>
        <div style={{ textAlign: "center" }}>
          <p>Made with ❤️ and 😓. See how you can help: <a href="https://github.com/confiq/wiki-annotate">wiki-annotate</a></p>
        </div>
      </Container>
    </Container>
  );
}
