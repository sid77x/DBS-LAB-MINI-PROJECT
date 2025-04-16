import sqlite3

def get_recommendations(user_id, db_path="database.db", limit=10):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = f""" 
    WITH liked_movies AS (
        SELECT movie_id 
        FROM Ratings 
        WHERE user_id = ? AND rating >= 4
    ),
    similar_users AS (
        SELECT DISTINCT user_id 
        FROM Ratings 
        WHERE movie_id IN (SELECT movie_id FROM liked_movies)
          AND user_id != ? AND rating >= 4
    ),
    recommended_movies AS (
        SELECT movie_id, AVG(rating) AS avg_rating, COUNT(*) AS vote_count
        FROM Ratings
        WHERE user_id IN (SELECT user_id FROM similar_users)
          AND movie_id NOT IN (SELECT movie_id FROM liked_movies)
        GROUP BY movie_id
        HAVING vote_count >= 3
    )
    SELECT 
        m.movie_id,
        m.title, 
        r.avg_rating, 
        r.vote_count
    FROM recommended_movies r
    JOIN Movies m ON r.movie_id = m.movie_id
    ORDER BY r.avg_rating DESC, r.vote_count DESC
    LIMIT ?
    """

    cur.execute(query, (user_id, user_id, limit))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print(f"\n😕 No recommendations found for user {user_id}. Try another one?\n")
        return []

    return [(row["movie_id"], row["avg_rating"]) for row in rows]
