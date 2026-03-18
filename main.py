# ----- Use python 3.12 --------
from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_sqlalchemy import SQLAlchemy


# ----- Creating the app --------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'



# ----- Creating the Database --------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
db = SQLAlchemy(app)

class Book_database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()



# ----- Creating the WTforms and using the objects in html by Jinja --------
class Book_form(FlaskForm):
    book = StringField(label='Book Name', validators=[DataRequired()])
    author = StringField(label='Book Author', validators=[DataRequired()])
    rating = IntegerField(label='Rating', validators=[NumberRange(min=0, max=10)])
    submit = SubmitField('Add Book')


# ------- rendering the index.html at home page with the data of books from the --------------
# ------- database which is list of each object = each rows --------------
@app.route('/')
def home():
    books = Book_database.query.all()
    return render_template('index.html', data=books)


# ------- add data inside the database by POSRT method once the submit button -------
# ------- is pressed --------------
@app.route("/add", methods=['GET','POST'])
def add():
    form = Book_form()

    if form.validate_on_submit():
        new_book = Book_database(title=form.book.data, author=form.author.data, rating=form.rating.data)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)

