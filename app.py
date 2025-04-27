from flask import Flask, render_template, request, redirect, url_for
import requests
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)

# TMDb API (replace 'YOUR_TMDB_API_KEY' with your real key)
TMDB_API_KEY = '483a8d6b53d5bb68c110d2c17aa6d725'

def search_tmdb(query):
    url = f'https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}'
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()['results']
        movies = []
        for item in results:
            if item.get('media_type') in ['movie', 'tv']:
                movies.append({
                    'id': item['id'],
                    'title': item.get('title') or item.get('name'),
                    'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else '/static/no-image.png',
                    'overview': item.get('overview', 'No overview available'),
                    'year': (item.get('release_date') or item.get('first_air_date', ''))[:4]
                })
        return movies
    return []

def get_movie_details(movie_id, media_type):
    url = f'https://api.themoviedb.org/3/{media_type}/{movie_id}?api_key={TMDB_API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'title': data.get('title') or data.get('name'),
            'overview': data.get('overview', ''),
            'year': (data.get('release_date') or data.get('first_air_date', ''))[:4],
            'poster': f"https://image.tmdb.org/t/p/w500{data.get('poster_path')}" if data.get('poster_path') else '/static/no-image.png'
        }
    return {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    results = search_tmdb(query)
    # Fuzzy match if nothing found
    if not results and query:
        common_titles = ["One Piece", "Naruto", "Demon Slayer", "Breaking Bad", "Game of Thrones", "Interstellar", "Inception"]
        closest_match = process.extractOne(query, common_titles)
        if closest_match and closest_match[1] > 60:
            results = search_tmdb(closest_match[0])
    return render_template('search.html', query=query, results=results)

@app.route('/watch/<int:movie_id>')
def watch(movie_id):
    # Try both movie and tv type to be safe
    details = get_movie_details(movie_id, 'movie')
    if not details:
        details = get_movie_details(movie_id, 'tv')

    # Example Embed links with fallback
    embed_link = f"https://vidsrc.to/embed/movie/{movie_id}"  # fallback 1
    embed_link_tv = f"https://vidsrc.to/embed/tv/{movie_id}/1/1"  # fallback 2

    return render_template('watch.html', details=details, movie_id=movie_id, embed_link=embed_link, embed_link_tv=embed_link_tv)

if __name__ == '__main__':
    app.run(debug=True)
