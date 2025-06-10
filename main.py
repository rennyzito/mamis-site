# from dotenv import load_dotenv
# load_dotenv()

from flask import Flask, render_template, request, flash, redirect, url_for
import requests
from post import Post
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TelField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_bootstrap import Bootstrap5
import os
import smtplib

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


class ContactForm(FlaskForm):
    name = StringField(label="Nome Completo", validators=[DataRequired()])
    email = EmailField(label="Email", validators=[DataRequired()])
    phone = TelField(label="Telefone", validators=[DataRequired(), Length(min=8)])
    text = TextAreaField(label="Mensagem", validators=[DataRequired()])
    submit = SubmitField(label="Enviar")


def send_email(name, email, phone, text):
    # Retrieve values from environment variables
    sender_email = os.environ.get("GMAIL_ADDRESS")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("MOM_EMAIL")

    # Basic check to ensure environment variables are set
    if not sender_email or not sender_password or not receiver_email:
        print("Error: Email credentials or receiver email not set as environment variables.")
        flash('Erro de configuração do servidor de e-mail.', 'danger')
        return

    message = f"Subject: Nova mensagem de contato do site!\n\nNome: {name}\nEmail: {email}\nTelefone: {phone}\nMensagem:\n{text}"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
        print("Email sent successfully!")
        flash('Mensagem enviada com sucesso!', 'success')
    except Exception as e:
        print(f"Error sending email: {e}")
        flash('Erro ao enviar a mensagem.', 'danger')


@app.route('/', methods=["GET", "POST"])
def home():
    contactform = ContactForm()
    if contactform.validate_on_submit():
        name = contactform.name.data
        email = contactform.email.data
        phone = contactform.phone.data
        text = contactform.text.data

        send_email(name, email, phone, text)  # Call the send_email function
        return redirect(url_for('home')) # Redirect to avoid resubmission
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
