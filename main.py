import requests
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

MUSEOFILE_API = "https://data.culture.gouv.fr/api/explore/v2.1/catalog/datasets/musees-de-france-base-museofile/records?limit=20"

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API simplifiée."}

@app.get("/museums")
def get_museums():
    
    try:
        response = requests.get(MUSEOFILE_API)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Erreur API :", e)
        raise HTTPException(status_code=502, detail="API Muséofile indisponible")

    data = response.json()
    results = []
    for record in data.get("results", []):  
        musee = {
            "id": record.get("identifiant"),
            "name": record.get("nom_officiel") ,
            "city": record.get("ville"),
            "department": record.get("departement"),
            "address": record.get("adresse"),
            "postal_code": record.get("code_postal"),
            "region": record.get("region"),
           
        }
        results.append(musee)

    return {"count": len(results), "results": results}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
