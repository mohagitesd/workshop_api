import os
import requests
from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from typing import Optional
from pydantic import EmailStr
import bcrypt
import uvicorn
from pydantic import BaseModel
from pathlib import Path
from database import get_connection
import sqlite3
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("MUSEOFILE_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440)) 

security = HTTPBearer()

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

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str: 
    to_encode = data.copy() 
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")



def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    print (token)
    payload = decode_token(token)
    print("payload:", payload)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token invalide (sub manquant)")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")

    return {"id": row[0], "username": row[1], "email": row[2]}



@app.post("/users")
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
        user_id = cur.lastrowid
        return {"message": "Utilisateur créé", "id": user_id, "username": user.username, "email": user.email}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou email déjà utilisé.")
    finally:
        conn.close()

@app.get("/users")
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



@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, hashed_password, username FROM users WHERE email = ?", (form_data.username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    user_id, hashed_password, username = row[0], row[1], row[2]
    if not bcrypt.checkpw(form_data.password.encode(), hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"sub": user_id, "username": username}
    token = create_access_token(token_data, expires_delta=access_token_expires)
    expires_at = datetime.now(timezone.utc) + access_token_expires
    return {"access_token": token, "expires_at": expires_at}


@app.get("/users/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}



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
def get_favorites(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT musee_id, name, city, department FROM favorites WHERE user_id = ?",
            (user_id,)
        )
        rows = cur.fetchall()
        favs = [
            {"id": r[0], "name": r[1], "city": r[2], "department": r[3]} for r in rows
        ]
        return {"count": len(favs), "favorites": favs}
    finally:
        conn.close()


@app.post("/favorites")
def add_favorite(fav: Favorite, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO favorites (musee_id, name, city, department, user_id) VALUES (?, ?, ?, ?, ?)",
            (fav.id, fav.name, fav.city, fav.department, user_id),
        )
        conn.commit()
        return {"message": "Musée ajouté aux favoris", "favorite": fav}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ce musée est déjà dans les favoris pour cet utilisateur.")
    finally:
        conn.close()


@app.delete("/favorites/{museum_id}")
def remove_favorite(museum_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM favorites WHERE musee_id = ? AND user_id = ?", (museum_id, user_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Musée non trouvé dans les favoris de cet utilisateur.")
        return {"message": "Musée retiré des favoris"}
    finally:
        conn.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
