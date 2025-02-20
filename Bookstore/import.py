import os 
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def import_book():
    f=open("books.csv")
    reader=csv.reader(f)
    for isbn, title, author, year in reader:
        if isbn != 'isbn':
            db.execute("INSERT INTO Books (isbn,title, author, year) VALUES(:isbn, :title, :author, :year)",
                {"isbn":isbn, "title":title, "author":author, "year":year})
            print (f"Book {title} added to database")
            db.commit()

if __name__=="__main__":
    import_book()  






