import { useState } from "react";

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ name: query });
  };

  return (
    <div className="search-wrapper">
      <form onSubmit={handleSubmit} style={{ width: '100%' }}>
        <input
          className="search-input"
          placeholder="Recherche..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </form>
    </div>
  );
}
