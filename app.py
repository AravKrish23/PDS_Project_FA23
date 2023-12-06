from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import psycopg2 

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'


bcrypt = Bcrypt(app)



@app.route("/")
def home():
    return "Welcome to the registration and login system using Flask and PostgreSQL!"


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = psycopg2.connect(database="pds_project", user="postgres", 
                        password="password", host="localhost", port="5432") 
        
        # Check if the email or phone number is already registered
        cur = conn.cursor()
        cur.execute('''select * from CUSTOMERS where email = %s or phone = %s''',(email, phone))
        rec = cur.fetchall()
        if len(rec) > 0:
            cur.close()
            return("The Following Credentials Have already been used to register some one else")
        cur.close()

        # Create User If the details are correct.
        cur = conn.cursor()
        cur.execute('''INSERT INTO CUSTOMERS (name, email, phone, password) values (%s, %s, %s, %s)''',(name, email, phone, hashed_password))
        conn.commit()
        cur.close()
        conn.close()

        # Add code for stating the user is created

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = psycopg2.connect(database="pds_project", user="postgres", 
                        password="password", host="localhost", port="5432") 
        
        cur = conn.cursor()
        cur.execute('''select email, password from customers where email = (%s)''', (email,))
        result = cur.fetchall()
        conn.commit()
        cur.close()
        if len(result) == 1:
            if bcrypt.check_password_hash(result[0][1], password):
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Login unsuccessful. Please check your email and password.', 'danger')
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)