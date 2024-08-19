from flask import Flask, render_template, redirect, url_for, request, Markup
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True)
    year = db.Column(db.Integer)
    description = db.Column(db.Text)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.Text)
    img_url = db.Column(db.String(255))

class RateMovieForm(FlaskForm):
  rating = StringField("Your Rating Out of 10 e.g. 7.5")
  review = StringField("Your Review")
  submit = SubmitField("Done")

class AddMovieForm(FlaskForm):
  title = StringField("Title", validators=[DataRequired()])
  submit = SubmitField("Add Movie")

def search_movie(query):
  TMDB_API = "https://api.themoviedb.org/3/search/movie"
  TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
  headers = {
    "accept": "application/json",
    "Authorization": F"Bearer {TMDB_API_KEY}",
    "query": query
    }
  response = requests.get(TMDB_API, headers=headers)
  data = response.json()["results"]
  print(data)
  return data

@app.route("/")
def home():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete_movie():
    movie_id = request.args.get("id")
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddMovieForm()
    if form.validate_on_submit():
        title = form.title.data
        movie = Movie(title=title)
        db.session.add(movie)
        db.session.commit()
        options = search_movie(movie)
        return render_template("select.html", optios=options)
    return render_template("add.html", form=form)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080, debug=True)

