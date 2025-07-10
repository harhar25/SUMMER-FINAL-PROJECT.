# script/reviews_handler.py
from script.db_connection import DBConnection

def load_reviews(user_id=None):
    try:
        db = DBConnection()
        if user_id:
            db.cursor.execute("SELECT * FROM reviews WHERE user_id = %s ORDER BY date_created DESC", (user_id,))
        else:
            db.cursor.execute("SELECT * FROM reviews ORDER BY date_created DESC")
        rows = db.cursor.fetchall()
        db.close()
        return rows
    except Exception as e:
        print("⚠️ Error loading reviews:", e)
        return []
