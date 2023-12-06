from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import psycopg2 

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'


bcrypt = Bcrypt(app)

@app.route("/")
def home_pre_login():
    return render_template('home_pre_login.html')

@app.route("/home")
def home():
    return render_template('home.html')


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


@app.route("/register_address", methods=['GET', 'POST'])
def register_address():
    if request.method == 'POST':
        unit_number = request.form['unit_number']
        flat_number = request.fomr['flat_number']
        street_name = request.form['street_name']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']

        flash('Address registered successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('register_address.html')


@app.route("/register_device", methods=['GET', 'POST'])
def register_device():
    if request.method == 'POST':
        device_type = request.form['device_type']
        device_model = request.form['device_model']
        address_id = request.form['address']


        flash('Device registered successfully!', 'success')
        return redirect(url_for('home'))

    # addresses = Address.query.filter_by(user=current_user).all()
    return render_template('register_device.html')



if __name__ == "__main__":
    app.run(debug=True)