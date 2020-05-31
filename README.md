# Project 1

Web Programming with Python and JavaScript

Flask App for a book review website for the project 1 of edx online course.

The app features :

Home page presenting the website and including the most reviewed books of the moment and the latest reviews from the Goodreads api.

Search page displaying results of a research in the book database in which the results can be rearrange by title, author, year, and best or worst reviews oming first

Book page showing the details of the book, including author, date and average rating, a description of the book story from goodreads, and links to other books from the same author if available. In addition to that, if the user is logged in its personnal account, he can submit a review if he hadn't left one already. If the user is not logged in, a link invites him to log in or register an account.

Login page when the user is not in session consisting of a username and password form to log user in. The form invite user who doesnt have a register account yet to create one first. If user forgot his password, a password reset with email verification is available. If any of the informations entered are incorrect, a message will display on screen with details about the problem.

Password reset page, where a user who requested a password reset his redirected with a unique and temporary link from his email.

Register page where the user can create a new account. Consisting of a form collecting information of a unique username, an email adress, a password and a password verification. If any of the details are unexact, a message will display on the screen with details about the problem. The password is hashed to be stored in the database for security.

My account section when a user is logged in, consisting of three pages:
My account page, where the user can edit his profile details, like username, email address and reset his pasword. The user also have the possibility to upload a profile picture.
My reviews page, where the user can see all the reviews he left on the website. 
API page, where the user can see instructions on how to use the api and see an example of the json response.


