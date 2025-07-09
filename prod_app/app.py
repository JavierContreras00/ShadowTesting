from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os
from pathlib import Path

# Añadir la carpeta raíz al path para poder importar utils
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import calcular_descuento, log_accion

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

# ============ LOGIN ============
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")
        try:
            with open("usuarios.txt", "r") as f:
                for linea in f:
                    u, c = linea.strip().split(":")
                    if usuario == u and clave == c:
                        session["usuario"] = usuario
                        return redirect(url_for("version_prod"))
        except FileNotFoundError:
            pass
        return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")


# ============ PRODUCCIÓN ============
@app.route("/prod", methods=["GET", "POST"])
def version_prod():
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    resultado = None
    if request.method == "POST":
        try:
            precio = float(request.form["precio"])
            resultado = calcular_descuento(precio)
            log_accion(session["usuario"], "producción", "calculó descuento")
        except:
            resultado = "Error al calcular el descuento."

    return render_template("version.html",
                           usuario=session["usuario"],
                           version="Producción",
                           color="success",
                           resultado=resultado)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
