

def get_details(_id,bar=False,local_array=[]):
    global temp_data 

    if bar!=False:
        bar.title('[INF] Fetching Flight Data:')
        bar()
    try:
        flight = fr_api.get_flight_details(_id)
        
        if flight.get('aircraft') and flight['aircraft'].get('registration'):
            reg_num=flight['aircraft']['registration']
        
        else:
            handle_nones(_id,local_array)
            return

        if flight.get('time'):
            departure = flight['time']['scheduled']['departure']
        elif flight.get('trail'):
            if len(flight['trail']) != 0:
                departure = flight['trail'][0]['ts']
        else:
            return
        if departure == 0 or departure == None:
            departure = str(time.time()).split('.')[0]

        if not os.path.exists(f"output/{reg_num}"):
            os.makedirs(f"output/{reg_num}")

        temp_data.update({reg_num:{"departure":departure,"id":_id}})
        extract_values(flight,local_array=local_array)
        # nparr = np.array([local_array.value,local_array.value2],dtype=object)
        # np.save(f"output/{reg_num}/{departure}", nparr) 
        with open(f"output/{reg_num}/{departure}", "wb") as file:
            file.write(bson.dumps(flight))
        local_array.value=[]

    except Exception as e:
        error = traceback.format_exc()
        #print(F"[DEBUG] ERROR IN VERBOUSE FUNCTION: {e}")
        with open('logfile','a+') as file:
            file.write(f"{error}\n")
        pass

def handle_nones(_id,local_array):
    try:
        flight = fr_api.get_flight_details(_id)
        if flight.get('time'):
            departure = flight['time']['scheduled']['departure']
        elif flight.get('trail'):
            if len(flight['trail']) != 0:
                departure = flight['trail'][0]['ts']
        else:
            return
        extract_values(flight,local_array=local_array)
        with open(f"output/No-Registration/{str(time.time()).split('.')[0]}_{_id}", "wb") as file:
            file.write(bson.dumps(flight))
            
    except Exception as e:
        error = traceback.format_exc()
        #print(f'[DEBUG] ERROR IN Handle_Nones FUNCTION: {e}')
        with open('logfile','a+') as file:
            file.write(f"{error}\n")
        pass


def update_path(reg_num,local_array):
    # global temp_data
    global temp_data
    try:
        flight = fr_api.get_flights(registration=reg_num)

        if flight:
            #print("[DEBUG] IN UPDATE-PATH TRY")
            if temp_data.get(reg_num) and flight[0].id == temp_data[reg_num]["id"]:
                data=['N/A','N/A','N/A','N/A','N/A','N/A']
                flight = vars(flight[0])
                if flight.get('latitude'):
                    data[0]=flight['latitude']
                if flight.get('longitude'):
                    data[1]=flight['longitude']
                if flight.get('altitude'):
                    data[2]=flight['altitude']
                if flight.get('ground_speed'):
                    data[3]=flight['ground_speed']
                if flight.get('time'):
                    data[4]=flight['time']
                if flight.get('heading'):
                    data[5]=flight['heading']
                with open(f"output/{reg_num}/{temp_data[reg_num]['departure']}", 'rb') as file:
                    a = bson.loads(file.read())
                    a['trail'].append(data)
                    a = bson.dumps(a)
                with open(f"output/{reg_num}/{temp_data[reg_num]['departure']}", 'wb') as file:
                    file.write(a)

            else:
                #print(f"[DEBUG] NEW FLIGHT: {reg_num}")
                if temp_data.get(reg_num):
                    print("change in flight")
                    temp_data.pop(reg_num)

                #print("new new flight")
                get_details(_id=flight[0].id,bar=False,local_array=local_array)
            