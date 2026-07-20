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

cursor.execute("""

INSERT INTO users(username,password)

VALUES('admin','admin')

""")

conn.commit()

conn.close()