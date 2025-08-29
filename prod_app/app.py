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
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    print("===> Entrando en la ruta /login")  # LOG INICIAL

    ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "usuarios.txt")
    print(f"Ruta absoluta esperada del fichero: {ruta_fichero}")  # LOG

    if os.path.exists(ruta_fichero):
        print("✅ Fichero usuarios.txt encontrado.")  # LOG
    else:
        print("❌ Fichero usuarios.txt NO encontrado.")  # LOG

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "").strip()
        print(f"🔐 Intento de login con -> usuario: {usuario}, clave: {clave}")  # LOG

        try:
            with open(ruta_fichero, "r", encoding="utf-8") as f:
                print("📖 Leyendo usuarios del fichero:")  # LOG
                for linea in f:
                    partes = linea.strip().split(":", 1)
                    if len(partes) != 2:
                        print(f"⚠️ Línea malformada ignorada: {repr(linea)}")  # LOG
                        continue
                    u, c = partes
                    print(f"  → Usuario registrado: {u}, Clave: {c}")  # LOG
                    if usuario == u and clave == c:
                        print("✅ Login correcto")  # LOG
                        session["usuario"] = usuario
                        return redirect(url_for("version_prod"))
        except Exception as e:
            print(f"⚠️ Error al abrir o leer el fichero: {e}")  # LOG

        print("❌ Login fallido. Credenciales incorrectas.")  # LOG
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

        # Validar si ya existe el usuario
        if os.path.exists(ruta_fichero):
            try:
                with open(ruta_fichero, "r", encoding="utf-8") as f:
                    for linea in f:
                        partes = linea.strip().split(":", 1)
                        if len(partes) != 2:
                            continue  # Ignora líneas corruptas
                        u, _ = partes
                        if nuevo_usuario == u:
                            return render_template("registro.html", error="Ese usuario ya existe")
            except Exception as e:
                return render_template("registro.html", error=f"Error al leer usuarios: {e}")

        # Añadir el nuevo usuario (asegurando salto de línea antes si hace falta)
        try:
            necesita_salto = True
            if os.path.exists(ruta_fichero):
                with open(ruta_fichero, "rb") as f:
                    f.seek(-1, os.SEEK_END)
                    last_char = f.read(1)
                    if last_char == b"\n":
                        necesita_salto = False

            with open(ruta_fichero, "a", encoding="utf-8") as f:
                if necesita_salto:
                    f.write("\n")
                f.write(f"{nuevo_usuario}:{nueva_clave}\n")

            return render_template("registro.html", mensaje="✅ Registro exitoso. Ya puedes iniciar sesión.")
        except Exception as e:
            return render_template("registro.html", error=f"Error al guardar usuario: {e}")

    return render_template("registro.html")


# ------- UTILIDAD: leer productos desde TXT (mismo separador que el guardado) -------
def leer_productos():
    productos = []
    ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")
    if os.path.exists(ruta_fichero):
        with open(ruta_fichero, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(":")  # <- usamos ":" para ser coherentes con /incluir_productos
                if len(partes) == 3:
                    nombre, cantidad, precio = partes
                    productos.append({
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "precio": precio
                    })
    return productos


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
 
    # Cargar productos en cada petición
    productos = leer_productos()

    return render_template("version.html",
                           usuario=session["usuario"],
                           version="Producción",
                           color="success",
                           resultado=resultado,
                           productos=productos)  # <- se inyecta a la plantilla
 

# (Opcional) Ruta de ejemplo que ya tenías para otra plantilla
@app.route("/produccion", methods=["GET", "POST"])
def produccion():
    productos = leer_productos()
    return render_template("produccion.html", usuario="Demo", productos=productos)


@app.route("/guardar_productos", methods=["POST"])
def guardar_productos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        productos = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_producto[]")

        ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")

        # 👇 Sobrescribe el fichero con las filas actuales
        with open(ruta_fichero, "w", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                f.write(f"{p}:{c}:{pr}\n")

        log_accion(session["usuario"], "producción", "actualizó productos")
        return redirect(url_for("version_prod"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


@app.route("/incluir_productos", methods=["POST"])
def incluir_productos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    try:
        productos = request.form.getlist("producto[]")
        cantidades = request.form.getlist("cantidad[]")
        precios = request.form.getlist("precio_producto[]")  # <- nombre correcto del input en la plantilla

        ruta_fichero = os.path.join(Path(__file__).resolve().parents[1], "productos.txt")

        with open(ruta_fichero, "a", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                f.write(f"{p}:{c}:{pr}\n")

        log_accion(session["usuario"], "producción", "añadió productos")
        return redirect(url_for("version_prod"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
