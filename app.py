import json
import random
import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "clave_secreta_123"

PASSWORD = "1234"  # 🔐 cambia esto

MEMORY_FILE = "memoria.json"

# -------- MEMORIA --------
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except:
        memory = {}
else:
    memory = {}

def guardar_memoria():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# -------- RESPUESTAS --------
RESPUESTAS = {
    "saludo": ["Hola 😄", "Hey 👋", "Buenas 😎"],
    "pregunta": ["No sé 🤔 ¿me enseñas?"],
    "aprendido": ["¡Ya lo aprendí! 😄", "Listo 👌"]
}

estado_aprendizaje = {}

# -------- IA --------
def detectar_intencion(mensaje):
    mensaje = mensaje.lower()
    if any(p in mensaje for p in ["hola", "hey", "buenas"]):
        return "saludo"
    if "?" in mensaje:
        return "pregunta"
    return "normal"

def responder(mensaje):
    mensaje = mensaje.lower()

    if mensaje in memory:
        return random.choice(memory[mensaje])

    for clave in memory:
        if clave in mensaje:
            return random.choice(memory[clave])

    tipo = detectar_intencion(mensaje)

    if tipo == "saludo":
        return random.choice(RESPUESTAS["saludo"])

    if tipo == "pregunta":
        return random.choice(RESPUESTAS["pregunta"])

    return "No sé 🤔 ¿me enseñas?"

# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")

        if password == PASSWORD:
            session["autorizado"] = True
            return redirect(url_for("index"))
        else:
            return "Contraseña incorrecta 😡"

    return render_template("login.html")

# -------- HOME --------
@app.route("/")
def index():
    if not session.get("autorizado"):
        return redirect(url_for("login"))
    return render_template("index.html")

# -------- CHAT --------
@app.route("/chat", methods=["POST"])
def chat():
    if not session.get("autorizado"):
        return jsonify({"respuesta": "No autorizado"}), 403

    data = request.json
    mensaje = data.get("mensaje")
    user = "default"

    if estado_aprendizaje.get(user):
        pregunta = estado_aprendizaje[user]

        if pregunta not in memory:
            memory[pregunta] = []

        if mensaje not in memory[pregunta]:
            memory[pregunta].append(mensaje)

        guardar_memoria()
        estado_aprendizaje[user] = None

        return jsonify({"respuesta": random.choice(RESPUESTAS["aprendido"])})

    respuesta = responder(mensaje)

    if "¿me enseñas?" in respuesta:
        estado_aprendizaje[user] = mensaje

    return jsonify({"respuesta": respuesta})

# -------- RUN --------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
