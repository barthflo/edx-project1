from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class Books(db.Model):
    __tablename__="books"
    id=db.Column(db.Integer, primary_key=True)
    isbn=db.Column(db.Text, nullable=False)
    title=db.Column(db.String, nullable=False)
    author=db.Column(db.String, nullable=False)
    year=db.Column(db.Integer, nullable=False)