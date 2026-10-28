import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)




@app.route("/", methods=['GET','POST'])
def home():
    # a linha a seguir verifica se o formulário não está vazio
    if request.form :
        try:
            title = request.form.get("title")

            if not title:
                raise Exception("O título não pode ser vazio")

            book = Book(title=request.form.get("title"))
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
        newtitle = request.form.get('newtitle')
        oldtitle = request.form.get('oldtitle')

        if not newtitle or not newtitle.strip():
            raise Exception('Escreva um novo título')

        book = Book.query.filter_by(title=oldtitle).first()

        if not book:
            raise Exception('Livro não encontrado')

        book.title = newtitle.strip()
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(e)

    return redirect(url_for('home'))



@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
