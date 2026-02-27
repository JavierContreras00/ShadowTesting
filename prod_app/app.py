from flask import Flask, render_template, request, redirect, url_for, session
import os
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

from utils import calcular_descuento, log_accion

app = Flask(__name__)

# ✅ Mejor que hardcodear: permite demo con env var, pero mantiene fallback
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_insecure_key_change_me")

BASE_DIR = Path(__file__).resolve().parents[0]  # ajusta si tu app.py está en otra carpeta
USUARIOS_TXT = BASE_DIR / "usuarios.txt"
PRODUCTOS_TXT = BASE_DIR / "productos.txt"


# ---------- USERS ----------
def iter_users():
    """Yield (user, stored_password) from usuarios.txt. Ignores malformed lines."""
    if not USUARIOS_TXT.exists():
        return
    with USUARIOS_TXT.open("r", encoding="utf-8") as f:
        for linea in f:
            partes = linea.strip().split(":", 1)
            if len(partes) != 2:
                continue
            yield partes[0].strip(), partes[1].strip()


def user_exists(username: str) -> bool:
    return any(u == username for u, _ in iter_users())


def verify_password(stored: str, candidate: str) -> bool:
    """
    Backward compatible:
    - If stored looks like a werkzeug hash => check_password_hash
    - else => legacy plain compare (so existing users still can login)
    """
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
        return check_password_hash(stored, candidate)
    return stored == candidate


# ============ LOGIN ============
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "").strip()

        # ✅ No loguear contraseñas
        print(f"🔐 Intento de login usuario={usuario!r}")

        for u, stored in iter_users():
            if usuario == u and verify_password(stored, clave):
                session["usuario"] = usuario
                return redirect(url_for("version_prod"))

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nuevo_usuario = request.form.get("usuario", "").strip()
        nueva_clave = request.form.get("clave", "").strip()

        if not nuevo_usuario or not nueva_clave:
            return render_template("registro.html", error="Usuario y contraseña no pueden estar vacíos")

        if user_exists(nuevo_usuario):
            return render_template("registro.html", error="Ese usuario ya existe")

        password_hash = generate_password_hash(nueva_clave)

        try:
            # Asegura salto de línea si el fichero no termina en \n
            needs_newline = False
            if USUARIOS_TXT.exists() and USUARIOS_TXT.stat().st_size > 0:
                with USUARIOS_TXT.open("rb") as f:
                    f.seek(-1, os.SEEK_END)
                    needs_newline = (f.read(1) != b"\n")

            with USUARIOS_TXT.open("a", encoding="utf-8") as f:
                if needs_newline:
                    f.write("\n")
                f.write(f"{nuevo_usuario}:{password_hash}\n")

            return render_template("registro.html", mensaje="✅ Registro exitoso. Ya puedes iniciar sesión.")
        except Exception as e:
            return render_template("registro.html", error=f"Error al guardar usuario: {e}")

    return render_template("registro.html")


# ---------- PRODUCTS ----------
def leer_productos():
    productos = []
    if PRODUCTOS_TXT.exists():
        with PRODUCTOS_TXT.open("r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(":")
                if len(partes) != 3:
                    continue
                nombre, cantidad, precio = partes
                try:
                    productos.append({
                        "nombre": nombre.strip(),
                        "cantidad": int(cantidad),
                        "precio": float(precio),
                    })
                except ValueError:
                    # ignora filas corruptas
                    continue
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
        except Exception:
            resultado = "Error al calcular el descuento."

    productos = leer_productos()

    return render_template(
        "version.html",
        usuario=session["usuario"],
        version="Producción",
        color="success",
        resultado=resultado,
        productos=productos,
    )


@app.route("/produccion", methods=["GET", "POST"])
def produccion():
    productos = leer_productos()
    return render_template("produccion.html", usuario="Demo", productos=productos)


@app.route("/guardar_productos", methods=["POST"])
def guardar_productos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    productos = request.form.getlist("producto[]")
    cantidades = request.form.getlist("cantidad[]")
    precios = request.form.getlist("precio_producto[]")

    try:
        with PRODUCTOS_TXT.open("w", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                p = (p or "").strip()
                if not p:
                    continue
                c_int = int(c)
                pr_f = float(pr)
                f.write(f"{p}:{c_int}:{pr_f}\n")

        log_accion(session["usuario"], "producción", "actualizó productos")
        return redirect(url_for("version_prod"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


@app.route("/incluir_productos", methods=["POST"])
def incluir_productos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    productos = request.form.getlist("producto[]")
    cantidades = request.form.getlist("cantidad[]")
    precios = request.form.getlist("precio_producto[]")

    try:
        with PRODUCTOS_TXT.open("a", encoding="utf-8") as f:
            for p, c, pr in zip(productos, cantidades, precios):
                p = (p or "").strip()
                if not p:
                    continue
                c_int = int(c)
                pr_f = float(pr)
                f.write(f"{p}:{c_int}:{pr_f}\n")

        log_accion(session["usuario"], "producción", "añadió productos")
        return redirect(url_for("version_prod"))
    except Exception as e:
        return f"❌ Error al guardar productos: {e}"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
