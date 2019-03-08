import pyrebase
from flask import request


class Login_Admin(object):

    def __init__(self):
        
        self.config = {
            "apiKey": "AIzaSyDDnlX2Rjq0xU0_Ln8bI0YVzpm_ntmDR-s",
            "authDomain": "farmardatabase.firebaseapp.com",
            "databaseURL": "https://farmardatabase.firebaseio.com",
            "projectId": "farmardatabase",
            "storageBucket": "farmardatabase.appspot.com",
            "messagingSenderId": "533114940793"
        }


        self.firebase = pyrebase.initialize_app(self.config)

        self.auth = self.firebase.auth()

    def admin_login(self):

        if request.method == 'POST':
            email = request.form['email']
            password = request.form['pass']
            try:
                user = self.auth.sign_in_with_email_and_password(email, password)
                # user['id']
                return 'successful',email
            except:
                return 'unsuccessful'