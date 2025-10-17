import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function Header() {
  const { user, logout } = useContext(AuthContext);

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="logo">Muséofile</Link>
        <nav className="main-nav">
          <Link to="/" className='nav-link'>Accueil</Link>
          <Link to="/favorites" className='nav-link'>Favoris</Link>
          {user ? (
            <button className='nav-link btn-primary' onClick={() => logout()}>Se déconnecter</button>
          ) : (
            <Link to="/login" className='nav-link btn-primary'>Connexion</Link>
          )}
        </nav>
      </div>
    </header>
  );
}
