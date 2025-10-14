import requests
from fastapi import FastAPI, HTTPException, Query
import uvicorn
from pydantic import BaseModel


app = FastAPI(title="API Muséofile rapide et filtrable")

MUSEOFILE_API = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records"

# --- Stockage temporaire des favoris (en mémoire)
favorites = []


# --- Modèle Pydantic pour un favori
class Favorite(BaseModel):
    id: str
    name: str
    city: str | None = None
    department: str | None = None
    
@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Muséofile filtrable !"}


@app.get("/museums")
def get_museums(
    city: str | None = Query(None, description="Ville du musée"),
    department: str | None = Query(None, description="Département du musée"),
    name: str | None = Query(None, description="Nom du musée"),
    limit: int = Query(50, description="Nombre de résultats à récupérer (max 1000)"),
):
    """Recherche de musées avec filtres combinés (ville, département, nom)."""
    
    params = {"limit": limit}
    where_clauses = []

    # Construction dynamique des filtres SQL-like
    if city:
        where_clauses.append(f"ville like '{city}'")
    if department:
        where_clauses.append(f"departement like '{department}'")
    if name:
        where_clauses.append(f"nom_officiel like '%{name}%' or nom like '%{name}%'")

    # Combine les conditions avec AND
    if where_clauses:
        params["where"] = " AND ".join(where_clauses)

    try:
        response = requests.get(MUSEOFILE_API, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Erreur API :", e)
        raise HTTPException(status_code=502, detail="API Muséofile indisponible")

    data = response.json()
    results = []

    for record in data.get("results", []):
        musee = {
            "id": record.get("id"),
            "name": record.get("nom_officiel"),
            "city": record.get("ville"),
            "department": record.get("departement"),
        }
        results.append(musee)

    return {
        "filters": {
            "city": city,
            "department": department,
            "name": name,
        },
        "count": len(results),
        "results": results,
    }

@app.get("/favorites")
def get_favorites():
    return {"count": len(favorites), "favorites": favorites}


# --- Ajouter un musée aux favoris
@app.post("/favorites")
def add_favorite(fav: Favorite):
    # Vérifie si déjà présent
    if any(f["id"] == fav.id for f in favorites):
        raise HTTPException(status_code=400, detail="Ce musée est déjà dans les favoris.")
    favorites.append(fav.dict())
    return {"message": "Musée ajouté aux favoris", "favorite": fav}


# --- Supprimer un musée des favoris
@app.delete("/favorites/{museum_id}")
def remove_favorite(museum_id: str):
    global favorites
    new_list = [f for f in favorites if f["id"] != museum_id]
    if len(new_list) == len(favorites):
        raise HTTPException(status_code=404, detail="Musée non trouvé dans les favoris.")
    favorites = new_list
    return {"message": "Musée retiré des favoris"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
