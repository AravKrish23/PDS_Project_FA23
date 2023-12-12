import psycopg2


def check_login(email):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
                        password="password", host="localhost", port="5432")         
    cur = conn.cursor()
    cur.execute('''select customer_id, name, email, password from customers where email = (%s)''', (email,))
    result = cur.fetchall()
    conn.commit()
    cur.close()
    if len(result) == 1:
        processed_msg = "User Exists"
        return [result[0][3], result[0][1], result[0][0], processed_msg]
    else:
        failure_message =  "Incorrect User or Password"
        return[None, None, None, failure_message]
