from flask import Flask, render_template, request, flash,jsonify,redirect,url_for
from flask_bootstrap import Bootstrap

# Weather Prediction
from weather import Weather

# Image Classifier
import os
from pest import Pest
import numpy as np
from keras.preprocessing import image
from keras import backend as K
import tensorflow as tf
import pickle
from test import Predict

# Market Stats
from market_stat import Market

# Crop Prediction
from crop_predict import Crop_Predict

# Fertilizer Info
import pandas as pd

# Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from test import Predict
from firebase_admin import auth

cred = credentials.Certificate('key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Firebase end Here

# Login
from login import Login

# Admin Login
from admin_login import Login_Admin

# Kisan Center Login
from kisan_center_login import Login_Kisan

# Twilo Message
from twilio.rest import Client

# Weather Forcast 15 Days
import requests
import bs4

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



app = Flask(__name__)
Bootstrap(app)

app.config['SECRET_KEY'] = 'e53b7406a43e2fd9ec89553019420927'


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/weather',methods=['POST','GET'])
def weather():
    weatherModel = Weather()
    if request.method == 'POST':
        city_name = request.form['city']
        if len(city_name) == 0:
            return render_template('weather_pred.html',error=1)
        try:
            daily = request.form['daily']
            print(daily)
            valid = weatherModel.update(city_name)
            if valid == 'noData':
                return render_template('weather_pred.html',error=1)

            weather_data = weatherModel.display()
            # print()
            invalidZip = False
            results = {"zipcode":city_name,"invalidZip":invalidZip, "weather":weather_data}

            return render_template('weather.html',results=results)
        except:
            day_15 = request.form['15days']
            print(day_15)
            city_name = city_name.lower()
            print(city_name)
            res = requests.get('https://www.timeanddate.com/weather/india/'+city_name+'/ext')
            data = bs4.BeautifulSoup(res.text,'lxml')
            # temp = data.find('table',{"id": "wt-ext"})
            temp = data.find_all('tr','c1')

            # type(temp)
            # temp
            lt = []
            for i in range(len(temp)):
                dt = {}
                dt['day'] = temp[i].find('th').text
                x = temp[i].find_all('td')
                dt['temp'] = x[1].text
                dt['weather'] = x[2].text
                dt['temp_max'] = x[3].text
                dt['wind_speed'] = x[4].text
                dt['max_humidity'] = x[6].text
                dt['min_humidity'] = x[7].text
                dt['sun_rise'] = x[10].text
                dt['sun_set'] = x[11].text
                
                lt.append(dt)
            

            return render_template('weather_15_days.html',result=lt,result_len = len(lt))



        
        
        




       
    
    return render_template('weather_pred.html',error=0)



@app.route("/upload", methods=['POST','GET'])
def upload():

    if request.method == 'POST': 
        pest = Pest()
        arrary_image,img = pest.Upload()
        print(arrary_image)

        if arrary_image == 'noData':
            return render_template('pest.html',display=1)
        
        else:
        
            model_file = pickle.load(open("model.pkl","rb"))
            # model._make_predict_function()
            global graph
            p = Predict()
            graph = tf.get_default_graph()
            with graph.as_default():
                predict = model_file.predict(arrary_image)
            
            label_binarizer = pickle.load(open("label_transform.pkl",'rb'))
            result = label_binarizer.inverse_transform(predict)[0]    
            print(result)
            x = p.predicts()
            result = label_binarizer.inverse_transform(x)[0]
            print(result)
            K.clear_session()

            if result == 'Pepper__bell___healthy' or result == 'Tomato_healthy' or result == 'Potato___healthy':

                return render_template('pest_predict.html',result=result,image_name=img)
            
            else :
                
                doc_ref = db.collection(u'pest').document(u''+result)

                try:
                    doc = doc_ref.get()
                    # print(u'Document data: {}'.format(doc.to_dict()))
                    doc = doc.to_dict()
                    print(len(doc))
                except google.cloud.exceptions.NotFound:
                    print(u'No such document!')
            
                # result = model.predict(test_image)
                # result =  model._make_predict_function(test_image)
            return render_template('pest_predict.html',result=result,image_name=img,data=doc)
    
    return render_template('pest.html',display=0)
        
  
@app.route('/market',methods=['POST','GET'])
def market():

    model = Market()
    states,crops = model.State_Crop()
    if request.method == 'POST':
        state = request.form['state']
        crop = request.form['crop']
        lt = model.predict_data(state,crop)

        return render_template('market.html',result=lt,result_len =len(lt),display=True,states=states,crops=crops)

    return render_template('market.html',states=states,crops=crops)   
    

@app.route('/crop',methods=['GET','POST'])
def crop():

    model = Crop_Predict()
    if request.method == 'POST':
        crop_name = model.crop()
        if crop_name == 'noData':
            return render_template('crop_prediction.html',error=1)

        return render_template('crop_prediction.html',crops=crop_name,crop_num = len(crop_name),display=True)

    return render_template('crop_prediction.html',error=0)



@app.route('/fertilizer_info',methods=['POST','GET'])
def fertilizer_info():
    data = pd.read_csv('final_fertilizer.csv')
    crops = data['Crop'].unique()

    if request.method == 'GET':
        crop_se = request.args.get('manager')
        query = data[data['Crop']==crop_se]
        query = query['query'].unique()
        queryArr = []
        if len(query):
            for query_name in query:
                queryObj = {}
                queryObj['name'] = query_name
                print(query_name)
                queryArr.append(queryObj)
            
            return jsonify({'data':render_template('fertilizer.html',crops=crops,crop_len=len(crops)),
                            'query':queryArr})
           
    
    if request.method == 'POST':
        crop_name = request.form['crop']
        query_type = request.form['query']
        query = data[data['Crop']==crop_name]
        answer = query[query['query']== query_type]
        answer = answer['KCCAns'].unique()
        protection = []
        for index in answer:
            protection.append(index)

        return render_template('fertilizer.html',protection=protection,protection_len=len(protection),display=True,crops=crops,crop_len=len(crops))


    return render_template('fertilizer.html',crops=crops,crop_len=len(crops),query_len=0)


@app.route('/shop',methods=['POST','GET'])
def shop():
    if request.method == 'POST':
        city = request.form['city']
        print(city)

        return render_template('fertilizer_shop.html',city=city,data=True)

    return render_template('fertilizer_shop.html')


@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':

        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone']
        kisan_id = request.form['kisan_id']
        adhar_id = request.form['adhar_id']
        state = request.form['state']
        city = request.form['city']
        fullAddress = request.form['fullAddress']
        locality = request.form['locality']
        zipcode = request.form['zipcode']
        password = request.form['password']
        conform_password = request.form['conform_password']
        print(first_name,middle_name,last_name, phone_number,kisan_id,state,city,fullAddress,locality,password,conform_password)


        docs = db.collection(u'kisan_id').get()

       
            # print(u'{} => {}'.format(doc.id,data))

        if password == conform_password:
             for doc in docs:
                data = doc.to_dict()
                if data['id'] == kisan_id:
                    try:
                        email_id = 'kisan'+kisan_id+'@gmail.com'
                        user = auth.create_user(email = email_id,password= password)
                        print('Sucessfully created new user: {0}'.format(user.uid))
                    except :
                        return render_template('register.html',alert=2,first_name=first_name)
                    

                    

                    if user.uid:
                        doc_ref = db.collection(u'users').document(u''+user.uid)
                        doc_ref.set({
                            u'first_name': first_name,
                            u'middle_name': middle_name,
                            u'last_name' :last_name,
                            u'phone_number': phone_number,
                            u'kisan_id': kisan_id,
                            u'adhar_id': adhar_id,
                            u'state': state,
                            u'city': city,
                            u'fullAddress': fullAddress,
                            u'locality': locality,
                            u'zipcode': zipcode
                            })

                        
                        return render_template('register.html',alert=1,first_name=first_name)

    return render_template('register.html')


@app.route('/login',methods=['POST','GET'])
def login():

    if request.method == 'POST':
        login_kisan = Login()
        data,email = login_kisan.kisan_login()
        print(data)
        print(type(data))
        
        if data == 'successful':
            user = auth.get_user_by_email(email)
            print('Successfully fetched user data: {0}'.format(user.uid))

            doc_ref = db.collection(u'users').document(u''+user.uid)
            
            docs = doc_ref.get().to_dict()
            print(docs)
            print(user.uid)
            return render_template('kisan_profile.html',data=docs,display=False,user_id=user.uid)
        else:
            flash(f'Login Failed Please check Your Kisan ID Number and Password','danger')
            return redirect('/login')



    return render_template('login.html')


@app.route('/add_data/<id>',methods=['POST','GET'])
def add_data(id):
    print(id)
    if request.method == 'POST':
        crop_1 = request.form['crop_1']
        crop_2 = request.form['crop_2']
        crop_3 = request.form['crop_3']
        crop_4 = request.form['crop_4']
        print(crop_1,crop_2,crop_3)

        db_ref =  db.collection(u'users').document(u''+id)
        print(db_ref.id)
        
        db_ref.update({
			u'crop_1':crop_1,
			u'crop_2':crop_2,
            u'crop_3':crop_3,
            u'crop_4':crop_4
			})
        docs = db_ref.get().to_dict()
        # flash(f'New Data Added!','success')
        # return redirect('/login')
        user_id = db_ref.id
        print(user_id)
        print("comes here")
        flash(f'Data Updated!','success')
        return render_template('kisan_profile.html',data=docs,dispaly=True,user_id=user_id)

    return render_template('add_data.html',user_id=id)


@app.route('/issue/<user_id>', methods=['GET','POST'])
def issue(user_id):
	if request.method == 'POST':
			fullName = request.form['fullName']
			issue = request.form['issue']

			doc_ref = db.collection(u'issue').document(u''+user_id).collection(u'user_issue').document()
			doc_ref.set({
				u'fullName': fullName,
				u'issue': issue,
				u'seen' : 0
			})

			return render_template('issue.html', user_id = user_id,data=True)
	return render_template('issue.html',user_id = user_id,data=False)



@app.route('/check_issue',methods=['POST','GET'])
def check_issue():
	
	docs = db.collection(u'issue').get()
	# print(docs.to_dict())
	lt = []
	ids = []
	for doc in docs:
		dt = {}
		print(u'{} => {}'.format(doc.id, doc.to_dict()))
		dt['id'] = doc.id
		dt['data'] = doc.to_dict()
		lt.append(dt)
		ids.append(doc.id)
		# print(doc.to_dict())
	# print(len(lt))
	print(lt)
	print(ids)

	data = []
	for i in range(len(ids)):
		id = ids[i]
		docs = db.collection(u'issue').document(u''+id).collection(u'user_issue').get()
		print('comes here')
		for doc in docs:
			dt = {}
			print(u'{} => {}'.format(doc.id, doc.to_dict()))
			dt['user_id'] = id
			dt['id'] = doc.id
			dt['data'] = doc.to_dict()
			data.append(dt)
	
	print(data)

	# print(lt[0]['data']['seen'])
	# print(lt[1]['id'])
	
	# print(doc)
	return render_template('check_issue.html',data=data,data_len=len(data))
	# return 'daata'


	
@app.route('/submit_issue/<user_id>/<data_id>',methods=['POST','GET'])
def submit_issue(user_id,data_id):
    
    docs = db.collection(u'issue').document(u''+user_id).collection(u'user_issue').document(u''+data_id).get().to_dict()
    print(docs)
    print(user_id,data_id)
    if request.method == 'POST':
        db_ref =  db.collection(u'issue').document(u''+user_id).collection(u'user_issue').document(u''+data_id)
        answer = request.form['answer']
        print(answer)
        db_ref.update({u'answer': answer,u'seen':1})

        account_sid = 'AC7b12fbd4c6a2cce3b4fa7d049dc074a7'
        auth_token = '5eb6f4ccbb2dcc0e0f71a6ae165a8cd4'
        
        client = Client(account_sid, auth_token)
        message = client.messages \
        .create(body="Your issue answer send to your profile check your profile for futher update",
            from_='+15104038027',
            to='+919663077540')
        
        print(message.sid)
        
        flash(f'Answer Submited!','success')
        return redirect(url_for('check_issue'))
        
    print(user_id,data_id)
    return render_template('submit_issue.html',data=docs,user_id=user_id,data_id=data_id)
	# return 'done'


@app.route('/issue_update/<user_id>',methods=['POST','GET'])
def issue_update(user_id):
    # docs = db.collection(u'issue').document(u''+id)
    docs =  db.collection(u'issue').document(u''+user_id).collection(u'user_issue').get()
    print(user_id)
    print(docs)
    lt = []
    for doc in docs:
        dt = {}
        print(u'{} => {}'.format(doc.id, doc.to_dict()))
        dt['id'] = doc.id
        dt['data'] = doc.to_dict()
        lt.append(dt)

    print(lt)



    return render_template('issue_update.html',data=lt,data_len = len(lt))
    # return 'data'

@app.route('/admin_login',methods=['POST','GET'])
def admin_login():
    if request.method == 'POST':
        login_kisan = Login_Admin()
        data,email = login_kisan.admin_login()
        print(data)
        print(type(data))
        
        if data == 'successful':
            user = auth.get_user_by_email(email)
            print('Successfully fetched user data: {0}'.format(user.uid))

            doc_ref = db.collection(u'users').document(u''+user.uid)
            
            docs = doc_ref.get().to_dict()
            print(docs)
            print(user.uid)
            return render_template('admin.html')
        else:
            flash(f'Login Failed Please check Your Kisan ID Number and Password','danger')
            return redirect('/admin_login')



    return render_template('admin_login.html')

@app.route('/kisan_center',methods=['POST','GET'])
def kisan_center():
    if request.method == 'POST':
        login_kisan = Login_Kisan()
        data,email = login_kisan.kisan_center_login()
        print(data)
        print(type(data))
        
        if data == 'successful':
            user = auth.get_user_by_email(email)
            print('Successfully fetched user data: {0}'.format(user.uid))

            doc_ref = db.collection(u'users').document(u''+user.uid)
            
            docs = doc_ref.get().to_dict()
            print(docs)
            print(user.uid)
            return render_template('kisan_center.html',data=False,error=False)
        else:
            flash(f'Login Failed Please check Your Kisan ID Number and Password','danger')
            return redirect('/kisan_center')

    return render_template('kisan_login.html')


@app.route('/add_kisan_id',methods=['POST','GET'])
def add_kisan_id():
    if request.method == 'POST':
        kisan_id = request.form['kisan_id']
        # print(kisan_id)
        if len(kisan_id) != 13:
            print(kisan_id)
            return render_template('kisan_center.html',data=False,error=True)

        doc_ref = db.collection(u'kisan_id').document()
        doc_ref.set({
            u'id': kisan_id
            })

        return render_template('kisan_center.html',data=True,error=False)



if __name__ == "__main__":
    
    app.run(debug=True)
    
