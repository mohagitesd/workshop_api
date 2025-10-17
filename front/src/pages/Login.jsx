import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../api';

export default function Login(){
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      
      const payload = { username: email, password };
      const res = await fetch(`${API_URL}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Auth failed');
      const data = await res.json();
      const token = data.token || data.access_token;
      if (!token) throw new Error('No token returned');
      login({ email }, token);
      navigate('/');
    } catch (e) {
      alert('Erreur de connexion');
      console.error(e);
    }
  }

  return (
    <div className="login-page">
      <h1 className="login-title">Connexion</h1>
      <form onSubmit={handleSubmit} className="login-form">
        <label>
          <span>email</span>
          <input placeholder="" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>

        <label>
          <span>Mot de passe</span>
          <input placeholder="" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>

        <div style={{ display: 'flex', gap: 8 }}>
          <button type="submit" className="btn-primary">se connecter</button>
          <button type="button" onClick={() => navigate(-1)}>annuler</button>
        </div>
      </form>
    </div>
  )
}
