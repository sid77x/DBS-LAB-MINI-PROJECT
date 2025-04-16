import sqlite3
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy

# Load data from SQLite
def load_ratings_from_db(db_path="database.db"):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT user_id, movie_id, rating FROM Ratings", conn)
    conn.close()
    return df

# Convert to Surprise Dataset
def prepare_surprise_data(df):
    reader = Reader(rating_scale=(0.5, 5.0))
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)
    return data

# Train model with hyperparameters tuning
def train_model(data):
    trainset, testset = train_test_split(data, test_size=0.2)
    model = SVD(n_factors=100, lr_all=0.005, reg_all=0.2)  # tuned parameters
    model.fit(trainset)
    
    # Evaluate the model
    predictions = model.test(testset)
    rmse = accuracy.rmse(predictions)
    mae = accuracy.mae(predictions)
    
    print(f"Model Evaluation:\nRMSE: {rmse}\nMAE: {mae}")
    return model

# Recommend movies for a user
def recommend_movies(user_id, model, df, top_n=10):
    # Movies user has already rated
    rated_movies = df[df["user_id"] == user_id]["movie_id"].tolist()
    
    all_movies = df["movie_id"].unique()
    movies_to_predict = [mid for mid in all_movies if mid not in rated_movies]
    
    predictions = []
    for movie_id in movies_to_predict:
        pred = model.predict(user_id, movie_id)
        predictions.append((movie_id, pred.est))
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:top_n]

# Get movie titles
def get_movie_titles(movie_ids, db_path="database.db"):
    conn = sqlite3.connect(db_path)
    movie_ids = [int(id) for id in movie_ids]
    placeholder = ",".join("?" for _ in movie_ids)
    
    query = f"SELECT movie_id, title FROM Movies WHERE movie_id IN ({placeholder})"
    cur = conn.cursor()
    cur.execute(query, tuple(movie_ids))
    rows = cur.fetchall()
    conn.close()
    
    return {movie_id: title for movie_id, title in rows}

# Get popular movies for cold start or fallback
def get_popular_movies(n=10, db_path="database.db"):
    conn = sqlite3.connect(db_path)
    query = "SELECT movie_id, title FROM Movies ORDER BY movie_id LIMIT ?"
    cur = conn.cursor()
    cur.execute(query, (n,))
    rows = cur.fetchall()
    conn.close()
    
    return {movie_id: title for movie_id, title in rows}

# Display recommendations for a user
def display_recommendations(user_id, top_preds):
    print(f"\n🎥 ML Recommendations for User {user_id}:\n")
    if not top_preds:
        print("No recommendations available. Here are some popular movies to check out:")
        popular_movies = get_popular_movies(n=10)
        for i, (movie_id, title) in enumerate(popular_movies.items(), 1):
            print(f"{i}. {title}")
    else:
        for i, (movie_id, rating) in enumerate(top_preds, 1):
            print(f"{i}. {titles.get(movie_id)}  👉 Predicted Rating: {round(rating, 2)}")

if __name__ == "__main__":
    user_id = int(input("Enter user ID: "))
    ratings_df = load_ratings_from_db()
    data = prepare_surprise_data(ratings_df)
    model = train_model(data)

    # Get top recommendations
    top_preds = recommend_movies(user_id, model, ratings_df)
    movie_ids = [mid for mid, _ in top_preds]
    titles = get_movie_titles(movie_ids)
    
    # Display recommendations
    display_recommendations(user_id, top_preds)

# ... all your functions remain the same ...

# New function to get recommendations in one call
def get_ml_recommendations(user_id, db_path="database.db", top_n=10):
    ratings_df = load_ratings_from_db(db_path)
    data = prepare_surprise_data(ratings_df)
    model = train_model(data)
    
    top_preds = recommend_movies(user_id, model, ratings_df, top_n=top_n)
    movie_ids = [mid for mid, _ in top_preds]
    titles = get_movie_titles(movie_ids, db_path)
    
    return [(titles.get(mid), rating) for mid, rating in top_preds]