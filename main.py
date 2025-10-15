import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import EmailStr
import bcrypt
import uvicorn
from pydantic import BaseModel
from pathlib import Path
from database import *
import sqlite3


app = FastAPI(title="API Muséofile rapide et filtrable")


MUSEOFILE_API = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records"


# --- Modèle Pydantic pour un favori
class Favorite(BaseModel):
    id: str
    name: str
    city: str | None = None
    department: str | None = None 


# --- Modèle Pydantic pour création d'utilisateur
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


@app.post("/register")
def register(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        hashed = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (user.username, user.email, hashed)
        )
        conn.commit()
        return {"message": "Utilisateur créé", "username": user.username, "email": user.email}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou email déjà utilisé.")
    finally:
        conn.close()

@app.get("/register")
def get_register():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        user_list = [{"id": u[0], "username": u[1], "email": u[2]} for u in users]
        return {"users": user_list}
    finally:
        conn.close()

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
        where_clauses.append(f"nom_officiel like '%{name}%'")

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
            "id": record.get("identifiant"),
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
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, city, department FROM favorites")
        rows = cur.fetchall()
        favs = [
            {"id": r[0], "name": r[1], "city": r[2], "department": r[3]} for r in rows
        ]
        return {"count": len(favs), "favorites": favs}
    finally:
        conn.close()


@app.post("/favorites")
def add_favorite(fav: Favorite):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO favorites (id, name, city, department) VALUES (?, ?, ?, ?)",
            (fav.id, fav.name, fav.city, fav.department),
        )
        conn.commit()
        return {"message": "Musée ajouté aux favoris", "favorite": fav}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ce musée est déjà dans les favoris.")
    except Exception as exc:
        print("Erreur DB:", exc)
        raise HTTPException(status_code=500, detail="Erreur lors de l'enregistrement du favori")
    finally:
        conn.close()


@app.delete("/favorites/{museum_id}")
def remove_favorite(museum_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM favorites WHERE id = ?", (museum_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Musée non trouvé dans les favoris.")
        return {"message": "Musée retiré des favoris"}
    finally:
        conn.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
