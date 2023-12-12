import psycopg2


def deregister_address(customer_id, house_id):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
    
    cur = conn.cursor()
    print("The Selected Address: ",  house_id)
    cur.execute('''update house_info set is_current= %s where customer_id = %s and house_id = %s''', (False, customer_id, house_id))
    conn.commit()
    cur.close()
    conn.close()

def get_customer_houses(customer_id):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
    cur = conn.cursor()
    address_list = list()
    cur.execute('''select house_id, address_id from house_info where customer_id = %s and is_current= %s''', (customer_id, True))
    result = cur.fetchall()
    
    if len(result) ==0:
        failure_msg = [0, "No Address Registered for this user!"]
        return failure_msg
    
    for res in result: 
        cur.execute('''select unit_number, flat_number, street_name, city, state from address where address_id = %s''', (res[1],))
        addr = list(cur.fetchone())
        addr = ' '.join(addr)
        address_list.append({"HouseID": res[0], "address":{addr}})
    
    success_msg = [1, address_list]
    return success_msg

def register_new_house(customer_id, zipcode, state, city, street, flat_number, unit_number, is_primary, is_billing):
    conn = psycopg2.connect(database="pds_project", user="postgres",  password="password", host="localhost", port="5432") 
            
    cur = conn.cursor()
    cur.execute('''select address_id, unit_number, flat_number,
    street_name, city, state from address where zipcode_id = %s
    and state= %s and city = %s and street_name= %s and flat_number=%s and unit_number=%s''', (zipcode, state, city, street, flat_number, unit_number))
    result = cur.fetchone()
    conn.commit()
    cur.close()
    if result is None:
        failure_message = [0, "Address is not servicable!"]
        return failure_message
    if result is not None:

        cur = conn.cursor()
                
        cur.execute('''select customer_id  from house_info  where address_id = %s order by owner_since desc''', (result[0], ))
        current_owner = cur.fetchone()
        if current_owner is not None:
            if current_owner[0] == customer_id:  
                failure_message = [0, "You are already the current owner!"]
                return failure_message
    

        if(is_primary):
            
            cur.execute('''select house_id  from house_info  where customer_id = %s and is_primary = true''', (customer_id, ))
            current_primary = cur.fetchone()
            if current_primary is not None:
                cur.execute('''update house_info set is_primary = false where customer_id = %s''', (customer_id, ))
            

        if(is_billing):

            cur.execute('''select house_id  from house_info  where customer_id = %s and is_billing = true''', (customer_id, ))
            current_primary = cur.fetchone()
            if current_primary is not None:
                cur.execute('''update house_info set is_billing = false where customer_id = %s''', (customer_id, ))

                    
        cur = conn.cursor()
        cur.execute('''insert into house_info (address_id, customer_id, owner_since, is_primary, is_billing, is_current) VALUES (%s, %s, %s, %s, %s, %s) RETURNING house_id''', (result[0], customer_id, '20201223', is_primary, is_billing, True ))
        new_reg_id = cur.fetchall()
        nri = str(new_reg_id[0][0]) 
        success_statement = [1, "Successfully Registered, Your House Id is:" + nri]

        conn.commit()
        cur.close()        
        conn.close()

        return (success_statement)