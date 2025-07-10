# script/auth.py
import bcrypt
from script.db_connection import DBConnection

def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        db = DBConnection()
        db.cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed)
        )
        db.connection.commit()
        db.close()
        return True, "User registered!"
    except Exception as e:
        return False, f"⚠️ {e}"

def login_user(username, password):
    db = DBConnection()
    db.cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = db.cursor.fetchone()
    db.close()

    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        return True, user["id"]
    return False, "Invalid credentials"
