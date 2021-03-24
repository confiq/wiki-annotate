import { Container, Table, Icon } from "semantic-ui-react";

const MainComponent = ({ items }) => {
    return (
      <Table.Body>
        {items.map((item, index) => (
          <Table.Row className="table-row-users" key={`#${index + 1}`}>
            <Table.Cell width="5">
              <ul className="annotation-users">
                {item.users.map((element, index) => (
                  <li key={`idontunderstandreact${item.annotated_text.revid}/${element}`}>{element}</li>
                ))}
              </ul>
            </Table.Cell>
            <Table.Cell width="1" className="annotation-line-number">
              {index + 1}
            </Table.Cell>
            <Table.Cell className="annotation-text code">
              {item.annotated_text.map((element, index) => (
                <div key={`revision#${element[1].revid}/index:${index}`} className="annotation-word" user={element[1].user} revid={element[1].revid} >
                  {element[0]}
                </div>
              ))}
            </Table.Cell>
          </Table.Row>
        ))}
      </Table.Body>
    );
  }


const main = ({items}) => (
  <Container id="annotation">
    <Table celled fixed>
      <MainComponent items={items} />
    </Table>
  </Container>
)
export default main;
