import React from 'react';
import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="logo">Muséofile</Link>
        <nav className="main-nav">
          <Link to="/" className='nav-link'>Accueil</Link>
          <Link to="/favorites" className='nav-link'>Favoris</Link>
         
        </nav>
      </div>
    </header>
  );
}
