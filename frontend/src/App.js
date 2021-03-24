import React, { useState, useEffect } from "react";
import { Container } from 'semantic-ui-react';
import Header from './components/layouts/Header';
import Nav from './components/layouts/Nav'
import Main from './components/Main'
const LoadInitData = () => {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [items, setItems] = useState([]);
  const [firstUser, setUser] = useState(null)

  // Note: the empty deps array [] means
  // this useEffect will run once
  // similar to componentDidMount()
  useEffect(() => {
    // api.fetchData();
    const apiURL = 'localhost:3000' //process.env.REACT_APP_API_URL
    fetch(`http://${apiURL}/demo_data.json`)
      .then((res) => res.json())
      .then(
        (result) => {
          setIsLoaded(true);
          setItems(result);
          setUser(result[0].users[0])
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {
          setIsLoaded(true);
          setError(error);
        }
      );
  }, [])

  
    if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return 'loading';
    } else {
    return <Main items={items}/>
  }
};

export default class App extends React.Component {
  render() {
    return (
    <Container fluid>
      <Header />
      <Nav pageName={LoadInitData.firstUser} isLoading={LoadInitData.isLoading}/>
        <LoadInitData/>
      <div>
        <p>42 is the answer to everything...</p>
      </div>

    </Container>

    );
  }
}


//

// const PreLoad = () => (
//   <Table.Body>
//     <Table.Row>
//       <Table.Cell width="5">
//         <Icon loading name="spinner" />
//         {"user1, user2, user3"}
//       </Table.Cell>
//       <Table.Cell width="1" className="annotation-line-number">
//         1
//       </Table.Cell>
//       <Table.Cell>
//         <Icon loading name="wait" />
//         loading navigation...
//       </Table.Cell>
//     </Table.Row>
//   </Table.Body>
// );
