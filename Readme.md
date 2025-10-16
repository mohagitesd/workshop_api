# API Muséofile — backend

Ce dépôt contient une petite API FastAPI qui :
- interroge l'API Muséofile publique pour rechercher des musées (/museums),
- permet l'enregistrement d'utilisateurs (signup), l'authentification par JWT (login),
- gère des favoris liés aux utilisateurs (GET/POST/DELETE /favorites) stockés dans une base SQLite locale.

Ce README explique comment installer les dépendances, configurer les variables d'environnement, lancer le serveur et tester les endpoints.

## Prérequis
- Python 3.10+ (un environnement virtuel est recommandé)
- git (si tu clones depuis un repo)

## Installation rapide
Ouvre un terminal dans le dossier `back/` et exécute :

```bash
# (si tu n'as pas encore de venv)
python -m venv venv
source venv/bin/activate

# installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
```

## Variables d'environnement
Le projet utilise JWT et lit la clé secrète depuis des variables d'environnement. Crée un fichier `.env` à la racine du dossier `back/` (ou exporte ces variables dans ton shell) :

```
MUSEOFILE_SECRET=une_clef_secrete_tres_longue_et_aleatoire
MUSEOFILE_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Notes :
- `MUSEOFILE_SECRET` est essentiel : choisis une valeur longue et secrète pour signer les JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES` est optionnel (défaut 1440 = 1 jour).

## Base de données
La base SQLite s'appelle `museofile.db` et est initialisée automatiquement par `database.py` (la fonction `init_db()` est appelée au démarrage du module). Les tables principales sont :
- `users` (id, username, email, hashed_password)
- `favorites` (musee_id, name, city, department, user_id) — favoris liés aux utilisateurs


## Lancer le serveur

```bash
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

L'API sera disponible sur `http://127.0.0.1:8000`. La documentation interactive OpenAPI est accessible à `http://127.0.0.1:8000/docs`.

## Endpoints principaux

- POST /user/signup — créer un utilisateur
	- Body JSON : { "fullname": "Nom", "email": "x@x.com", "password": "..." }
	- Retourne un JWT signé (access_token) pour l'utilisateur créé.

- POST /users/login — obtenir un token
	- Content-Type: application/x-www-form-urlencoded
	- Body: `username=<email>&password=<motdepasse>` (le formulaire `username` contient l'email dans le code actuel)
	- Retourne : { "access_token": "...", "expires_at": "..." }

- GET /users/me — renvoie les informations de l'utilisateur connecté (token requis)

- GET /museums — recherche de musées via l'API Muséofile
	- Query params : `city`, `department`, `name`, `limit`

- GET /favorites — liste les favoris de l'utilisateur connecté (token requis)
- POST /favorites — ajoute un favori pour l'utilisateur connecté (token requis)
	- Body JSON : { "id": "MUSEE_ID", "name": "Nom", "city": "Ville", "department": "Dépt" }
- DELETE /favorites/{museum_id} — supprime un favori pour l'utilisateur connecté (token requis)





## Suggestions / améliorations possibles
- Ajouter une route `/token` ou accepter JSON dans `/users/login` pour compatibilité avec clients qui n'envoient pas de form-url-encoded.




