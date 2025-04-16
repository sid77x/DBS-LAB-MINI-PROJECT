import sqlite3
import pandas as pd
import re

movies_df = pd.read_csv("data/movies.csv")
ratings_df = pd.read_csv("data/ratings.csv")


conn = sqlite3.connect("database.db")
cursor = conn.cursor()


with open("schema.sql", "r") as f:
    cursor.executescript(f.read())
conn.commit()

user_ids = ratings_df['userId'].unique()
cursor.executemany("INSERT INTO Users (user_id) VALUES (?)", [(int(uid),) for uid in user_ids])
conn.commit()


all_genres = set()
for genre_str in movies_df['genres']:
    all_genres.update(genre_str.split('|'))
genre_map = {}
for genre in all_genres:
    cursor.execute("INSERT INTO Genres (name) VALUES (?)", (genre,))
    genre_map[genre] = cursor.lastrowid
conn.commit()

for _, row in movies_df.iterrows():
    movie_id = row['movieId']
    title = row['title']
    year_match = re.search(r"\((\d{4})\)", title)
    year = int(year_match.group(1)) if year_match else None
    clean_title = re.sub(r"\(\d{4}\)", "", title).strip()

    cursor.execute("INSERT INTO Movies (movie_id, title, year) VALUES (?, ?, ?)",
                   (movie_id, clean_title, year))

    genres = row['genres'].split('|')
    for g in genres:
        cursor.execute("INSERT INTO MovieGenres (movie_id, genre_id) VALUES (?, ?)",
                       (movie_id, genre_map[g]))
conn.commit()

ratings_to_insert = ratings_df[['userId', 'movieId', 'rating', 'timestamp']].values.tolist()
cursor.executemany(
    "INSERT INTO Ratings (user_id, movie_id, rating, timestamp) VALUES (?, ?, ?, ?)",
    ratings_to_insert
)
conn.commit()

print("✅ Database setup and data import complete.")
conn.close()
