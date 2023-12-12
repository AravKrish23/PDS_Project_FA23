import psycopg2 


def check_and_create_user(email, phone, name, hashed_password):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
                        password="password", host="localhost", port="5432") 
        
        # Check if the email or phone number is already registered
    cur = conn.cursor()
    cur.execute('''select * from CUSTOMERS where email = %s or phone = %s''',(email, phone))
    rec = cur.fetchall()
    if len(rec) > 0:
        cur.close()
        display_msg = "The User with these credentials already exists!"
        cur.close()
        return [0, display_msg]

    # Create User If the details are correct.
    cur = conn.cursor()
    cur.execute('''INSERT INTO CUSTOMERS (name, email, phone, password) values (%s, %s, %s, %s)''',(name, email, phone, hashed_password))
    conn.commit()
    cur.close()
    conn.close()
    display_msg = "The User Has been Created"
    return [1, display_msg]
