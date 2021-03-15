//inspired from https://stackblitz.com/edit/react-vrtngq
import React from 'react';
import ReactDOM from 'react-dom';
import 'semantic-ui-css/semantic.min.css'
import './style.css';
import App from './App'
const history = require("history").createBrowserHistory

const render = App =>
  ReactDOM.render(
    <App history={history}/>
    ,
    document.getElementById('root')
  )

render(App)
