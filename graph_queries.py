import psycopg2


def calculate_charges_cost(sd, ed, selected_address):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
            
    cur = conn.cursor()
    address_list = list()
    cur.execute('''with primary_data as (
    select e.ed_id, e.value_stored, e.timestamp, a.zipcode_id, h.customer_id, h.house_id
    from event_info e
    join enrolled_devices ed on ed.ed_id = e.ed_id
    join house_info h on ed.house_id = h.house_id
    join address a on a.address_id = h.address_id
    join event_type et on et.event_type_id = e.event_type_id
    where et.event_type = %s)

    select  sum(value_stored * price_per_unit) from primary_data pd
    join price_map pm
    on pd.zipcode_id = pm.zipcode
    and pm.start_time = (select max(start_time) from price_map where
    zipcode = pd.zipcode_id and start_time <= pd.timestamp)
    where pd.timestamp between %s and %s
    and pd.house_id = %s''', ('Energy Use',  sd, ed, selected_address))
    result = cur.fetchall()
    
    if result[0][0] is not None:
        charges = float(result[0][0])
    else:
        charges = 0
    conn.commit()
    cur.close()
    conn.close()
    return "The Charges for this user is $" + str(charges) + " during the period between " + str(sd) + " and " + str(ed)


def get_house_statistics_data(sd, ed, selected_address):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
            
    cur = conn.cursor()            
    cur.execute('''with primary_data as (
    select e.ed_id, e.value_stored, e.timestamp, a.zipcode_id, h.customer_id, h.house_id
    from event_info e
    join enrolled_devices ed on ed.ed_id = e.ed_id
    join house_info h on ed.house_id = h.house_id
    join address a on a.address_id = h.address_id
    join event_type et on et.event_type_id = e.event_type_id
    where et.event_type = %s),
                

    energy_data as (
    select pd.ed_id, sum(value_stored) as energy_usage from primary_data pd
    join price_map pm
    on pd.zipcode_id = pm.zipcode
    and pm.start_time = (select max(start_time) from price_map where
    zipcode = pd.zipcode_id and start_time <= pd.timestamp)
    where pd.timestamp between %s and %s
    and pd.house_id = %s
    group by pd.ed_id)
                
    select ed2.ed_id, device_type, device_model, 
    energy_usage from energy_data ed join enrolled_devices ed2 
    on ed.ed_id = ed2.ed_id''', ('Energy Use',  sd, ed, selected_address))
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    
    values = list()
    labels  = list()
    device_type_data = dict()
    for data in result:
        values.append(data[3])
        labels.append(str(data[0])+"-"+str(data[1])+"_"+str(data[2]))
        if data[1] in device_type_data.keys():
            device_type_data[data[1]] += float(data[3])
        else:
            device_type_data[data[1]] = float(data[3])
        
    device_type_values = list()
    for key in device_type_data:
        device_type_values.append(device_type_data[key])
        
    consumption_data = {'values': values, 'labels':labels, 'device_types':list(device_type_data.keys()), 'device_type_values':device_type_values}
    return consumption_data

def get_area_statistics_data(sd, ed, selected_address):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
        
    cur = conn.cursor()            
    cur.execute(''' select zipcode_id from address a join house_info h on h.address_id = a.address_id and h.house_id=%s''', (selected_address, ))
    result_zipcode = cur.fetchone()[0]
    print(result_zipcode)
    cur.execute(
    '''with primary_data as (
    select e.ed_id, e.value_stored, e.timestamp, a.zipcode_id, h.customer_id, h.address_id, a.sqft, h.house_id from event_info e 
    join enrolled_devices ed on ed.ed_id = e.ed_id
    join house_info h on ed.house_id = h.house_id
    join address a on a.address_id = h.address_id
    join event_type et on et.event_type_id = e.event_type_id
    where et.event_type = 'Energy Use' 
    and a.zipcode_id = %s),

    sec_data as (
    select pd.house_id, sum(value_stored) as sum1 from primary_data pd
    join price_map pm 
    on pd.zipcode_id = pm.zipcode
    and pm.start_time = (select max(start_time) from price_map where zipcode = pd.zipcode_id and start_time <= pd.timestamp)
    where pd.timestamp >= %s and pd.timestamp < %s 
    group by pd.house_id),

    ter_data as (
    select a.address_id, sd.house_id, sd.sum1, a.sqft, a.sqft * 0.90 as low, a.sqft * 1.10 as high 
        from sec_data sd join house_info h on h.house_id  = sd.house_id
        join address a on h.address_id = a.address_id
    ),

    get_range as (
    select t.house_id, t.address_id, t.sqft, t.sum1, t2.sum1 as range_sum from ter_data t join
    ter_data t2 on 
    t2.sqft >= t.low and t2.sqft <= t.high)

    select house_id, round(avg(sum1),2), round((avg(sum1) - avg(range_sum))*100/avg(range_sum), 2) as 
    PercentageChange, round(avg(sqft),0)  from get_range group by house_id
    ''', (result_zipcode, sd, ed))
    result = cur.fetchall()

    other_bill = 0
    bill = 0
    avg_above = 0
    for data in result:
        
        if int(data[0]) == int(selected_address):
            bill = data[1]
            avg_above = data[2]
        else:
            other_bill += data[1]        
    percentage_of_total = list()
    # percentage_of_total.append(bill *100/(bill+other_bill))
    # percentage_of_total.append(other_bill * 100/(bill+other_bill))
    percentage_of_total = [50,50]
    labels = ["Your House", "Rest of the service Locations in this zipcode"]
    consumption_data = {'own_consumption': bill, 'other_consumption':other_bill, 'percentage_of_total':percentage_of_total, 'labels':labels, 'avg_above':avg_above}
    conn.commit()
    cur.close()
    conn.close()
    return consumption_data


def get_device_consumption_data(level, chosenGraph, sd, ed, selected_address, chosen_device):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
            
    if(chosenGraph == "EC"):    
        cur = conn.cursor()
        cur.execute('''with primary_data as (
        select e.ed_id, e.value_stored, DATE_TRUNC(%s, e.timestamp ) as stamp, a.zipcode_id, h.customer_id, h.house_id
        from event_info e
        join enrolled_devices ed on ed.ed_id = e.ed_id
        join house_info h on ed.house_id = h.house_id
        join address a on a.address_id = h.address_id
        join event_type et on et.event_type_id = e.event_type_id
        where et.event_type = %s)

        select  cast(stamp as date), sum(value_stored) from primary_data pd
        join price_map pm
        on pd.zipcode_id = pm.zipcode
        where pd.stamp between %s and %s
        and pd.ed_id = %s 
        and pd.house_id = %s
        group by stamp''', (level, 'Energy Use',  sd, ed, chosen_device, selected_address))
        result = cur.fetchall()
        
        dates = list()
        values = list()
        for data in result:
            dates.append(str(data[0]))
            values.append(data[1])

        consumption_data = {'dates': dates, 'values':values}
    
    else:
        cur = conn.cursor()            
        cur.execute('''with primary_data as (
        select e.ed_id, e.value_stored, e.timestamp, date_trunc(%s, e.timestamp) as datestamp, a.zipcode_id, h.customer_id, h.house_id
        from event_info e
        join enrolled_devices ed on ed.ed_id = e.ed_id
        join house_info h on ed.house_id = h.house_id
        join address a on a.address_id = h.address_id
        join event_type et on et.event_type_id = e.event_type_id
        where et.event_type = %s)

        select cast(datestamp as date), sum(value_stored * price_per_unit) from primary_data pd
        join price_map pm
        on pd.zipcode_id = pm.zipcode
        and pm.start_time = (select max(start_time) from price_map where
        zipcode = pd.zipcode_id and start_time <= pd.timestamp)
        where pd.timestamp between %s and %s
        and pd.ed_id  = %s
        and pd.house_id = %s
        group by datestamp''', (level,'Energy Use',  sd, ed, chosen_device, selected_address))
        result = cur.fetchall()
        dates = list()
        values = list()
        for data in result:
            dates.append(str(data[0]))
            values.append(data[1])
    
        consumption_data = {'dates': dates, 'values':values}
    conn.commit()
    cur.close()
    conn.close()
    return consumption_data

def get_house_consumption_data(level, chosenGraph, sd, ed, selected_address):
    conn = psycopg2.connect(database="pds_project", user="postgres", 
            password="password", host="localhost", port="5432") 
            
    if(chosenGraph == "EC"):    
        cur = conn.cursor()
        cur.execute('''with primary_data as (
        select e.ed_id, e.value_stored, DATE_TRUNC(%s, e.timestamp ) as stamp, a.zipcode_id, h.customer_id, h.house_id
        from event_info e
        join enrolled_devices ed on ed.ed_id = e.ed_id
        join house_info h on ed.house_id = h.house_id
        join address a on a.address_id = h.address_id
        join event_type et on et.event_type_id = e.event_type_id
        where et.event_type = %s)

        select  cast(stamp as date), sum(value_stored) from primary_data pd
        join price_map pm
        on pd.zipcode_id = pm.zipcode
        where pd.stamp between %s and %s
        and pd.house_id = %s
        group by stamp''', (level, 'Energy Use',  sd, ed, selected_address))
        result = cur.fetchall()
        
        dates = list()
        values = list()
        for data in result:
            dates.append(str(data[0]))
            values.append(data[1])

        consumption_data = {'dates': dates, 'values':values}
    
    else:
        cur = conn.cursor()            
        cur.execute('''with primary_data as (
        select e.ed_id, e.value_stored, e.timestamp, date_trunc(%s , e.timestamp) as datestamp, a.zipcode_id, h.customer_id, h.house_id
        from event_info e
        join enrolled_devices ed on ed.ed_id = e.ed_id
        join house_info h on ed.house_id = h.house_id
        join address a on a.address_id = h.address_id
        join event_type et on et.event_type_id = e.event_type_id
        where et.event_type = %s)

        select cast(datestamp as date), sum(value_stored * price_per_unit) from primary_data pd
        join price_map pm
        on pd.zipcode_id = pm.zipcode
        and pm.start_time = (select max(start_time) from price_map where
        zipcode = pd.zipcode_id and start_time <= pd.timestamp)
        where pd.timestamp between %s and %s
        and pd.house_id = %s
        group by datestamp''', (level,'Energy Use',  sd, ed, selected_address))
        result = cur.fetchall()
        print(result)
        dates = list()
        values = list()
        for data in result:
            dates.append(str(data[0]))
            values.append(data[1])

        consumption_data = {'dates': dates, 'values':values}
    conn.commit()
    cur.close()
    conn.close()
    return consumption_data