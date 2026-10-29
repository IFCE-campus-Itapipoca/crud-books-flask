import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, "bookdatabase.db")
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)


class Book(db.Model):
    title = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        primary_key=True
    )

    def __repr__(self):
        return "<Title: {}>".format(self.title)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()

            if not title:
                raise ValueError("O título não pode ser vazio.")

            if Book.query.filter_by(title=title).first():
                raise ValueError("Esse livro já está cadastrado.")

            book = Book(title=title)
            db.session.add(book)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print("Houve uma falha na inserção desse livro.")
            print(e)

    books = Book.query.all()
    return render_template("home.html", books=books)


@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle", "").strip()
        oldtitle = request.form.get("oldtitle", "")

        if not newtitle:
            raise ValueError("Escreva um novo título.")

        book = Book.query.filter_by(title=oldtitle).first()

        if not book:
            raise ValueError("Livro não encontrado.")

        # Verifica se o novo título já pertence a outro livro
        existing_book = Book.query.filter_by(title=newtitle).first()

        if existing_book and existing_book.title != oldtitle:
            raise ValueError("Já existe um livro com esse título.")

        book.title = newtitle
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Houve uma falha na atualização do livro.")
        print(e)

    return redirect(url_for("home"))


@app.route("/delete", methods=["POST"])
def delete():
    try:
        title = request.form.get("title", "")
        book = Book.query.filter_by(title=title).first()

        if not book:
            raise ValueError("Livro não encontrado.")

        db.session.delete(book)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print("Houve uma falha na exclusão do livro.")
        print(e)

    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
