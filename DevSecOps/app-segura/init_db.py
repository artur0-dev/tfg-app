import sqlite3
import bcrypt

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

hashed = bcrypt.hashpw(
    b"admin",
    bcrypt.gensalt()
).decode()

cursor.execute(
    "INSERT INTO users(username,password) VALUES(?,?)",
    ("admin", hashed)
)

conn.commit()
conn.close()

print("Base de datos creada.")