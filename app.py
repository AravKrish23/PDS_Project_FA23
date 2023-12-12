from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
import psycopg2 
from datetime import timedelta
from datetime import datetime, date, time
import random 
from register_validate import check_and_create_user
from login_validate import check_login
from address import register_new_house, get_customer_houses, deregister_address
from devices import get_devices, register_device,deregister_device, get_devices_in_house
from graph_queries import get_house_consumption_data, get_device_consumption_data, get_area_statistics, get_house_statistics, calculate_charges_cost


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'
app.permanent_session_lifetime = timedelta(minutes=90)
# csrf = CSRFProtect(app)

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
        response = check_and_create_user(email, phone, name, hashed_password)
        # Add code for stating the user is created
        if response[0] == 1:
            success_msg = response[1]
            flash(success_msg)
            return redirect(url_for('login'))
        else:
            failure_msg = response[1]
            flash(failure_msg)
    return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['user_email']
        password = request.form['user_pwd']
        response = check_login(email)
        if response[0] is None:
            failure_msg = response[3] 
            flash(failure_msg)
        elif bcrypt.check_password_hash(response[0], password):
            session["name"] = response[1]
            session["customer_id"] = response[2]
            return redirect(url_for('home'))
        else:
            failure_msg = "Incorrect User or Password"
            flash(failure_msg)
    
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
            response =  register_new_house(session['customer_id'], zipcode, state, city, street, flat_number, unit_number, is_primary, is_billing)
            if response[0] == 0:
                failure_message = response[1]
                flash(failure_message)
            else:
                success_msg = response[1]
                flash(success_msg)
            return redirect(url_for('home'))
        
    if session["customer_id"] is None:
        return render_template('login.html')
    zipcodes = ["12345", "56789", "10101"]  # Add your prepopulated zipcodes
    return render_template('select_zipcode.html', zipcodes=zipcodes)


@app.route("/deregister_address", methods=['GET', 'POST'])
def deregister_address():

    if session["customer_id"] is None:
        return render_template('login.html')
    customer_id = session["customer_id"];

    if request.method == 'POST':

        selected_address_id = request.form['selected_address']
        response = deregister_address(customer_id, selected_address_id)
        if response[0] == 0:
            failure_msg = response[1]
            flash(failure_msg)
        else:
            success_msg = response[1]
            flash(success_msg)
        return redirect(url_for('home'))


# GET COMMAND
    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
    address_list = response[1] 
    return render_template('deregister_address.html', houses=address_list)


@app.route("/register_device", methods=['GET', 'POST'])
def register_device():
    
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"];

    if request.method == 'POST':
    
        device_type = request.form['device_type']
        device_model = request.form['device_model']
        house_id = request.form['address']
        response = register_device(house_id, device_type, device_model)
        if response[0] == 0:
            failure_msg = response[1]
            flash(failure_msg)
        else:
            success_msg = response[1]
            flash(success_msg)
        return redirect(url_for('home'))

    
    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 

    device_response = get_devices()
    if device_response[0] == 0:
        failure_msg = device_response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    device_list = device_response[1]

    return render_template('register_device.html', address_list=address_list, device_list=device_list)



@app.route("/deregister_device", methods=['GET', 'POST'])
def deregister_device():
    
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"];

    if request.method == 'POST':
        selected_device_id = request.form['devices']
        # Deregister the selected device from the current user
        response = deregister_device(selected_device_id)
        success_msg = response[1]
        flash(success_msg)
        return redirect(url_for('home'))
    

    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 
    
    devices_response = get_devices_in_house(address_list)
    dh = devices_response[1]
    
    return render_template('deregister_device.html', devices_house=dh, addresses = address_list)


@app.route("/calculate_charges", methods=['GET', 'POST'])
def calculate_charges():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"];

    if request.method == 'POST':
        selected_address = request.form['selected_address']
        start_date = str(request.form['start'])
        end_date =str(request.form['end'])
        sd = datetime.strptime(start_date, '%Y-%m-%d')
        ed = datetime.strptime(end_date, '%Y-%m-%d')
        calculate_charges_cost(sd, ed, selected_address)
        
        
    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 

    return render_template('calculate_charges.html', addresses=address_list)

@app.route("/generate_consumption_graph_device")
def generate_graph_device():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"]

    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 
    
    devices_response = get_devices_in_house(address_list)
    dh = devices_response[1]

    return render_template('generate_consumption_graph_device.html', houses=address_list, device_list = dh)

@app.route("/generate_consumption_graph")
def generate_graph():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"]

    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 

    return render_template('generate_consumption_graph.html', houses=address_list )


@app.route("/generate_house_statistics")
def generate_house_statistics():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"]

    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 
    return render_template('generate_house_statistics.html', houses=address_list )

@app.route("/generate_area_statistics")
def generate_area_statistics():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    customer_id = session["customer_id"]
    response = get_customer_houses(customer_id)
    if response[0] == 0:
        failure_msg = response[1]
        flash(failure_msg)
        return redirect(url_for('home'))
    address_list = response[1] 
    return render_template('generate_area_statistics.html', houses=address_list )


@app.route("/get_consumption_data",  methods=['POST'])
def get_consumption_data():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    if request.method == 'POST':
        sd = request.form['startDatetime']
        ed = request.form['endDatetime'] 
        level = request.form['dateLevel']
        selected_address = request.form['selected_address']
        chosenGraph = request.form['chosenGraph']
        consumptionData  = get_house_consumption_data(level, chosenGraph, sd, ed, selected_address)        
        return jsonify(consumptionData)

@app.route("/get_consumption_data_device",  methods=['GET', 'POST'])
def get_consumption_data_device():
    if session["customer_id"] is None:
        return render_template('login.html')    

    if request.method == 'POST':
        sd = request.form['startDatetime']
        ed = request.form['endDatetime'] 
        level = request.form['dateLevel']
        selected_address = request.form['selected_address']
        chosenGraph = request.form['chosenGraph']
        chosen_device = request.form['chosenDevice']
        consumptionData = get_device_consumption_data(level, chosenGraph, sd, ed, selected_address, chosen_device)
        return jsonify(consumptionData)

@app.route("/get_house_statistics",  methods=['GET', 'POST'])
def get_house_statistics():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    if request.method == 'POST':
        sd = request.form['startDatetime']
        ed = request.form['endDatetime'] 
        selected_address = request.form['selected_address']
        house_statistics = get_house_statistics(sd, ed, selected_address)
        return jsonify(house_statistics)    

@app.route("/get_area_statistics",  methods=['GET', 'POST'])
def get_area_statistics():
    if session["customer_id"] is None:
        return render_template('login.html')
    
    

    if request.method == 'POST':
        sd = request.form['startDatetime']
        ed = request.form['endDatetime'] 
        selected_address = request.form['selected_address']
        area_stats = get_area_statistics(sd, ed, selected_address)
        return jsonify(area_stats)    


@app.route("/logout")
def logout():
    if session["customer_id"] is None:
        return render_template('login.html')
    session.pop("name", None)
    session.pop("customer_id", None)
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)