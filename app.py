import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify, json
import requests
import datetime
from datetime import date, timedelta
from keys import api_key, auth_token, account_sid
from forms import signUpForm, loginForm
from models import User, weekly_meal
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client


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
request_list1 = []



def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: 
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

d1 = date.today()
d = datetime.datetime.now()
next_monday = next_weekday(d, 0) 
monday_stamp = datetime.datetime.timestamp(next_monday)
next_tuesday = next_monday + timedelta(1)
tuesday_stamp = datetime.datetime.timestamp(next_tuesday)
next_wednesday = next_tuesday + timedelta(1)
wednesday_stamp = datetime.datetime.timestamp(next_wednesday)
next_thursday = next_wednesday + timedelta(1) 
thursday_stamp = datetime.datetime.timestamp(next_thursday)
next_friday = next_thursday + timedelta(1) 
friday_stamp = datetime.datetime.timestamp(next_friday)
next_saturday = next_friday + timedelta(1) 
saturday_stamp = datetime.datetime.timestamp(next_saturday)
next_sunday = next_saturday + timedelta(1)
sunday_stamp = datetime.datetime.timestamp(next_sunday)
monday = next_weekday(d1, 0)
tuesday = monday + timedelta(1)
wednesday = tuesday + timedelta(1)
thursday = wednesday + timedelta(1)
friday = thursday + timedelta(1)
saturday = friday + timedelta(1)
sunday = saturday + timedelta(1)
print(monday)



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

        spoon_user = requests.post(f'https://api.spoonacular.com/users/connect?apiKey={api_key}', json = payload).content
        spoon_user_json = json.loads(spoon_user)
        print('**********')
        print(spoon_user)
        print(spoon_user_json['username'], spoon_user_json['hash'])
        print('***********')
        user_data = User.signup(name = name, username = username, password = password, email = email, number = number, spoon_username = spoon_user_json['username'], spoon_hash = spoon_user_json['hash'])
        
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
    return render_template('profile.html',  user = user)

@app.route('/api/newplan', methods= ['POST'])
def get_plan():
    
    duration = request.json.get('duration')
    calories = request.json.get('calories')
    diet = request.json.get('diet')
    payload = {'timeFrame': duration, 'targetCalories': calories, 'diet':diet, 'apiKey': api_key}
    plan = requests.get(f'https://api.spoonacular.com/mealplanner/generate', params=payload).content.decode('UTF-8')
  
    json_plan = json.loads(plan)
    
    for day in json_plan['week'].items():
        

        for meal in day[1].items():
            for meals in meal[1]:
                print(meals)
                for id in meals:  
                    print(id)
                    if day[0] == 'monday':
                        request_list1.append({'date':monday_stamp, 'slot': 1, 'position': 0,'type': 'RECIPE', 'value': {'id': id , 'title':title, 'servings':servings}})
                    if day[0] == 'tuesday':
                        request_list1.append({'date':tuesday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
                    if day[0] == 'wednesday':
                        request_list1.append({'date':wednesday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
                    if day[0] == 'thursday':
                        request_list1.append({'date':thursday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
                    if day[0] == 'friday':
                        request_list1.append({'date':friday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
                    if day[0] == 'saturday':
                        request_list1.append({'date':saturday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
                    if day[0] == 'sunday':
                        request_list1.append({'date':sunday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id':('id'), 'title':('title'), 'servings':('servings')}})
  
    request_list = [i for i in request_list1 if not (i['value'] == 'carbohydrates' or i['value'] =='fat' or i['value'] =='protein' or i['value'] =='calories')]
    print(request_list1)
    add_plan = requests.post(f'https://api.spoonacular.com/mealplanner/{g.user.spoon_username}/items?apiKey={api_key}&hash={g.user.spoon_hash}', json = request_list).content.decode('UTF-8')
    
    get_list()
    return jsonify({'duration':duration, 'targetCalories': calories, 'diet':diet, 'new_plan':plan})

@app.route('/api/shopping', methods = ['POST'])
def get_list():

    resp = shopping_list.append(requests.post(f'https://api.spoonacular.com/mealplanner/{g.user.spoon_username}/shopping-list/{monday}/{sunday}?apiKey={api_key}&hash={g.user.spoon_hash}').content.decode('UTF-8'))
    print(resp)
    return ({'list': shopping_list})




