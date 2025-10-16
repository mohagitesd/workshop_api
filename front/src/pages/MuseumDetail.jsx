import { useLocation, useNavigate } from 'react-router-dom';

export default function MuseumDetail(){
  const location = useLocation();
  const navigate = useNavigate();
  const museum = location.state?.museum;

  if(!museum){
    return (
      <div style={{ maxWidth: 900, margin: '40px auto', padding: 20 }}>
        <p>Musée introuvable. Revenez à la liste et cliquez sur une carte.</p>
        <button onClick={() => navigate(-1)}>Retour</button>
      </div>
    )
  }

  const mapQuery = museum.location ? `${museum.location.lat},${museum.location.lng}` : encodeURIComponent(`${museum.name} ${museum.city}`);

  return (
    <div className="museum-detail">
      <button style={{ marginBottom: 12 }} onClick={() => navigate(-1)}>← Retour</button>
      <article className="detail-grid">
        <main className="detail-main">
          <h1>{museum.name}</h1>

          <section className="detail-section">
            <h4>Nom du musée</h4>
            <div>{museum.name}</div>
          </section>

          <section className="detail-section">
            <h4>Adresse</h4>
            <div>{museum.address || `${museum.city}${museum.department ? ', ' + museum.department : ''}`}</div>
          </section>

          <section className="detail-section">
            <h4>Description</h4>
            <div>{museum.description }</div>
          </section>

          <section className="detail-section">
            <h4>Artistes</h4>
            <div>{museum.artist}</div>
          </section>

          <section className="detail-section">
            <h4>Domaine thématique</h4>
            <div>{museum.domaine_thematique}</div>
          </section>

          <section className="detail-section">
            <h4>En savoir plus</h4>
            <div>{museum.url}</div>
          </section>
        </main>

        <aside className="detail-aside">
          <img className="detail-image" src={museum.image || "https://picsum.photos/seed/" + museum.id + "/800/400"} alt={museum.name} />

          <div className="notice-box">
            <h4>A propos de la notice</h4>
            <ul className="notice-list">
              <li>Identifiant du musée<br/><strong>{museum.id}</strong></li>
              <li>Nom de la base<br/><strong>{museum.source || 'Site du musée national'}</strong></li>
              <li>Date de création<br/><strong>{museum.create_date || '2019-01-21'}</strong></li>
            </ul>
          </div>

          <iframe
            title="map"
            className="map-embed"
            loading="lazy"
            src={`https://www.google.com/maps?q=${mapQuery}&output=embed`}
          />
        </aside>
      </article>
    </div>
  )
}
