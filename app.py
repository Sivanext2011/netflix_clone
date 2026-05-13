from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Load movie data
with open('movie_data.json') as f:
    movies = json.load(f)

@app.route('/')
def home():
    return render_template('index.html', title="Netflix Clone", movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_details(movie_id):
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if movie:
        return render_template('movie.html', title=movie['title'], movie=movie)
    return "Movie not found", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    results = [m for m in movies if query in m['title'].lower()]
    return render_template('search.html', title="Search Results", results=results)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
