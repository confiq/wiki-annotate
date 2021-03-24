import {
  Container,
  Segment,
  Label,
  Icon,
  Button,
} from "semantic-ui-react";
import React from "react";

const Loader = () => <><Icon loading name="spinner" />loading...</>;

const Navigation = ({pageName, isLoading = false}) => {
  const renderPageName = () => {
    if (isLoading) return <Loader />;
    return pageName;
  }

  return (
    <Container id="navigation">
      <Segment.Group horizontal id="header-diff">
        <Segment textAlign="left">
          <Icon name="file" />
          <span className="wiki_page_title">{renderPageName()}</span>
        </Segment>
        <Segment textAlign="right">
          <Button>source</Button>
          <Button disabled>rendered</Button>
          <Label color="grey" floating size="tiny">
            TODO
          </Label>
        </Segment>
      </Segment.Group>
    </Container>
  )};




export default Navigation;
