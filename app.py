import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, json
import requests
from keys import api_key, auth_token, account_sid
from forms import signUpForm, loginForm
from models import User, weekly_meal
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client


# from forms import 
from models import db, connect_db

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///nutrition_plan'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
account_sid = account_sid
auth_token = auth_token
client = Client(account_sid, auth_token)

connect_db(app)

shopping_list = []

def send_message():
    message = client.messages \
                .create(
                     body=shopping_list,
                     from_='+19522601547',      
                     to='+19082408500'
                 )

    print(message.sid)
@app.before_request
def add_user_to_g():
    

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
   

    session[CURR_USER_KEY] = user.id


def do_logout():
   

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def show_home():
    
    return render_template('home.html', user = g.user)

@app.route('/signup', methods = ['GET','POST'])
def show_signup_form():
    form = signUpForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data
        number = form.number.data
        payload = {"name":name, "username":username, "apiKey": api_key}
        headers = {'COntent-Type': 'application/json', 'Accept': 'application/json'}
        spoon_user = requests.post('https://api.spoonacular.com/users/connect', payload, headers = headers ).content.decode('UTF-8')
        print(spoon_user)
        user_data = User.signup(name = name, username = username, password = password, email = email, number = number, spoon_hash = spoon_user.hash, spoon_username = spoon_user.username)
        
        db.session.commit()
    
        do_login(user_data)
        return redirect('/')
    else:
        return render_template('signup.html', form = form, user = g.user)

@app.route('/login', methods = ['GET', 'POST'])
def show_login():
    form = loginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)
        
        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form, user = g.user)

@app.route('/logout')
def logout_user():
    session[CURR_USER_KEY]=None
    return redirect('/')

@app.route('/newplan')
def show_new_plan():


    return render_template('new_plan.html', user = g.user)

@app.route('/users/<int:id>/profile')
def show_profile(id):
    user= User.query.get_or_404(id)
    return render_template('profile.html', user = user)

@app.route('/api/newplan', methods= ['POST'])
def get_plan():
    
    duration = request.json.get('duration')
    calories = request.json.get('calories')
    diet = request.json.get('diet')
    payload = {'timeFrame': duration, 'targetCalories': calories, 'diet':diet, 'apiKey': api_key}
    plan = requests.get(f'https://api.spoonacular.com/mealplanner/generate', params=payload).content.decode('UTF-8')
    weekly_plan = weekly_meal(meal = plan)
    db.session.add(weekly_plan)
    db.session.commit()
    return jsonify({'duration':duration, 'targetCalories': calories, 'diet':diet, 'new_plan':plan})

@app.route('/api/shopping', methods = ['POST'])
def get_list():
    meal = request.form.get('ingredientList')
    servings = request.form.get('servings')
    payload = {'ingredientList': meal, 'servings': servings, 'apiKey': api_key}
    shopping_list.append(requests.get('https://api.spoonacular.com/recipes/parseIngredients', params = payload).content.decode('UTF-8'))
    
    return ({'list': shopping_list})




