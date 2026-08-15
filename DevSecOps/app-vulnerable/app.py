from flask import Flask, render_template, request, redirect, session, make_response
import sqlite3
import subprocess
import hashlib
import os

app = Flask(__name__)

app.secret_key = "supersecretkey"

# Gitleaks
API_KEY = "sk-1234567890abcdef"

# Bandit
DB_PASSWORD = "admin123"
# "-------------------------------"
def get_db():

    return sqlite3.connect("users.db")
# "-------------------------------"
@app.route("/")
def index():

    return render_template("index.html")
# "-------------------------------"

@app.route("/login", methods=["GET","POST"])

def login():

    if request.method == "POST":

        username=request.form["username"]

        password=request.form["password"]

        conn=get_db()

        cursor=conn.cursor()

        query="SELECT * FROM users WHERE username='"+username+"' AND password='"+password+"'"

        cursor.execute(query)

        user=cursor.fetchone()

        conn.close()

        if user:

            session["user"]=username

            response=make_response(redirect("/dashboard"))

            response.set_cookie("sessionid","123456")

            return response

        return "Usuario incorrecto"

    return render_template("login.html")
# "-------------------------------"
@app.route("/dashboard")

def dashboard():

    if "user" not in session:

        return redirect("/login")

    return render_template(
    "dashboard.html",
    user=session["user"],
    api=API_KEY
)

# "-------------------------------"
@app.route("/ping", methods=["GET", "POST"])
def ping():

    result = ""

    if request.method == "POST":

        host = request.form["host"]

        try:
            result = subprocess.check_output(
                "ping -c 1 " + host,
                shell=True,
                text=True
            )

        except Exception as e:
            result = str(e)

    return render_template("ping.html", result=result)
# "-------------------------------"

@app.route("/download", methods=["GET", "POST"])
def download():

    content = ""

    if request.method == "POST":

        filename = request.form["filename"]

        try:

            with open("uploads/" + filename, "r") as f:
                content = f.read()

        except Exception as e:
            content = str(e)

    return render_template("download.html", content=content)
# "-------------------------------"

@app.route("/profile",methods=["GET","POST"])

def profile():

    hashed=""

    if request.method=="POST":

        password=request.form["password"]

        hashed=hashlib.md5(

            password.encode()

        ).hexdigest()

    return render_template(

        "profile.html",

        hashed=hashed

    )
# "-------------------------------"
@app.route("/search")

def search():

    q=request.args.get("q","")

    return render_template(
        "search.html",
        query=q
    )
# "-------------------------------"
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



if __name__=="__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True
    )