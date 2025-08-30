!pip install deepface flask flask-cors pyngrok requests spotipy

from flask import Flask, request, jsonify
from flask_cors import CORS
from deepface import DeepFace
import requests, base64
from pyngrok import ngrok

# ========================
# Spotify Credentials
# ========================
SPOTIFY_CLIENT_ID = "1670c421e1ea44feb49e190716824b17"
SPOTIFY_CLIENT_SECRET = "b2492d431783479a9e0f6d1a0d04cab7"

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
    }
    data = {"grant_type": "client_credentials"}
    res = requests.post(url, headers=headers, data=data)
    return res.json().get("access_token")

def search_spotify(mood, country="US"):
    token = get_spotify_token()
    url = f"https://api.spotify.com/v1/search?q={mood}%20music&type=track&limit=5"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    tracks = []
    data = res.json()
    if "tracks" in data:
        for item in data["tracks"]["items"]:
            tracks.append(f"https://open.spotify.com/embed/track/{item['id']}")
    return tracks

def search_bangla_spotify(mood):
    token = get_spotify_token()
    url = f"https://api.spotify.com/v1/search?q={mood}%20Bangla&type=track&limit=5"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    tracks = []
    data = res.json()
    if "tracks" in data:
        for item in data["tracks"]["items"]:
            tracks.append(f"https://open.spotify.com/embed/track/{item['id']}")
    return tracks

# ========================
# Quote API (ZenQuotes)
# ========================
def get_quote():
    try:
        res = requests.get("https://zenquotes.io/api/random")
        if res.status_code == 200:
            data = res.json()[0]
            return f"{data['q']} — {data['a']}"
    except:
        pass
    return "Stay positive and keep going!"

# ========================
# Flask App
# ========================
app = Flask(__name__)
CORS(app)

@app.route("/detect_mood", methods=["POST"])
def detect_mood():
    try:
        file = request.files["image"]
        file.save("temp.jpg")

        analysis = DeepFace.analyze(img_path="temp.jpg", actions=['emotion'])
        mood = analysis[0]['dominant_emotion']

        quote = get_quote()
        english_songs = search_spotify(mood)
        bangla_songs = search_bangla_spotify(mood)

        return jsonify({
            "mood": mood,
            "quote": quote,
            "english": english_songs,
            "bangla": bangla_songs
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ========================
# Start ngrok and Flask
# ========================
NGROK_AUTH_TOKEN = "315GwB45fVVWUdyl6dgUybbZBSi_6nEMnJH8PAUFZbWqZCiGY"
ngrok.set_auth_token(NGROK_AUTH_TOKEN)
public_url = ngrok.connect(5000)
print("🚀 Public URL:", public_url)

app.run(port=5000)
