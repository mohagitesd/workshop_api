import requests
from fastapi import FastAPI, HTTPException, Query, Header
import uvicorn
from pydantic import BaseModel
from pathlib import Path
from database import *
import sqlite3
import bcrypt
from uuid import uuid4
from typing import Optional


app = FastAPI(title="API Muséofile rapide et filtrable")


MUSEOFILE_API = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records"


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


# ------------------ Authentication ------------------


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str


class LoginIn(BaseModel):
    username: str
    password: str


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


@app.post('/register')
def register(data: RegisterIn):
    conn = get_connection()
    cur = conn.cursor()
    try:
        hashed = hash_password(data.password)
        cur.execute(
            'INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)',
            (data.username, data.email, hashed),
        )
        conn.commit()
        return {'message': 'Utilisateur créé'}
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=400, detail='Username ou email déjà utilisé')
    finally:
        conn.close()


@app.post('/login')
def login(data: LoginIn):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT id, hashed_password FROM users WHERE username = ?', (data.username,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=401, detail='Identifiants invalides')
        user_id, hashed = row[0], row[1]
        if not verify_password(data.password, hashed):
            raise HTTPException(status_code=401, detail='Identifiants invalides')
        token = str(uuid4())
        cur.execute('INSERT INTO tokens (token, user_id, created_at) VALUES (?, ?, datetime("now"))', (token, user_id))
        conn.commit()
        return {'token': token}
    finally:
        conn.close()


def get_user_from_token(authorization: Optional[str]) -> Optional[int]:
    # expects Authorization: Bearer <token>
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    token = parts[1]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT user_id FROM tokens WHERE token = ?', (token,))
        row = cur.fetchone()
        if not row:
            return None
        return row[0]
    finally:
        conn.close()


# ------------------ User favorites (protected) ------------------


@app.post('/my/favorites')
def add_my_favorite(fav: Favorite, Authorization: Optional[str] = Header(None)):
    user_id = get_user_from_token(Authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')

    # Ensure favorite exists in favorites table
    conn = get_connection()
    cur = conn.cursor()
    try:
        try:
            cur.execute('INSERT INTO favorites (id, name, city, department) VALUES (?, ?, ?, ?)', (fav.id, fav.name, fav.city, fav.department))
        except sqlite3.IntegrityError:
            # already exists, that's fine
            pass

        # link to user
        cur.execute('INSERT INTO user_favorites (user_id, favorite_id) VALUES (?, ?)', (user_id, fav.id))
        conn.commit()
        return {'message': 'Favori ajouté pour l\'utilisateur'}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail='Favori déjà lié à cet utilisateur')
    finally:
        conn.close()


@app.get('/my/favorites')
def list_my_favorites(Authorization: Optional[str] = Header(None)):
    user_id = get_user_from_token(Authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('''
            SELECT f.id, f.name, f.city, f.department
            FROM favorites f
            JOIN user_favorites uf ON uf.favorite_id = f.id
            WHERE uf.user_id = ?
        ''', (user_id,))
        rows = cur.fetchall()
        favs = [{"id": r[0], "name": r[1], "city": r[2], "department": r[3]} for r in rows]
        return {"count": len(favs), "favorites": favs}
    finally:
        conn.close()


@app.delete('/my/favorites/{museum_id}')
def remove_my_favorite(museum_id: str, Authorization: Optional[str] = Header(None)):
    user_id = get_user_from_token(Authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail='Unauthorized')
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM user_favorites WHERE user_id = ? AND favorite_id = ?', (user_id, museum_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail='Favori non trouvé pour cet utilisateur')
        return {'message': 'Favori retiré'}
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
