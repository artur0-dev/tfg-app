from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    make_response
)

from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

import sqlite3
import subprocess
import bcrypt
import os

app = Flask(__name__)

# ===========================
# Inicialización segura del entorno
# ===========================
# Crea el directorio de cargas si no existe para evitar fallos de E/S
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Asegura la existencia de la base de datos y su esquema básico en Docker
if not os.path.exists("users.db"):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE, 
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# ===========================
# Configuración segura
# ===========================

app.secret_key = os.getenv("SECRET_KEY", "change_me")

API_KEY = os.getenv("API_KEY")

# Cookie de sesión de Flask con SameSite y Secure
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Protección CSRF global para TODOS los formularios POST,
# no solo los que usan FlaskForm explícitamente
csrf = CSRFProtect(app)

# ===========================
# Base de datos
# ===========================

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ===========================
# Formularios
# ===========================

class LoginForm(FlaskForm):

    username = StringField(
        "Usuario",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired()]
    )


class PingForm(FlaskForm):

    host = StringField(
        "Host",
        validators=[DataRequired()]
    )


class DownloadForm(FlaskForm):

    filename = StringField(
        "Archivo",
        validators=[DataRequired()]
    )


class ProfileForm(FlaskForm):

    password = PasswordField(
        "Nueva contraseña",
        validators=[DataRequired()]
    )

# ===========================
# Página principal
# ===========================

@app.route("/")
def index():

    return render_template("index.html")

# ===========================
# Login seguro
# ===========================

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (username,)
        )

        row = cursor.fetchone()

        conn.close()

        if row:

            stored_password = row["password"].encode()

            if bcrypt.checkpw(
                password.encode(),
                stored_password
            ):

                session["user"] = username
                session.permanent = True

                response = make_response(
                    redirect("/dashboard")
                )

                response.set_cookie(
                    "sessionid",
                    "123456",
                    httponly=True,
                    secure=os.getenv("FLASK_ENV") == "production",
                    samesite="Lax"
                )

                return response

        return render_template(
            "login.html",
            form=form,
            error="Usuario o contraseña incorrectos"
        )

    return render_template(
        "login.html",
        form=form
    )

# ===========================
# Dashboard
# ===========================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

# ===========================
# Logout
# ===========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ===========================
# Ping seguro
# ===========================

@app.route("/ping", methods=["GET", "POST"])
def ping():

    form = PingForm()
    result = ""

    if form.validate_on_submit():

        host = form.host.data

        try:

            result = subprocess.run(
                ["ping", "-c", "1", host],
                capture_output=True,
                text=True,
                timeout=5
            ).stdout

        except Exception as e:

            result = str(e)

    return render_template(
        "ping.html",
        form=form,
        result=result
    )


# ===========================
# Descarga segura
# ===========================

@app.route("/download", methods=["GET", "POST"])
def download():

    form = DownloadForm()
    content = ""

    if form.validate_on_submit():

        filename = form.filename.data

        base_path = os.path.abspath("uploads")

        requested_path = os.path.abspath(
            os.path.join(base_path, filename)
        )

        if not requested_path.startswith(base_path):

            content = "Acceso denegado."

        else:

            try:

                with open(requested_path, "r") as f:

                    content = f.read()

            except Exception:

                content = "El archivo no existe."

    return render_template(
        "download.html",
        form=form,
        content=content
    )


# ===========================
# Perfil
# ===========================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    form = ProfileForm()
    hashed = ""

    if form.validate_on_submit():

        password = form.password.data

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    return render_template(
        "profile.html",
        form=form,
        hashed=hashed
    )


# ===========================
# Búsqueda
# ===========================

@app.route("/search")
def search():

    query = request.args.get("q", "")

    return render_template(
        "search.html",
        query=query
    )


# ===========================
# Manejadores de Errores Personalizados
# ===========================

@app.errorhandler(404)
def page_not_found(error):

    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    # Mitiga 'Application Error Disclosure' y 'Debug Error Messages'
    # devolviendo una estructura HTML controlada sin volcados de pila (stack traces).
    return render_template("500.html"), 500


# ===========================
# Cabeceras de seguridad
# ===========================

@app.after_request
def security_headers(response):

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["Referrer-Policy"] = "strict-origin"

    response.headers["Permissions-Policy"] = "geolocation=()"

    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

    response.headers["Strict-Transport-Security"] = "max-age=31536000"

    # Ocultar la versión real del servidor
    response.headers["Server"] = "WebServer"

    return response


# ===========================
# Inicio de la aplicación
# ===========================

if __name__ == "__main__":

    # Nota: en producción esta app se sirve con Gunicorn (ver Dockerfile),
    # que sí respeta el header "Server" definido en security_headers().
    # Este bloque solo se usa para pruebas locales con "python app.py".
    from werkzeug.serving import WSGIRequestHandler

    class CustomRequestHandler(WSGIRequestHandler):
        def version_string(self):
            return "WebServer"

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        request_handler=CustomRequestHandler
    )
