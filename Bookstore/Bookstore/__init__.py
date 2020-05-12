import os
from flask_mail import Mail
from flask import Flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt


app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure secret key
app.config["SECRET_KEY"]="91fc466a78e3b7f356c7046f35bf9ee1"

# Configure Goodread API key
app.config["GOODREAD_API_KEY"]='Uq6qdoFIWruPeMilwCmhA'

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Mail Server
app.config["MAIL_SERVER"]='smtp.googlemail.com'
app.config["MAIL_PORT"]=587 
app.config["MAIL_USE_TLS"]=1
app.config["MAIL_USERNAME"]=os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]=os.getenv("MAIL_PASSWORD")
mail=Mail(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Password hash
bcrypt=Bcrypt(app)

from Bookstore import routes
