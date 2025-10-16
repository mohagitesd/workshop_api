import { useEffect, useState } from "react";
import { fetchFavorites, removeFavorite } from "../api";
import { Link } from 'react-router-dom';

export default function Favorites() {
  const [favorites, setFavorites] = useState([]);

  async function loadFavorites() {
    const data = await fetchFavorites();
    setFavorites(data.favorites || data || []);
  }

  useEffect(() => {
    loadFavorites();
  }, []);

  async function handleRemove(id) {
    await removeFavorite(id);
    loadFavorites();
  }

  return (
    <div className="favorites-page">
      <h1>Mes favoris</h1>
      {favorites.length === 0 ? (
        <p>Aucun favori enregistré.</p>
      ) : (
        <div className="favorites-list">
          {favorites.map((f) => (
            <div className="favorite-item" key={f.id}>
              <img src={f.image || `https://picsum.photos/seed/${f.id}/300/160`} alt={f.name} />
              <div className="favorite-body">
                <h3>{f.name}</h3>
                <p className="muted">{f.city}{f.department ? `, ${f.department}` : ''}</p>
                <div className="favorite-actions">
                  <Link to={`/museum/${f.id}`} state={{ museum: f }} className="btn-favorite">Voir la fiche</Link>
                  <button onClick={() => handleRemove(f.id)} className="btn-favorite">Supprimer</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
