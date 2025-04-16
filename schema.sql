-- USERS
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY
);

-- MOVIES
CREATE TABLE Movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT,
    year INTEGER
);

-- GENRES
CREATE TABLE Genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);

-- MOVIE-GENRES (Many-to-many)
CREATE TABLE MovieGenres (
    movie_id INTEGER,
    genre_id INTEGER,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id),
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
);

-- RATINGS
CREATE TABLE Ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_id INTEGER,
    rating REAL,
    timestamp TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
);
