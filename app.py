from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import psycopg2 
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.permanent_session_lifetime = timedelta(minutes=30)

bcrypt = Bcrypt(app)

@app.route("/")
def home_pre_login():
    return render_template('home_pre_login.html')

@app.route("/home")
def home():
    if session["customer_id"] is not None:
        return render_template('home.html', customer_id= session["name"])
    else:
        return render_template('home_pre_login.html')

        


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
        email = request.form['user_email']
        password = request.form['user_pwd']

        conn = psycopg2.connect(database="pds_project", user="postgres", 
                        password="password", host="localhost", port="5432") 
        
        cur = conn.cursor()
        cur.execute('''select customer_id, name, email, password from customers where email = (%s)''', (email,))
        result = cur.fetchall()
        conn.commit()
        cur.close()
        if len(result) == 1:

            if bcrypt.check_password_hash(result[0][3], password):
                print("Here!")
                session["name"] = result[0][1]
                session["customer_id"] = result[0][0]
                print(session["name"])
                print(session["customer_id"])
                return redirect(url_for('home'))

            else:
                flash('Login unsuccessful. Please check your email and password.', 'danger')

        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template('login.html')


@app.route("/register_address", methods=['GET', 'POST'])
def register_address():
    if request.method == 'POST':
        if 'zipcode' in request.form:
            # Step 1: User selected a zipcode
            zipcode = request.form['zipcode']
            return render_template('register_address.html', step='select_address', zipcode=zipcode)

        elif 'zipcode_fixed' in request.form:

            zipcode = request.form['zipcode_fixed']
            state = request.form['state']
            city = request.form['city']
            street = request.form['street']
            flat_number = request.form['flat_number']
            unit_number = request.form['unit_number']
            is_primary = True
            is_billing = True

            conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
            
            cur = conn.cursor()
            cur.execute('''select address_id, unit_number, flat_number,
                         street_name, city, state from address where zipcode_id = %s
                          and state= %s and city = %s and street_name= %s and flat_number=%s and unit_number=%s''', (zipcode, state, city, street, flat_number, unit_number))
            result = cur.fetchone()

            conn.commit()
            cur.close()
            if len(result) > 0:

                customer_id = 1;

                if(is_primary):
                    cur = conn.cursor()
                    cur.execute('''select house_id  from house_info  where customer_id = %s and is_primary = true''', (customer_id, ))
                    current_primary = cur.fetchone()[0]
                    if current_primary is not None:
                        cur.execute('''update house_info set is_primary = false where customer_id = %s''', (customer_id, ))
                    cur.close()

                if(is_billing):
                    cur = conn.cursor()
                    cur.execute('''select house_id  from house_info  where customer_id = %s and is_billing = true''', (customer_id, ))
                    current_primary = cur.fetchone()[0]
                    if current_primary is not None:
                        cur.execute('''update house_info set is_billing = false where customer_id = %s''', (customer_id, ))
                    cur.close()


                

                #  Check if the use is already the current owner
                cur = conn.cursor()
                
                cur.execute('''select customer_id  from house_info  where address_id = %s order by owner_since desc''', (result[0], ))
                current_owner = cur.fetchone()
                
                if current_owner[0] == customer_id:  
                    warning = "You are already the current owner!"
                    return(warning)
                cur.close()

                
                cur = conn.cursor()
                cur.execute('''insert into house_info (address_id, customer_id, owner_since, is_primary, is_billing) VALUES (%s, %s, %s, %s, %s) RETURNING house_id''', (result[0], customer_id, '20201223', is_primary, is_billing ))
                new_reg_id = cur.fetchall()
                nri = str(new_reg_id[0][0])
                conn.commit()
                cur.close()
                success_statement = "Successfully Registered, Your Customer Id is:" + nri
                return (success_statement)
                
            conn.close()
            return redirect(url_for('home'))

    zipcodes = ["12345", "56789", "10101"]  # Add your prepopulated zipcodes
    return render_template('select_zipcode.html', zipcodes=zipcodes)


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


@app.route("/logout")
def logout():
    session.pop("name", None)
    session.pop("custoemr_id", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)