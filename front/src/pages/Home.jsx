import { useState } from "react";
import { fetchMuseums, addFavorite } from "../api";
import SearchBar from "../components/SearchBar";
import MuseumCard from "../components/MuseumCard";

export default function Home() {
  const [museums, setMuseums] = useState([]);
  const [loading, setLoading] = useState(false);

  async function handleSearch(filters) {
    setLoading(true);
    const data = await fetchMuseums(filters);
    setMuseums(data.results);
    setLoading(false);
  }

  async function handleAddFavorite(museum) {
    await addFavorite(museum);
    alert("Ajouté aux favoris !");
  }

  return (
    <div>
      <SearchBar onSearch={handleSearch} />
      {loading ? (
        <p>Chargement...</p>
      ) : (
        <section className="museum-grid">
          {museums.map((m) => (
            <MuseumCard key={m.id} museum={m} onAdd={handleAddFavorite} />
          ))}
        </section>
      )}
    </div>
  );
}
