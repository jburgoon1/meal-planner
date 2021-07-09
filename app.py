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



#add the current user to the global variable
@app.before_request
def add_user_to_g():
    

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

#save the current user id in the session
def do_login(user):
   

    session[CURR_USER_KEY] = user.id

#remove the current user from the session
def do_logout():
   

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/')
def show_home():
    
    return render_template('home.html', user = g.user)
#create a user instance and send the information to spoonacular to connect the user, then save the api hash and username to the database
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
#get the information sent from app.js and send it to the api to get a new plan.
@app.route('/api/newplan', methods= ['POST'])
def get_plan():
    
    duration = request.json.get('duration')
    calories = request.json.get('calories')
    diet = request.json.get('diet')
    payload = {'timeFrame': duration, 'targetCalories': calories, 'diet':diet, 'apiKey': api_key}
    plan = requests.get(f'https://api.spoonacular.com/mealplanner/generate', params=payload).content.decode('UTF-8')
  
    json_plan = json.loads(plan)
   
    for day in json_plan['week'].items():
        for meal in day[1].get('meals'):
            if day[0] == 'monday':
                request_list1.append({'date':monday_stamp, 'slot': 1, 'position': 0,'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'tuesday':
                request_list1.append({'date':tuesday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'wednesday':
                request_list1.append({'date':wednesday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'thursday':
                request_list1.append({'date':thursday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'friday':
                request_list1.append({'date':friday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'saturday':
                request_list1.append({'date':saturday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
            if day[0] == 'sunday':
                request_list1.append({'date':sunday_stamp, 'slot': 1, 'position': 0, 'type': 'RECIPE', 'value': {'id': meal['id'] , 'title':meal['title'], 'servings':meal['servings']}})
  
    request_list = [i for i in request_list1 if not (i['value'] == 'carbohydrates' or i['value'] =='fat' or i['value'] =='protein' or i['value'] =='calories')]
    #add the new plan to the users meal plan on the api side
    add_plan = requests.post(f'https://api.spoonacular.com/mealplanner/{g.user.spoon_username}/items?apiKey={api_key}&hash={g.user.spoon_hash}', json = request_list).content.decode('UTF-8')
    
    get_list()
    return jsonify({'duration':duration, 'targetCalories': calories, 'diet':diet, 'new_plan':plan})
#get the ingredients to send to the user
@app.route('/api/shopping', methods = ['POST'])
def get_list():

    resp = requests.post(f'https://api.spoonacular.com/mealplanner/{g.user.spoon_username}/shopping-list/{monday}/{sunday}?apiKey={api_key}&hash={g.user.spoon_hash}').content.decode('UTF-8')
    json_resp = json.loads(resp)
    for ing in json_resp['aisles']:
        for items in ing['items']:
            shopping_list.append(items.get('name'))
            for measure in items['measures']['original'].items():
                shopping_list.append(str(measure[1]))

   
   
    new_listR1 = shopping_list[:len(shopping_list)//2]
    
    new_listR2 = new_listR1[:len(new_listR1)//2]

    new_listRF3 = new_listR2[:len(new_listR2)//2]

    new_listR3 = new_listRF3[:len(new_listRF3)//2]
    new_list1 = ' '.join(new_listR3[:len(new_listR3)//2])
    new_list2 = ' '.join(new_listR3[len(new_listR3)//2:])

    new_listR4 = new_listR3[len(new_listR3)//2:]
    new_list2 = ' '.join(new_listR4[:len(new_listR4)//2])
    new_list2 = ' '.join(new_listR4[len(new_listR4)//2:])

    new_listR5 = new_listR2[len(new_listR2)//2:]

    new_listR6 = new_listR5[:len(new_listR5)//2]
    new_list3 = ' '.join(new_listR6[:len(new_listR6)//2])
    new_list4 = ' '.join(new_listR6[len(new_listR6)//2:])

    new_listR7 = new_listR5[len(new_listR5)//2:]
    new_list5 = ' '.join(new_listR7[:len(new_listR7)//2])
    new_list6 = ' '.join(new_listR7[len(new_listR7)//2:])

    new_listR8 = new_listR1[len(new_listR1)//2:]

    new_listR9 = new_listR3[:len(new_listR8)//2]

    new_listR10 = new_listR9[:len(new_listR9)//2]
    new_list7 = ' '.join(new_listR10[:len(new_listR10)//2])
    new_list8 = ' '.join(new_listR10[len(new_listR10)//2:])

    new_listR11 = new_listR9[len(new_listR9)//2:]
    new_list9 = ' '.join(new_listR11[:len(new_listR11)//2])
    new_list10 = ' '.join(new_listR11[len(new_listR11)//2:])

    new_listR12 = new_listR8[len(new_listR8)//2:]

    new_listR13 = new_listR12[:len(new_listR12)//2:]
    new_list11 = ' '.join(new_listR13[:len(new_listR13)//2])
    new_list12 = ' '.join(new_listR13[len(new_listR13)//2:])

    new_listR14 = new_listR12[len(new_listR12)//2:]
    new_list13 = ' '.join(new_listR14[:len(new_listR14)//2])
    new_list14 = ' '.join(new_listR14[len(new_listR14)//2:])
    

    new_listR15 = shopping_list[len(shopping_list)//2:]

    new_listR16 = new_listR15[:len(new_listR15)//2]

    new_listR17 = new_listR16[:len(new_listR16)//2]

    new_listR18 = new_listR17[:len(new_listR17)//2]
    new_list15 = ' '.join(new_listR18[:len(new_listR18)//2])
    new_list16 = ' '.join(new_listR18[len(new_listR18)//2:])

    new_listR19 = new_listR17[len(new_listR17)//2:]
    new_list17 = ' '.join(new_listR19[:len(new_listR19)//2])
    new_list18 = ' '.join(new_listR19[len(new_listR19)//2:])

    new_listR20 = new_listR16[len(new_listR16)//2:]

    new_listR21 = new_listR20[:len(new_listR20)//2]
    new_list19  = ' '.join(new_listR21[:len(new_listR21)//2])
    new_list20 = ' '.join(new_listR21[len(new_listR21)//2:])

    new_listR22 = new_listR20[len(new_listR20)//2:]
    new_list21 = ' '.join(new_listR22[:len(new_listR22)//2])
    new_list22 = ' '.join(new_listR22[len(new_listR22)//2:])

    new_listR23 = new_listR15[len(new_listR15)//2:]

    new_listR24 = new_listR23[:len(new_listR23)//2]

    new_listR25 = new_listR24[:len(new_listR24)//2]
    new_list23 = ' '.join(new_listR25[:len(new_listR25)//2])
    new_list24 = ' '.join(new_listR25[len(new_listR25)//2:])

    new_listR26 = new_listR24[len(new_listR24)//2:]
    new_list25 = ' '.join(new_listR26[:len(new_listR26)//2])
    new_list26 = ' '.join(new_listR26[len(new_listR26)//2:])

    new_listR27 = new_listR23[len(new_listR23)//2:]

    new_listR28 = new_listR27[:len(new_listR27)//2]
    new_list27 = ' '.join(new_listR28[:len(new_listR28)//2])
    new_list28 = ' '.join(new_listR28[len(new_listR28)//2:])
    
    new_listR29 = new_listR27[len(new_listR27)//2:]
    new_list29 = ' '.join(new_listR29[:len(new_listR29)//2])
    new_list30 = ' '.join(new_listR29[len(new_listR29)//2:])
    

    print(new_list1)
    print(len(new_list1))
    print(new_list2)
    print(len(new_list2))
    print(new_list3)
    print(len(new_list3))
    print(new_list4)
    print(len(new_list4))
    print(new_list5)
    print(len(new_list5))
    print(new_list6)
    print(len(new_list6))
    print(new_list7)
    print(len(new_list7))
    print(new_list8)
    print(len(new_list8))
    print(new_list9)
    print(len(new_list9))
    print(new_list10)
    print(len(new_list10))
    print(new_list11)
    print(len(new_list11))
    print(new_list12)
    print(len(new_list12))
    print(new_list13)
    print(len(new_list13))
    print(new_list14)
    print(len(new_list14))
    print(new_list15)
    print(len(new_list15))
    print(new_list16)
    print(len(new_list16))
    send_message(new_list1, new_list2, new_list3, new_list4, new_list5, new_list6, new_list7, new_list8, new_list9, new_list10,new_list11, new_list12, new_list13, new_list14, new_list15,new_list16, new_list17, new_list18, new_list19, new_list20,new_list21, new_list22, new_list23, new_list24, new_list25,new_list26, new_list27, new_list28, new_list29, new_list30)
    
    return ({'list': shopping_list})

# send a meesage through twilio to the cuurent users number
def send_message(new_list1, new_list2, new_list3, new_list4, new_list5, new_list6, new_list7, new_list8, new_list9, new_list10,new_list11, new_list12, new_list13, new_list14, new_list15,new_list16, new_list17, new_list18, new_list19, new_list20,new_list21, new_list22, new_list23, new_list24, new_list25,new_list26, new_list27, new_list28, new_list29, new_list30):
    message = client.messages \
                .create(
                     body=new_list1,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list2,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list3,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list4,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list5,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list6,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list7,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list8,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list9,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list10,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list11,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list12,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list13,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list14,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list15,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list16,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list17,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list18,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list19,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list20,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list21,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list22,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list23,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list24,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list25,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list26,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list27,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list28,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list29,
                     from_='+19522601547',      
                     to=g.user.number
                 )
    message = client.messages \
                .create(
                     body=new_list30,
                     from_='+19522601547',      
                     to=g.user.number
                 )

    print(message.sid)




