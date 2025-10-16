import React from 'react'
import { Link } from 'react-router-dom'

export default function MuseumCard({ museum, onAdd }) {
  return (
    <article className="museum-card">
      <Link to={`/museum/${museum.id}`} state={{ museum }} style={{ textDecoration: 'none', color: 'inherit' }}>
        <img src={museum.image || "https://picsum.photos/seed/" + museum.id + "/800/400"} alt={museum.name} />
      </Link>
      <div className="card-body">
        <h3>
          <Link to={`/museum/${museum.id}`} state={{ museum }} style={{ textDecoration: 'none', color: 'black',textTransform:'uppercase' }}>{museum.name}</Link>
        </h3>
        <p style={{ marginTop: 8, color: '#666' }}>{museum.city}{museum.department ? `, ${museum.department}` : ''}</p>
        <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
          <button className="btn-favorite" onClick={() => onAdd && onAdd(museum)}>Favoris</button>
          <Link to={`/museum/${museum.id}`} state={{ museum }} className="btn-favorite">Voir la fiche</Link>
        </div>
      </div>
    </article>
  );
}
