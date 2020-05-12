import os, secrets, jwt, requests, xmltodict, json, pytz
from threading import Thread
from flask_mail import Message
from time import time
from datetime import datetime
from PIL import Image 
from flask import flash, redirect, url_for, session, render_template, jsonify
from Bookstore import db, bcrypt, app, mail
from bs4 import BeautifulSoup



# ---------- SEND EMAIL FUNCTIONS ----------------
#-----------  Send Asynchrous Email --------------
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#---------------- Send an Email ------------------
def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

#             ---------------------



# --------- USER SESSION FUNCTIONS ---------------
# ----------- Register New User ------------------
def register_user(register_form):
    # hash password for security
    hashed_pw = bcrypt.generate_password_hash(register_form.password.data).decode('utf-8')
    # check if username and email are unique
    usernames = db.execute("SELECT username FROM Users WHERE username=:username", {
                        'username': register_form.username.data}).fetchone()
    emails = db.execute("SELECT email FROM Users WHERE email=:email", {
                        'email': register_form.email.data}).fetchone()
    if usernames:
        flash('Username is already taken. Please chose another one', 'danger')
        return redirect(url_for('register'))
    if emails:
        flash('Email address is already taken. Please chose another one', 'danger')
        return redirect(url_for('register'))
    else:
        # create user and add to database
        user=db.execute("INSERT INTO Users(username, email, password, avatar) VALUES(:username, :email, :hashed_pw, :avatar)",
            {"username": register_form.username.data, "email": register_form.email.data, "hashed_pw": hashed_pw, "avatar": 'default.jpg'})
        db.commit()
        flash("Your account has been succesfully created. You can now log in!", "success")
        return redirect(url_for('login'))

#---------------- Log User In --------------------
def log_user(login_form):
    # check email exist in database 
    registered_user=db.execute("SELECT * FROM Users WHERE email=:email", {'email': login_form.email.data}).fetchone()
    if registered_user is None :
        flash ("User doesn't exist", 'danger')
        return redirect(url_for('login'))
    #check if password match db
    hashed_pw=db.execute("SELECT password FROM Users WHERE email=:email", {'email': login_form.email.data}).fetchone()
    pw_checked=bcrypt.check_password_hash(f'{hashed_pw[0]}', login_form.password.data)
    if pw_checked is False:
        flash ("Invalid password. Please try again", "danger")
        return redirect(url_for('login'))
    #Redirect if user already logged in
    if session.get('user'):
        flash ("You are already logged in", "danger")
        return redirect(url_for('user_account'))
    #Log user in
    session['user'] = registered_user
    flash (f"Welcome {session['user'][1]}! You are now connected!", "success")
    #return redirect(url_for('home'))
    return session['user']

#------------ Update User Details ----------------
def user_update(form, user):
    # Check new username and email address are not already use
    if form.username.data is not user.username and form.email.data is not user.email:
        username = db.execute("SELECT username FROM Users WHERE username=:username", {'username': form.username.data}).fetchone()
        email = db.execute("SELECT email FROM Users WHERE email=:email", {'email': form.email.data}).fetchone()
        if username:
            flash('Username is already taken. Please chose another one', 'danger')
            return redirect(url_for('user_account', username=session['user'][1]))
        if email:
            flash('Email address is already taken. Please chose another one', 'danger')
            return redirect(url_for('user_account', username=session['user'][1]))
    # ------------ USERNAME -----------
    # Update username in database
    if form.username.data:
        db.execute(f"UPDATE Users SET username='{form.username.data}' WHERE username=:username", {'username' :user.username})
        db.commit()
        flash("Your username has been updated!", "info")
    # ------------ EMAIL -----------
    # Update email in database
    if form.email.data:
        db.execute(f"UPDATE Users SET email='{form.email.data}' WHERE email=:email", {'email' :user.email})
        db.commit()
        flash("Your email address has been updated!", "info")
    # ------------ PASSWORD -----------
    if form.new_password.data:
        #check current password is correct
        hashed_pw=db.execute("SELECT password FROM Users WHERE id=:id", {'id': user.id}).fetchone()
        pw_checked=bcrypt.check_password_hash(f'{hashed_pw[0]}', form.current_password.data)
        if pw_checked is False:
            flash ("Invalid password. Please try again", "danger")
            return redirect(url_for('user_account', username=session['user'][1]))
        #check if new password is new
        if bcrypt.check_password_hash(f'{hashed_pw[0]}', form.new_password.data):
            flash("You are already using this password", "info")
            return redirect(url_for('user_account', username=session['user'][1]))
        # Update password in database
        else:
            # hash password for security
            hashed_pw = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            db.execute(f"UPDATE Users SET password='{hashed_pw}' WHERE password=:password", {'password' :user.password})
            db.commit()
            flash("Your password has been reset", "info")
    # -------------- PICTURE -----------
    if form.picture.data:
        picture_file=save_picture(form.picture.data)
        db.execute(f"UPDATE Users SET avatar='{picture_file}' WHERE id=:id",{'id': user.id})
        db.commit()
    # Query database for updated user and refresh the session variable
    session['user']=db.execute(f"SELECT * FROM Users WHERE id='{user.id}'").fetchone()
    return redirect(url_for('user_account', username=session['user'][1]))

#--------------- Save picture --------------------
def save_picture(form_picture):
    # Rename the file with a random hex
    random_hex=secrets.token_hex(8) #create random hex
    _, f_ext = os.path.splitext(form_picture.filename) #keep the correct extension
    picture_fn = random_hex + f_ext # new filename
    #define the path to save the picture
    picture_path = os.path.join(app.root_path, 'static/image_library/uploads', picture_fn)
    #resize the image
    output_size = (400, 400)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    #save the resized image
    i.save(picture_path)
    return picture_fn


#             --------------------



# --------- FORGOT PASSWORD FUNCTIONS ------------
# ------  Generate unique token for user ---------
def get_reset_password_token(user, expires_in=600):
    return jwt.encode({'reset_password': user.username, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

# ---------- Send Password Reset Email -----------
def send_pwd_reset_email(user):
    token=get_reset_password_token(user)
    send_email('[SecretBooks] Reset Your Password',
               sender=app.config['MAIL_USERNAME'],
               recipients=[user.email],
               html_body=render_template('email/reset_password.html', user=user, token=token))

#----------- Reset Pw Email Request------
def reset_pwd_request(request_form):
    user = db.execute("SELECT * FROM Users WHERE email=:email", {'email': request_form.email.data}).fetchone()
    if user:
        send_pwd_reset_email(user)
        flash(f'An email has been send to you with the instructions to reset your password', "info")
        return redirect(url_for('home'))

#             ---------------------



# -------------- BOOKS FUNCTIONS -----------------
# ---------- Display Most Reviewed Books ---------
def most_reviewed():
    isbns=db.execute("SELECT isbn FROM Books LIMIT 350").fetchall()
    res=review_counts_res(isbns)
    book_counts=res['books']
    book_counts.sort(key=lambda k: k['work_reviews_count'], reverse=True)
    isbn=[] # ----- Create a list of the 6 most reviewed books isbns
    for book in book_counts[0:6]:
        # Check if goodread average is already in db
        avg=db.execute("SELECT average_rating FROM Books WHERE isbn=:isbn", {'isbn':book['isbn']}).fetchone()
        if avg is None :
            # ---- Update database with goodread average rating 
            db.execute("UPDATE Books SET average_rating=:average_rating WHERE isbn=:isbn", {'average_rating':book['average_rating'], 'isbn':book['isbn']})
            db.commit()
        # ---- Add 6 most reviewed isbns to the list
        isbn.append(book['isbn']) 
    # ---- Fetch the 6 most goodread reviewed books from our database  
    isbn=tuple(isbn)
    most_reviewed=db.execute(f"SELECT * FROM Books WHERE isbn IN {isbn}").fetchall()
    return most_reviewed

# ------------- Display Search Result ------------
def search_results(results):
    #Check for goodread average rating
    books=review_counts_res(results)
    updated=[] # Create list of updated rating search
    for book in books['books']:
        # Check if average rating in database is same as goodreads
        avg=db.execute(f"SELECT average_rating FROM Books WHERE isbn='{book['isbn']}'").fetchone()
        if avg[0] is None:
            # Update db if rating is none or different
            db.execute("UPDATE Books SET average_rating=:average_rating WHERE isbn=:isbn", {'average_rating':book['average_rating'], 'isbn':book['isbn']})
            db.commit()
        update=db.execute(f"SELECT * FROM Books WHERE isbn='{book['isbn']}'").fetchone()
        updated.append(update)
    return updated            

# -------   Display Series of same author ---------
def same_author(book):
    isbns=db.execute(f"SELECT isbn FROM Books WHERE author='{book.author}'").fetchall()  # Fetch isbns from books of the same author
    books=search_results(isbns) # Check for goodread average rating and update if necessary
    results=sorted([result for result in books if result != book], key=lambda x:x[2]) #Remove current book from results and reorder by title ASC
    return results
    #return([result for result in books if result != book])
  
#             ---------------------



# ---------- GOODREAD API FUNCTIONS --------------
# ----- Goodread API Review_Counts response ------
def review_counts_res(isbn):
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"Key":app.config['GOODREAD_API_KEY'], "isbns[]": isbn}).json()
    return res

# ----- Goodread API Description of a given title  -----
def book_description(title, author):
    res=requests.get("https://www.goodreads.com/book/title.xml", params={"key":app.config['GOODREAD_API_KEY'], "title":title, "author":author})
    resjson=xmltodict.parse(res.content)
    htmldescription=resjson['GoodreadsResponse']['book']['description']
    description=strip(htmldescription)
    #print (resjson)
    return description

# ----- Goodread API Recent_reviews response -----
def recent_review():
    resxml=requests.get("https://www.goodreads.com/review/recent_reviews.xml", params={"key":app.config['GOODREAD_API_KEY']})
    resjson=xmltodict.parse(resxml.content)
    goodreadResponse=resjson["GoodreadsResponse"]['reviews']
    reviews=goodreadResponse['review']
    return reviews

# ---------- Strip HTML from Strings -----------
def strip(string):
    soup=BeautifulSoup(string, features="lxml")
    return soup.get_text()

# ---------- Get current date and time -----------
def current_time():
    tz_LA= pytz.timezone('America/Los_Angeles')
    now=datetime.now(tz_LA)
    nowstr=now.strftime("%a %B %d ,%Y, %X")
    return nowstr

'''def best_ranked():
    isbn=db.execute("SELECT isbn FROM Books").fetchall()
    res=requests.get("https://www.goodreads.com/book/review_counts.json", params={"Key":app.config['GOODREAD_API_KEY'], "isbns[]": isbn[0:351]}).json()
    book_counts=res['books']
    book_counts.sort(key=lambda k: k['average_rating'], reverse=True)
    isbn=[]
    for book in book_counts:
        isbn.append(book['isbn'])
    t=tuple(isbn[0:6])
    best_ranked=db.execute(f"SELECT * FROM Books WHERE isbn IN {t}").fetchall()
    return best_ranked
'''

    