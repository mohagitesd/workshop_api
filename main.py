import requests
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr
import bcrypt
import uvicorn
from database import get_connection
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from auth_bearer import JWTBearer
from auth_handler import sign_jwt, decode_jwt






app = FastAPI(title="API Muséofile rapide et filtrable")

MUSEOFILE_API = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ton front React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

#--- login
class UserLogin(BaseModel):
    username: str
    password: str




@app.post("/users/register")
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
        # return signed token
        return sign_jwt(str(user_id))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur ou email déjà utilisé.")
    finally:
        conn.close()


@app.get("/users/register")
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

@app.post("/users/login")
def login(user: UserLogin):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, hashed_password FROM users WHERE username = ?", (user.username,))
        row = cur.fetchone()
        if row and bcrypt.checkpw(user.password.encode(), row[1].encode()):
            user_id = row[0]
            return sign_jwt(str(user_id))
        else:
            raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect.")
    finally:
        conn.close()


def get_current_user(token: str = Depends(JWTBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide (user_id manquant)")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return {"id": row[0], "username": row[1], "email": row[2]}


@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Muséofile filtrable !"}


@app.get("/museums")
def get_museums(
    city: str | None = Query(None, description="Ville du musée"),
    department: str | None = Query(None, description="Département du musée"),
    name: str | None = Query(None, description="Nom du musée"),
    description: str | None = Query(None, description="Description du musée"),
    artist: str | None = Query(None, description="Artiste associé au musée"),
    domaine_thematique: str | None = Query(None, description="Domaine thématique du musée"),
    url: str | None = Query(None, description="URL du musée"),
    limit: int = Query(50, description="Nombre de résultats à récupérer (max 1000)"),
):
    """Recherche de musées avec filtres combinés (ville, département, nom)."""
    
    params = {"limit": limit}
    where_clauses = []

    if city:
        where_clauses.append(f"ville like '{city}'")
    if department:
        where_clauses.append(f"departement like '{department}'")
    if name:
        where_clauses.append(f"nom_officiel like '%{name}%'")
    if description:
        where_clauses.append(f"histoire like '%{description}%'")
    if artist:
        where_clauses.append(f"artiste like '%{artist}%'")
    if domaine_thematique:
        where_clauses.append(f"domaine_thematique like '%{domaine_thematique}%'")
    if url:
        where_clauses.append(f"url like '%{url}%'")

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
            "description": record.get("histoire"),
            "artist": record.get("artiste"),
            "domaine_thematique": record.get("domaine_thematique"),
            "url": record.get("url"),
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
        cur.execute("SELECT musee_id, name, city, department FROM favorites WHERE user_id = ?", (user_id,))
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
