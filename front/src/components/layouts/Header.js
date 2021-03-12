import "./Headers.css";
import logo from './logo.svg';

export default function Header() {
    
    return (
      <header className="Header">
        <img src={logo} className="App-logo" alt="logo" class="logo" />
        <nav className="Nav">
          <a href="/">Home</a>
          <a href="/">Articles</a>
          <a href="/About">About 🎳</a>
        </nav>
      </header>
    );
  }
