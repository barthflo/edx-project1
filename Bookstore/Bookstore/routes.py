import jwt
from Bookstore import app, db, bcrypt
from flask import render_template, url_for, redirect, flash, request, session, abort, jsonify, json
from Bookstore.forms import LoginForm, RegisterForm, UpdateUserForm, RequestResetForm, SearchForm, SubmitReviewForm
from Bookstore.functions import register_user, save_picture, user_update, log_user, reset_pwd_request, most_reviewed, recent_review, review_counts_res, search_results, book_description, same_author, strip, current_time

# ---------------------- Home Page--------------------
@app.route("/", methods=['GET', 'POST'])
def home():
    books = most_reviewed()
    reviews = recent_review()
    search = SearchForm()
    if 'user' in session:
        return render_template("home.html", title="Home", user=session['user'], books=books, reviews=reviews, searchform=search)
    return render_template('home.html', title="Home", books=books, reviews=reviews, searchform=search)


@app.route("/test")
def test():
    return None

# ---------------------- Search Page ---------------------------
@app.route("/search", methods=['POST', 'GET'])
def search():
    searchform = SearchForm()
    if request.method == 'POST':
        try :
            # Search database for results matching the search
            isbns = db.execute(
            f"SELECT isbn FROM Books WHERE title ILIKE '%{searchform.search.data}%' OR author ILIKE '%{searchform.search.data}%' OR isbn LIKE '%{searchform.search.data}%' OR year='{searchform.search.data}' ORDER BY title ASC").fetchall()
        except:
            if 'user' in session:
                return render_template('search.html', title="Search", searchform=searchform, message=(f"No results. Please try again"), user=session['user'])
            return render_template('search.html', title="Search", searchform=searchform, message=(f"No results. Please try again"))
        # If no results found return to no result page :
        if (len(isbns) == 0) or (len(isbns) > 350):
            if 'user' in session:
                return render_template('search.html', title="Search", searchform=searchform, message=(f"No results. Please try again"), user=session['user'])
            return render_template('search.html', title="Search", searchform=searchform, message=(f"No results. Please try again"))
        # If results are found, save in a session for reordering the results by title, author, rate etc..
        session['results'] = search_results(isbns)
        if 'user' in session:
            return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=session['results'])
        return render_template('search.html', title="Search", searchform=searchform, books=session['results'])
    # Clear the result session when search page is accessed throught GET
    #session.pop('results', None)
    if 'user' in session:
        return render_template('search.html', title="Search", searchform=searchform, user=session['user'])
    return render_template('search.html', title="Search", searchform=searchform)


@app.route("/search/titleASC")
def order_by_title():
    searchform = SearchForm()
    if 'user' in session:
        return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=session['results'])
    return render_template('search.html', title="Search", searchform=searchform, books=session['results'])


@app.route("/search/authorASC")
def order_by_author():
    searchform = SearchForm()
    author_order = sorted(session['results'], key=lambda x: x[3])
    if 'user' in session:
        return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=author_order)
    return render_template('search.html', title="Search", searchform=searchform, books=author_order)


@app.route("/search/yearASC")
def order_by_year():
    searchform = SearchForm()
    year_order = sorted(session['results'], key=lambda x: x[4])
    if 'user' in session:
        return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=year_order)
    return render_template('search.html', title="Search", searchform=searchform, books=year_order)


@app.route("/search/rate_low_to_high")
def order_by_rate_low():
    searchform = SearchForm()
    low_to_high = sorted(session['results'], key=lambda x: x[5])
    if 'user' in session:
        return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=low_to_high)
    return render_template('search.html', title="Search", searchform=searchform, books=low_to_high)


@app.route("/search/rate_hight_to_low")
def order_by_rate_high():
    searchform = SearchForm()
    high_to_low = sorted(session['results'], key=lambda x: x[5], reverse=True)
    if 'user' in session:
        return render_template('search.html', title="Search", user=session['user'], searchform=searchform, books=high_to_low)
    return render_template('search.html', title="Search", searchform=searchform, books=high_to_low)

# ---------------------- Book Details --------------------
@app.route("/book/<string:book_title>/id:<int:book_id>", methods=['POST', 'GET'])
def book(book_title, book_id):
    search = SearchForm()
    review = SubmitReviewForm()
    login = LoginForm()
    book = db.execute("SELECT * FROM Books WHERE id=:id",
                      {'id': book_id}).fetchone()
    description = book_description(book.title, book.author)
    author = same_author(book)
    recents = db.execute(f"SELECT * FROM Users JOIN Reviews ON Reviews.user_id=Users.id WHERE book_id IN (SELECT id FROM Books WHERE id={book_id})").fetchall()
    recents.sort(reverse=True)
    now=current_time()
    if 'user' in session:
        # Check if user already left a review
        edit = db.execute(
            f"SELECT book_id FROM Reviews WHERE user_id={session['user'].id} AND book_id={book_id}").fetchall()
        if len(edit) > 0:
            return render_template('book.html', title=book_title, searchform=search, book=book, author=author, description=description, edit=edit, recents=recents, user=session['user'])
        if request.method == "POST" and review.validate():
            db.execute(
                "INSERT INTO Reviews (body_text, rating, datetime, book_id, user_id) VALUES (:body_text, :rating, :datetime, :book_id, :user_id)", 
                {"body_text" : review.review.data, "rating": review.rating.data, "datetime": now , "book_id":book_id, "user_id": session['user'].id})
            # Add review count to book database
            db.execute ("UPDATE Books SET review_count = review_count + 1 WHERE id=:id", {"id": book_id})
            db.commit()
            flash (f'Your review has been post', 'success')
            return redirect(url_for('book', book_title=book.title, book_id=book.id))
        return render_template('book.html', title=book_title, searchform=search, book=book, author=author, description=description, review=review, recents=recents, user=session['user'])
    if request.method == "POST" and login.validate():
        log_user(login)
        return redirect(url_for('book', book_title=book.title, book_id=book.id))
    return render_template('book.html', title=book_title, form=login, searchform=search, book=book, author=author, description=description, recents=recents)

# ---------------------- Register a new User--------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if 'user' in session:
        abort(401)
    search = SearchForm()
    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        return register_user(form)
    return render_template('register.html', title="Sign Up", form=form, searchform=search)

# ---------------------- Login a User --------------------
@app.route("/login", methods=['POST', 'GET'])
def login():
    if 'user' in session:
        abort(401)
    form = LoginForm()
    requestForm = RequestResetForm()
    search = SearchForm()
    if request.method == "POST" and form.validate():
        log_user(form)
        return redirect(url_for('home'))
    if request.method == "POST" and requestForm.validate():
        return reset_pwd_request(requestForm)
    return render_template('login.html', title="Log In", form=form, requestform=requestForm, searchform=search)

# -------------------------- LogOut ----------------------------
@app.route("/logout")
def logout():
    if 'user' in session:
        session.pop('user', None)
        flash("You have been logged out. See you next time!", "success")
        return redirect(url_for('home'))
    else:
        abort(404)

# --------------------- Delete account --------------------------
@app.route("/delete", methods=['GET','POST'])
def delete_account():
    if 'user' in session:
        user = session['user']
        # log user out
        session.pop('user', None)
        # delete all datas from db
        db.execute(f"DELETE FROM Users WHERE id='{user.id}'")
        db.commit()
        flash(f"Your account have been deleted", "info")
        return redirect(url_for('register'))
    else:
        abort(404)

# ---------------------- User Account ---------------------------
@app.route("/Profile/<username>", methods=["GET", "POST"])
def user_account(username):
    if 'user' not in session:
        flash("You need to login first", "danger")
        return redirect(url_for('login'))
    else:
        form = UpdateUserForm()
        search = SearchForm()
        if request.method == 'POST' and form.validate():
            return user_update(form, session['user'])
        elif request.method == 'GET':
            user = session['user']
            form.username.data = user.username
            form.email.data = user.email
        return render_template('profile.html', title="Your Profile", user=session['user'], form=form, searchform=search)

@app.route("/Reviews/<username>", methods=["GET", "POST"])
def user_reviews(username):
    if 'user' not in session:
        flash("You need to login first", "danger")
        return redirect(url_for('login'))
    search=SearchForm()
    recents=db.execute(f"SELECT * FROM Books JOIN Reviews ON Reviews.book_id=books.id WHERE user_id={session['user'][0]}").fetchall()  
    return render_template('reviews.html', title="Your Reviews", user=session['user'], searchform=search, recents=recents )

# ----------------- Password Reset Request ------------
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if 'user' in session:
        return redirect(url_for('home'))
    try:
        username = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[
                              'HS256'])['reset_password']
    except:
        flash(f'Link invalid or expired.', 'danger')
        return redirect(url_for('home'))
    if username:
        user = db.execute(
            f"SELECT * FROM Users WHERE username=:username", {'username': username}).fetchone()
        form = UpdateUserForm()
        search = SearchForm()
        if request.method == 'POST' and form.validate():
            hashed_pw = bcrypt.generate_password_hash(
                form.new_password.data).decode('utf-8')
            db.execute(f"UPDATE Users SET password='{hashed_pw}'")
            db.commit()
            # log user
            session['user'] = user
            flash(
                f"Welcome back {session['user'][1]}! Your password has been reset and you are now connected!", "success")
            return redirect(url_for('user_account', username=user.username))
    return render_template('reset_password.html', title="Reset Password", user=user, form=form, searchform=search)

# ---------------- API Route --------------------------
@app.route("/api/<string:isbn>")
def book_api(isbn):
    books=db.execute("SELECT * FROM Books WHERE isbn=:isbn", {'isbn':isbn}).fetchall()
    if len(books) != 1 :
        return jsonify({"error": "Invalid book isbn"}), 422
    print(books)
    for book in books:
        return jsonify({
            "isbn" : isbn,
            "title": book['title'],
            "author":book['author'],
            "year": book['year'],
            "average_score": book.average_rating,
            "review_count": book.review_count
        })

@app.route("/api")
def api():
    if 'user' not in session :
        abort(403)
    search=SearchForm()
    return render_template('api.html', user=session['user'], searchform=search)