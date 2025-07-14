# game/api.py
import requests
import json
import os

API_BASE = "http://localhost:8080/api"
AUTH_FILE = "auth.json"

def login(username, password):
    url = f"{API_BASE}/login/"
    response = requests.post(url, json={"username": username, "password": password})
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data.get("user_id")
        if user_id:
            with open(AUTH_FILE, "w") as f:
                json.dump({"user_id": user_id}, f)
            print("Connexion réussie.")
            return user_id
    print("Erreur de connexion :", response.status_code, response.text)
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
