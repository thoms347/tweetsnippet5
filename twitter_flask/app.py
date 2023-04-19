from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import tweepy

app = Flask(__name__)
app.secret_key = "UIGNHUTH2346"
app.permanent_session_lifetime = timedelta(minutes=5)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tweets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Twitter API Credentials
consumer_key = "fhQr0tMioNoJycI8IjPtb1gYA"
consumer_secret = "UlnrWuvJiJrFyV5XjrVlamOCoIHUXWOmmjOgJgPyFUcMmYfDSi"
access_token = "1615863193519128578-I2JIs222covmJn52BbOpdKvlQWqeOZ"
access_token_secret = "XC1LETHdK9dERRQIa3uJJEUGnphPf2fTQsUiZnay6ZSOg"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

#Creating an API Object
api = tweepy.API(auth)

db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login" , methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user
        return redirect(url_for("user"))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("welcome.html")


@app.route("/user" , methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}</h1>"

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            return render_template()
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect (url_for("login"))

@app.route('/tweet/<string:tweet_id>', methods=['GET'])
def get_tweet(tweet_id):
    try:
        tweet = api.get_status(tweet_id)
        return jsonify(tweet._json)
    except tweepy.TweepError as e:
        return jsonify(error=str(e))

# Define the User model for storing user data
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Define the Tweet model for storing tweet data
class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(280), nullable=False)

    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text 


# Endpoint for creating a new user account
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    username = user_data.get('username')
    password = user_data.get('password')

    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'error': 'username already taken'}), 400

    user = User(username, password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'user created successfully'}), 201

    db.create_all()
    app.run(debug=True)
















# Endpoint for retrieving tweets for a particular user
@app.route('/tweets/<username>', methods=['GET'])
def get_tweets(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'error': 'user not found'}), 404

    tweets = Tweet.query.filter_by(user_id=user.id).all()
    return jsonify([{'text': tweet.text} for tweet in tweets]), 200

# Endpoint for storing a tweet for a particular user
@app.route('/tweets/<username>', methods=['POST'])
def store_tweet(username, tweet, password):
    # Check if the user exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 400

    # Check if the provided password is correct
    if not user.check_password(password):
        return jsonify({"error": "Incorrect password"}), 400

    # Create a new tweet object and add it to the user's tweets
    new_tweet = Tweet(content=tweet)
    user.tweets.append(new_tweet)

    # Commit the changes to the database
    db.session.add(new_tweet)
    db.session.commit()

    # Return success
    return jsonify({"message": "Tweet stored successfully"}), 201