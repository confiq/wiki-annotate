import React from 'react'
import logo from './logo.svg'
import './Headers.css'

import {
  Container,
  Image,
  Menu,
} from 'semantic-ui-react'

const FixedMenuLayout = () => (
    <Menu fixed='top' inverted color='grey'>
      <Container>
        <Menu.Item as='a' header href='/'>
          <Image size='mini' src={logo} style={{ marginRight: '1.5em' }} />
          wiki blame
        </Menu.Item>
        <Menu.Item as='a' href='/'>Home</Menu.Item>
        <Menu.Item as='a' href='/about'>Whatever</Menu.Item>
      </Container>
    </Menu>
)

export default FixedMenuLayout
