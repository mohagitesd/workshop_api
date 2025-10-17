export const API_URL = "http://127.0.0.1:8000";

let authToken = null;
export function setAuthToken(token) {
  authToken = token;
}

function authHeaders(extra = {}){
  const base = {};
  if (authToken) base['Authorization'] = `Bearer ${authToken}`;
  return { ...base, ...extra };
}

export async function fetchMuseums(filters = {}) {
  const params = new URLSearchParams(filters);
  const res = await fetch(`${API_URL}/museums?${params}`, { headers: authHeaders() });
  return res.json();
}

export async function fetchFavorites() {
  const res = await fetch(`${API_URL}/favorites`, { headers: authHeaders() });
  return res.json();
}

export async function addFavorite(fav) {
  const res = await fetch(`${API_URL}/favorites`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(fav),
  });
  return res.json();
}

export async function removeFavorite(id) {
  const res = await fetch(`${API_URL}/favorites/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  return res.json();
}

export async function fetchMuseumById(id) {
  const res = await fetch(`${API_URL}/museums/${id}`, { headers: authHeaders() });
  return res.json();
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_URL}/user/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function registerUser(userData) {
  const res = await fetch(`${API_URL}/user/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  return res.json();
}


