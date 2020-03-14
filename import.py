import os
import csv

from flask import Flask, render_template, request
from model import *
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db.init_app(app)


def data():
    file=open("books.csv")
    reader=csv.reader(file)
    for isbn, title, author, year in reader:
        book=Books(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print (f"Added book ref {isbn}: {title} from {author} published in {year} .")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        data()