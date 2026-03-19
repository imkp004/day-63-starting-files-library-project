# ----- Use python 3.12 --------
from flask import Flask, render_template, redirect, url_for, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, NumberRange

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# ----- Creating the app --------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'



# ----- Creating the Database --------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
db = SQLAlchemy(app)

class Book_database(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[int] = mapped_column(Float, nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'

with app.app_context():
    db.create_all()


# ----- Creating the WTforms and using the objects in html by Jinja --------
class Book_form(FlaskForm):
    book = StringField(label='Book Name', validators=[DataRequired()])
    author = StringField(label='Book Author', validators=[DataRequired()])
    rating = IntegerField(label='Rating', validators=[NumberRange(min=0, max=10)])
    submit = SubmitField('Add Book')

class edit_form(FlaskForm):
    rating = IntegerField(label='Rating', validators=[NumberRange(min=0, max=10)])
    id = HiddenField()
    submit = SubmitField('Update')

# ------- rendering the index.html at home page with the data of books from the --------------
# ------- database which is list of each object = each rows --------------
@app.route('/')
def home():
    # ------ Old Method ------
    # books = Book_database.query.all()

    # ------ New Method ------
    # Read A Particular Record By Query
    # with app.app_context():
    #     book = db.session.execute(db.select(Book_database).where(Book_database.title == "Harry Potter")).scalar()
    # To get a single element we can use scalar() instead of scalars().

    result = db.session.execute(db.select(Book_database).order_by(Book_database.title))
    all_books = result.scalars()
    return render_template('index.html', data=all_books)


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


@app.route("/edit", methods=['GET','POST'])
def edit_rating():

    form = edit_form()

    if form.validate_on_submit():
        # Update A Particular Record By Query
        # with app.app_context():
        #     book_to_update = db.session.execute(db.select(Book).where(Book.title == "Harry Potter")).scalar()
        #     book_to_update.title = "Harry Potter and the Chamber of Secrets"
        #     db.session.commit()
        #
        #
        # Update A Record By PRIMARY KEY
        # book_id = 1
        # with app.app_context():
        #     book_to_update = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
        #     # or book_to_update = db.get_or_404(Book, book_id)
        #     book_to_update.title = "Harry Potter and the Goblet of Fire"
        #     db.session.commit()

        # Did same thing as below
        book_id = form.id.data
        book_to_update = db.get_or_404(Book_database, book_id)

        book_to_update.rating = form.rating.data
        db.session.commit()
        return redirect(url_for('home'))

    # Did same thing as above
    id = request.args.get("id", type=int)
    book = db.session.execute(db.select(Book_database).where(Book_database.id == id)).scalar()

    form.id.data = book.id
    return render_template('edit.html', book=book, form=form)


@app.route("/delete")
def delete():
    id = request.args.get("id", type=int)
    book_to_delete = db.session.execute(db.select(Book_database).where(Book_database.id == id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(url_for('home'))
    # Delete A Particular Record By PRIMARY KEY
    # book_id = 1
    # with app.app_context():
    #     book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    #     # or book_to_delete = db.get_or_404(Book, book_id)
    #     db.session.delete(book_to_delete)
    #     db.session.commit()




if __name__ == "__main__":
    app.run(debug=True, port=5001)

