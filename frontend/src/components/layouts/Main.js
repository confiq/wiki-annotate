import {
  Container,
  Segment,
  Dimmer,
  Loader,
  Grid,
  Placeholder,
} from "semantic-ui-react";
// import { Button, Divider, Form, Grid, Segment } from 'semantic-ui-react'


const main = () => (
  <Container id="main">
    <Segment raised>
      <PreLoad />
    </Segment>
  </Container>
);


const PreLoad = () => 
<Grid columns={2} relaxed="very" stackable>
<Grid.Column>
  <Dimmer active inverted>
    <Loader inverted>Loading users</Loader>
  </Dimmer>
  <Placeholder>
    <Placeholder.Paragraph>
      <Placeholder.Line />
      <Placeholder.Line />
      <Placeholder.Line />
      <Placeholder.Line />
    </Placeholder.Paragraph>
  </Placeholder>
</Grid.Column>

<Grid.Column>
  <Dimmer active inverted>
    <Loader inverted>Loading data</Loader>
  </Dimmer>

  <Placeholder>
    <Placeholder.Paragraph>
      <Placeholder.Line />
      <Placeholder.Line />
      <Placeholder.Line />
      <Placeholder.Line />
    </Placeholder.Paragraph>
  </Placeholder>
</Grid.Column>
</Grid>

export default main;
