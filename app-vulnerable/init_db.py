import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("DELETE FROM users")

# Contraseña en texto plano a propósito (coincide con la comparación SQL directa de app.py)
cursor.execute(
    "INSERT INTO users(username,password) VALUES(?,?)",
    ("admin", "admin123")
)

conn.commit()
conn.close()

print("Base de datos creada (vulnerable).")
