from script.db_connection import DBConnection
from datetime import datetime
import joblib
import re

# Load model and vectorizer
model = joblib.load("model/sentiment_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")

def predict_sentiment(text: str, user_id=1, product_id=1, score=0) -> str:
    # Optional: minimal cleaning
    cleaned = text.lower()
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned_vector = vectorizer.transform([cleaned])
    sentiment = model.predict(cleaned_vector)[0]

    print("DEBUG — Text:", text)
    print("DEBUG — Cleaned:", cleaned)
    print("DEBUG — Score:", score)
    print("DEBUG — Predicted Sentiment:", sentiment)

    # ✅ Save to DB
    try:
        db = DBConnection()
        query = """
            INSERT INTO reviews (user_id, product_id, review_text, score, sentiment, date_created)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (user_id, product_id, text, score, sentiment, datetime.now())
        db.cursor.execute(query, values)
        db.connection.commit()
        db.close()
    except Exception as e:
        print("⚠️ Failed to save to DB:", e)

    return sentiment
