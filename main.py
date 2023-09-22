from flask import Flask, render_template, request
import requests
from post import Post
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TelField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
import os


URL = os.environ.get("ARTICLE_DATA", "https://api.npoint.io/7e05301098625b40878d")
article_data = requests.get(URL).json()

post_objects = []
for post in article_data:
    post_obj = Post(
        post["id"], post["titulo"], post["autor"], post["subtitulo"], post["imagem_url"], post["date"], post["intro"],
        post["subtitulo1"], post["corpo1"], post["subtitulo2"], post["corpo2"], post["subtitulo3"], post["corpo3"],
        post["subtitulo4"], post["corpo4"], post["conclu"]
    )
    post_objects.append(post_obj)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_KEY", "mamae-maioral-te-amo")
bootstrap = Bootstrap5(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///contact_db_xza9.db")
db = SQLAlchemy()
db.init_app(app)

##CREATE TABLE
class Contact(db.Table):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# with app.app_context():
#     db.create_all()

class ContactForm(FlaskForm):
    name = StringField(label="Nome Completo", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    phone = TelField(label="Telefone", validators=[DataRequired(), Length(min=8)])
    text = TextAreaField(label="Mensagem", validators=[DataRequired()])
    submit = SubmitField(label="Enviar")


@app.route('/', methods=["GET", "POST"])
def home():
    contactform = ContactForm()
    if contactform.validate_on_submit():
        name = contactform.name.data
        email = contactform.email.data
        phone = contactform.phone.data
        text = contactform.text.data

        contact_entry = Contact(name=name, email=email, phone=phone, text=text)
        db.session.add(contact_entry)
        db.session.commit()
        return render_template("contactme.html")
    else:
        return render_template("index.html", form=contactform, articles=post_objects)

@app.route('/article/<int:num>')
def get_article(num):
    requested_post = None
    for full_post in post_objects:
        if full_post.id == num:
            requested_post = full_post
    return render_template("artigos.html", full_post=requested_post)

if __name__ == "__main__":
    app.run(debug=False)
