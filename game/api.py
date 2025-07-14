# game/api.py
import requests
import json
import os

API_BASE = "http://localhost:8080/api"
AUTH_FILE = "auth.json"

def login(username, password):
    try:
        response = requests.post(
            "http://localhost:8080/api/login/",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"username": username, "password": password})
        )
        if response.status_code == 200:
            print("Connexion réussie.")
            return response.json().get("user_id")  # <- on retourne directement l'id
        else:
            print(f"Erreur de connexion : {response.status_code} {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Erreur réseau : {e}")
        return None

def get_user_id():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f).get("user_id")
    return None

def submit_score(score, role, outcome):
    user_id = get_user_id()
    if not user_id:
        print("❌ Aucun utilisateur connecté.")
        return
    payload = {
        "user_id": user_id,
        "score": score,
        "role": role,
        "outcome": outcome,
    }
    try:
        response = requests.post(f"{API_BASE}/submit_score/", json=payload)
        if response.status_code == 200:
            print("✅ Score enregistré avec succès.")
        else:
            print(f"❌ Échec de l'envoi du score ({response.status_code}):\n{response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion au serveur : {e}")
