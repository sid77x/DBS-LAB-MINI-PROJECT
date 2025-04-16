from flask import Flask, render_template, request
import sqlite3
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import requests
import random

# Function to fetch poster path from TMDb API
def fetch_poster_path(title):
    api_key = '3775e069e6e81ef8539ccc537185eea5'
    url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={title}'
    response = requests.get(url).json()
    if response['results']:
        return response['results'][0].get('poster_path')
    return None

# Function to fetch trending movies from TMDb
def fetch_trending_movies():
    api_key = '3775e069e6e81ef8539ccc537185eea5'
    url = f'https://api.themoviedb.org/3/trending/movie/day?api_key={api_key}'
    response = requests.get(url).json()
    trending_movies = []
    for movie in response['results']:
        trending_movies.append({
            'title': movie['title'],
            'poster_path': movie['poster_path'],
            'id': movie['id']
        })
    return trending_movies

def fetch_featured_movie():
    api_key = '3775e069e6e81ef8539ccc537185eea5'
    # Here you can pick a movie manually or randomly for "featured" (for now, picking a random trending movie)
    trending_movies = fetch_trending_movies()
    featured_movie = random.choice(trending_movies)  # Pick a random movie from trending movies
    return featured_movie


app = Flask(__name__)

# Route for the homepage

@app.route('/')
def index():
    trending_movies = fetch_trending_movies()
    featured_movie = fetch_featured_movie()
    
    return render_template('index.html', trending_movies=trending_movies, featured_movie=featured_movie)



# Route to display recommendations
from recommender_sql import get_recommendations
from recommender_ml import (
    get_ml_recommendations,
    load_ratings_from_db,
    prepare_surprise_data,
    train_model,
    recommend_movies,
    get_movie_titles
)

@app.route('/recommend', methods=['POST'])
def recommend():
    user_id = int(request.form['user_id'])

    # --- ML Recommendations ---
    ratings_df = load_ratings_from_db()
    data = prepare_surprise_data(ratings_df)
    model = train_model(data)
    ml_preds = get_ml_recommendations(user_id)  # returns list of (title, predicted_rating)

    ml_results = [
    {
        "title": title,
        "predicted_rating": round(pred, 2),
        "poster_path": fetch_poster_path(title)
    }
    for title, pred in ml_preds
]
    # --- SQL Recommendations ---
    sql_preds = get_recommendations(user_id)
    sql_movie_ids = [mid for mid, _ in sql_preds]
    sql_titles = get_movie_titles(sql_movie_ids)

    # Fetch poster paths for SQL-based recommendations
    sql_poster_paths = {}
    for movie_id in sql_movie_ids:
        movie_title = sql_titles[movie_id]
        poster_path = fetch_poster_path(movie_title)
        sql_poster_paths[movie_id] = poster_path

    return render_template(
        'recommendations.html',
        user_id=user_id,
        ml_results=ml_results,
        sql_preds=sql_preds,
        sql_titles=sql_titles,
        sql_poster_paths=sql_poster_paths  # Pass poster paths to the template
    )

if __name__ == '__main__':
    app.run(debug=True)
