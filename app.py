from flask import Flask, render_template, request, redirect, url_for
import requests
import difflib
import os

app = Flask(__name__)
TMDB_API_KEY = "483a8d6b53d5bb68c110d2c17aa6d725"

def search_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    return response.json().get('results', [])

def get_movie_details(tmdb_id, media_type='movie'):
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json()

def get_top_imdb_movies():
    url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    return response.json().get('results', [])

@app.route('/')
def home():
    trending_movies = get_top_imdb_movies()[:6]
    trending_series = search_tmdb('series')[:6]
    trending_anime = search_tmdb('anime')[:6]
    return render_template('home.html', movies=trending_movies, series=trending_series, anime=trending_anime)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    results = search_tmdb(query)
    if not results:
        all_titles = [r['title'] for r in search_tmdb(' ')]
        corrected = difflib.get_close_matches(query, all_titles, n=1, cutoff=0.6)
        if corrected:
            results = search_tmdb(corrected[0])
    return render_template('search.html', results=results)

@app.route('/watch/<media_type>/<int:tmdb_id>')
def watch(media_type, tmdb_id):
    details = get_movie_details(tmdb_id, media_type)
    return render_template('watch.html', details=details, media_type=media_type, tmdb_id=tmdb_id)

if __name__ == '__main__':
    app.run(debug=True)
