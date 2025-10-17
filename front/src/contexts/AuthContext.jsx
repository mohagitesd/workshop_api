import { createContext, useState } from 'react';
import { setAuthToken } from '../api';

export const AuthContext = createContext({});

export function AuthProvider({ children }){

  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null }
  });

  // restore token into api module if exists
  try {
    const t = localStorage.getItem('token');
    if (t) setAuthToken(t);
  } catch(e){}

  const login = (userData, token) => {
    setUser(userData);
    setAuthToken(token);
    try { localStorage.setItem('user', JSON.stringify(userData)); localStorage.setItem('token', token); } catch(e){}
  };

  const logout = () => {
    setUser(null);
    setAuthToken(null);
    try { localStorage.removeItem('user'); localStorage.removeItem('token'); } catch(e){}
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
