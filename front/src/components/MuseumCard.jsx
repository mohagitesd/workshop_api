import React from 'react'
import { Link } from 'react-router-dom'

export default function MuseumCard({ museum, onAdd }) {
  return (
    <Link to={`/museum/${museum.id}`} state={{ museum }} style={{ textDecoration: 'none', color: 'inherit' }}>
      <article className="museum-card">
        <div className='img-card-wrapper'><img src={museum.image || "https://picsum.photos/seed/" + museum.id + "/800/400"} alt={museum.name} /></div>
        <div className="card-body">
          <h3 style={{ textTransform: 'uppercase' }}>{museum.name}</h3>
          <p style={{ marginTop: 8, color: '#666' }}>{museum.city}{museum.department ? `, ${museum.department}` : ''}</p>
          <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
            <button className="btn-favorite" onClick={(e) => { e.stopPropagation(); e.preventDefault(); onAdd && onAdd(museum); }}>Favoris</button>
            <span className="btn-favorite">Voir la fiche</span>
          </div>
        </div>
      </article>
    </Link>
  );
}
