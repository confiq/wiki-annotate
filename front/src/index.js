import React from 'react';
import ReactDOM from 'react-dom';
import 'semantic-ui-css/semantic.min.css'

import './style.css';
import Header from './components/layouts/Header';
import reportWebVitals from './reportWebVitals';
import { Container } from 'semantic-ui-react';

function App() {
  return (
    <Container fluid>
    <div className='App'>
      <Header />
      <div className='Content'>
        <p>42 is the answer to everything...</p>
      </div>
    </div>
    </Container>
  );
}
const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
