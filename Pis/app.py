from flask import Flask, request, jsonify, render_template
from pony.orm import Database, Required, PrimaryKey, db_session, select
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

db = Database()
db.bind(provider='sqlite', filename='movie_database.sqlite', create_db=True)


class Movie(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    year_of_publication = Required(int)
    duration = Required(int)
    genre = Required(str)
    description = Required(str)
    grade = Required(float)
    comment = Required(str)


db.generate_mapping(create_tables=True)

@app.route('/movie', methods=['POST'])
@db_session
def add_movie():
    data = request.get_json()
    movie = Movie(
        title=data['title'],
        year_of_publication=data['year_of_publication'],
        duration=data['duration'],
        genre=data['genre'],
        description=data['description'],
        grade=data['grade'],
        comment=data['comment']
    )
    return jsonify(movie.to_dict())


@app.route('/movie/<int:movie_id>', methods=['GET'])
@db_session
def get_movie(movie_id):
    movie = Movie.get(id=movie_id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404
    return jsonify(movie.to_dict())


@app.route('/movie/<int:movie_id>', methods=['PUT'])
@db_session
def update_movie(movie_id):
    data = request.get_json()
    movie = Movie.get(id=movie_id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404

    movie.title = data.get('title', movie.title)
    movie.year_of_publication = data.get('year_of_publication', movie.year_of_publication)
    movie.duration = data.get('duration', movie.duration)
    movie.genre = data.get('genre', movie.genre)
    movie.description = data.get('description', movie.description)
    movie.grade = data.get('grade', movie.grade)
    movie.comment = data.get('comment', movie.comment)

    return jsonify(movie.to_dict())


@app.route('/movie/<int:movie_id>', methods=['DELETE'])
@db_session
def delete_movie(movie_id):
    movie = Movie.get(id=movie_id)
    if movie is None:
        return jsonify({"error": "Movie not found"}), 404
    movie.delete()
    return jsonify({"success": f"Movie {movie_id} deleted"})


@app.route('/movies', methods=['GET'])
@db_session
def get_all_movies():
    genre = request.args.get('genre')
    grade = request.args.get('grade')
    
    query = select(m for m in Movie)
    
    if genre:
        query = query.where(lambda m: m.genre == genre)
    
    if grade:
        try:
            grade = float(grade)
            query = query.where(lambda m: m.grade == grade)
        except ValueError:
            return jsonify({"error": "Invalid grade value"}), 400

    movies = query[:]
    
    return jsonify([m.to_dict() for m in movies])

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000 , debug=True)
