import mysql.connector

class DBConnection:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sentiment_db"
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def insert_review(self, review_text, sentiment):
        query = "INSERT INTO reviews (review_text, sentiment) VALUES (%s, %s)"
        values = (review_text, sentiment)
        self.cursor.execute(query, values)
        self.connection.commit()

    def fetch_reviews(self, limit=100):
        query = f"SELECT id, review_text, sentiment, date_created FROM reviews ORDER BY date_created DESC LIMIT {limit}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_sentiment_distribution(self):
        query = "SELECT sentiment, COUNT(*) AS count FROM reviews GROUP BY sentiment"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
