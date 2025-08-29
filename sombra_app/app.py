from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os
import time
from pathlib import Path

# Añadir la carpeta raíz al path para poder importar utils
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils import calcular_descuento, log_accion

app = Flask(__name__)
app.secret_key = "clave_super_secreta_sombra"

# ------- UTILIDAD: leer productos desde TXT (mismo separador que el guardado) -------
def leer_productos():
    productos = []
    ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")
    if os.path.exists(ruta_fichero):
        with open(ruta_fichero, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(":")  # coherente con incluir/guardar
                if len(partes) == 3:
                    nombre, cantidad, precio = partes
                    productos.append({
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "precio": precio
                    })
    return productos


# ============ LOGIN ============
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "usuarios.txt")

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "").strip()

        try:
            with open(ruta_fichero, "r", encoding="utf-8") as f:
                for linea in f:
                    partes = linea.strip().split(":", 1)
                    if len(partes) != 2:
                        continue
                    u, c = partes
                    if usuario == u and clave == c:
                        session["usuario"] = usuario
                        time.sleep(5)  # espera de 5s para simular latencia en Sombra
                        return redirect(url_for("version_sombra"))
        except Exception:
            pass

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/registro", methods=["GET", "POST"])
def registro():
    ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "usuarios.txt")

    if request.method == "POST":
        nuevo_usuario = request.form.get("usuario", "").strip()
        nueva_clave = request.form.get("clave", "").strip()

        if not nuevo_usuario or not nueva_clave:
            return render_template("registro.html", error="Usuario y contraseña no pueden estar vacíos")

        # Validar si ya existe
        if os.path.exists(ruta_fichero):
            try:
                with open(ruta_fichero, "r", encoding="utf-8") as f:
                    for linea in f:
                        partes = linea.strip().split(":", 1)
                        if len(partes) == 2 and partes[0] == nuevo_usuario:
                            return render_template("registro.html", error="Ese usuario ya existe")
            except Exception as e:
                return render_template("registro.html", error=f"Error al leer usuarios: {e}")

        # Guardar
        try:
            necesita_salto = os.path.exists(ruta_fichero) and os.path.getsize(ruta_fichero) > 0
            with open(ruta_fichero, "a", encoding="utf-8") as f:
                if necesita_salto:
                    f.write("\n")
                f.write(f"{nuevo_usuario}:{nueva_clave}\n")
            return render_template("registro.html", mensaje="✅ Registro exitoso. Ya puedes iniciar sesión.")
        except Exception as e:
            return render_template("registro.html", error=f"Error al guardar usuario: {e}")

    return render_template("registro.html")


# ============ SOMBRA ============
@app.route("/sombra", methods=["GET", "POST"])
def version_sombra():
    if "usuario" not in session:
        return redirect(url_for("login"))

    resultado = None
    if request.method == "POST":
        try:
            precio = float(request.form["precio"])
            resultado = calcular_descuento(precio)
            log_accion(session["usuario"], "sombra", "calculó descuento")
        except:
            resultado = "Error al calcular el descuento."

    # Cargar productos en cada petición
    productos = leer_productos()

    return render_template("version.html",
                           usuario=session["usuario"],
                           version="Sombra",
                           color="warning",
                           resultado=resultado,
                           productos=productos)


@app.route("/guardar_productos_sombra", methods=["POST"])
def guardar_productos_sombra():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        productos = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_producto[]")

        ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")

        # Reescribe el fichero con las filas actuales
        with open(ruta_fichero, "w", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                f.write(f"{p}:{c}:{pr}\n")

        log_accion(session["usuario"], "sombra", "actualizó productos")
        return redirect(url_for("version_sombra"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


@app.route("/incluir_productos_sombra", methods=["POST"])
def incluir_productos_sombra():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        productos = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_producto[]")  # nombre correcto del input

        ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")

        with open(ruta_fichero, "a", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                f.write(f"{p}:{c}:{pr}\n")

        log_accion(session["usuario"], "sombra", "añadió productos")
        return redirect(url_for("version_sombra"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


if __name__ == "__main__":
    app.run(port=5001, debug=True)
