from flask import Flask, render_template, request
import requests
import difflib

app = Flask(__name__)

# Your TMDB API key
TMDB_API_KEY = 'your_tmdb_api_key_here'

def search_tmdb(query):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def get_details(content_type, content_id):
    url = f"https://api.themoviedb.org/3/{content_type}/{content_id}?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return {}

def get_trending(content_type='movie'):
    url = f"https://api.themoviedb.org/3/trending/{content_type}/week?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

@app.route('/')
def home():
    trending_movies = get_trending('movie')[:6]
    trending_series = get_trending('tv')[:6]
    trending_anime = get_trending('tv')[:6]  # anime section, improve if you add anilist later
    return render_template('home.html', trending_movies=trending_movies, trending_series=trending_series, trending_anime=trending_anime)

@app.route('/search')
def search():
    query = request.args.get('query')
    results = search_tmdb(query)

    if not results and query:
        close_match = difflib.get_close_matches(query, [r.get('title', '') for r in results], n=1)
        if close_match:
            results = search_tmdb(close_match[0])
    return render_template('search.html', results=results, query=query)

@app.route('/watch/<content_type>/<int:content_id>')
def watch(content_type, content_id):
    details = get_details(content_type, content_id)

    # Generate stream link
    if content_type == 'movie':
        stream_link = f"https://multiembed.mov/?video_id={content_id}&tmdb=1"
    else:
        stream_link = f"https://multiembed.mov/?video_id={content_id}&tmdb=1"

    return render_template('watch.html', details=details, stream_link=stream_link)

if __name__ == '__main__':
    app.run(debug=True)
