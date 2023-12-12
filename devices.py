import psycopg2


def get_devices():

    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432")         
    cur = conn.cursor()
    cur.execute('''select device_type,device_model from devices''')
    devices = cur.fetchall()
    device_list = dict()
    for device in devices:
        if device[0] in device_list.keys():
            device_list[device[0]].append(device[1])
        else:
            device_list[device[0]] = list()
            device_list[device[0]].append(device[1])
    conn.commit()
    cur.close()
    conn.close()
    if len(device_list) == 0:
        return [0, "No Devices!"]
    else:
        return [1, device_list]

def register_device(house_id, device_type, device_model):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
        password="password", host="localhost", port="5432") 
        
    cur = conn.cursor()
    cur.execute('''insert into enrolled_devices (house_id, device_type, device_model, is_active) VALUES(%s, %s, %s, %s) RETURNING ed_id''', (house_id, device_type, device_model, True))
    result = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()        
    if result is None:
        return [0, "Failed to Register Device"]
    else:
        return [1, "Device Registered, ID is"+str(result)]

def deregister_device(ed_id):
    
    # Deregister the selected device from the current user
    conn = psycopg2.connect(database="pds_project", user="postgres", 
        password="password", host="localhost", port="5432") 
        
    cur = conn.cursor()
    cur.execute('''update enrolled_devices set is_active = %s where ed_id = %s''', (False, ed_id))
    conn.commit()
    cur.close()
    conn.close()        
    
    return [1, "Device Unenrolled!"]
    
def get_devices_in_house(address_list):
    dh = dict()
    conn = psycopg2.connect(database="pds_project", user="postgres", 
        password="password", host="localhost", port="5432") 
    cur = conn.cursor()
    for house in address_list:
        house_id = house["HouseID"]
        
        cur.execute('''select ed_id,device_type,device_model from enrolled_devices where house_id = %s''', (house_id,))
        devices = cur.fetchall()
        dl = dict()
        for device in devices:
            dl[device[0]] = str(device[1]) + " - " + str(device[2])
        dh[house_id] = dl
    conn.commit()
    cur.close()
    conn.close() 
    
    return [1, dh]