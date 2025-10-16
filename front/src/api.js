const API_URL = "http://127.0.0.1:8000";

export async function fetchMuseums(filters = {}) {
  const params = new URLSearchParams(filters);
  const res = await fetch(`${API_URL}/museums?${params}`);
  return res.json();
}

export async function fetchFavorites() {
  const res = await fetch(`${API_URL}/favorites`);
  return res.json();
}

export async function addFavorite(fav) {
  const res = await fetch(`${API_URL}/favorites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(fav),
  });
  return res.json();
}

export async function removeFavorite(id) {
  const res = await fetch(`${API_URL}/favorites/${id}`, { method: "DELETE" });
  return res.json();
}
