import { useEffect, useState } from "react";
import { fetchFavorites, removeFavorite } from "../api";

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);

  async function loadFavorites() {
    const data = await fetchFavorites();
    setFavorites(data.favorites);
  }

  useEffect(() => {
    loadFavorites();
  }, []);

  async function handleRemove(id) {
    await removeFavorite(id);
    loadFavorites();
  }

  return (
    <div>
      <h1>Mes favoris</h1>
      {favorites.length === 0 ? (
        <p>Aucun favori enregistré.</p>
      ) : (
        <ul>
          {favorites.map((f) => (
            <li key={f.id}>
              <strong>{f.name}</strong> — {f.city} ({f.department})
              <button onClick={() => handleRemove(f.id)}>Supprimer</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
