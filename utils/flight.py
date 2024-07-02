from FlightRadar24 import FlightRadar24API
from multiprocessing.pool import ThreadPool
from discord_webhook import DiscordWebhook, DiscordEmbed
from requests.adapters import HTTPAdapter, Retry
import requests
from alive_progress import alive_bar
import geojson
from geojson import Feature, Point, FeatureCollection
#import numpy as np
import os
from .bounds.flight_bounds import bounds as flight_bounds
from typing import Optional
from datetime import date
import gzip
import bson
import threading
import subprocess
import argparse
import json
import time
import random
import ijson
import traceback

fr_api = FlightRadar24API(...)
lock = threading.Lock()
na_regs = [] # stores flights with 'N/A' Registration value
counter = 0
check_last=0
geojson_datas = []
reg_nums=[] # strores list of registration numbers
temp_regnums=[] # stores a newer list of registration numbers to compare with ref_nums
empty_regs=[]
departure={}    #holds a list of key, value registrationNumber:Departure time
temp_data={}
geojson_statics = '{"type": "FeatureCollection", "features": ['
flights = []
ids=[]
local_array = threading.local()
flight_bounds = flight_bounds[0:500]
with open('logfile','a+') as file:
    file.write(f"\n\nDate: {date.today()}\n")
    file.close()
def discord(title, description):
    webhook = DiscordWebhook(
        url="https://discord.com/api/webhooks/1103661510162653305/Z5GQvXU4VqcCilQTFyBGEbZzp52gxL-XSme1cQF-ACrrlz-3v_z17tMJlF55aWfZSz0X",
        rate_limit_retry=True)
    embed = DiscordEmbed(
        title=title,
        description=description,
        color='65535')
    webhook.add_embed(embed)
    response = webhook.execute()

os.system('cls' if os.name == 'nt' else 'clear')
def extract_values(obj,local_array):
    if not hasattr(local_array, 'value'):
        local_array.value = []
    for i in obj['trail']:
        temp=[]
        for k, v in i.items():
            if v is None:
                temp.append('N/A')
            else:
                temp.append(v)
            
        local_array.value.append(temp)
    obj['trail']=local_array.value
    obj['aircraft'].pop('images')
    return obj


def get_flights(bound,bar=False,update=reg_nums,local_array=[],debug=False):
    global temp_array
    global reg_nums
    global ids
    bounds = fr_api.get_bounds(bound)
    flights = fr_api.get_flights(bounds=bounds)
    # if not isinstance(flights, list):
    #     print("[DEBUG] in not instance (get_flights)")
    #     return 

    if debug:
        if len(flights) == 1500:
            print('[DEBUG] Hit 1500 Limit')
    for j in flights:
        if j.registration != 'N/A':
            ids.append(j.id)
            update.append(j.registration)
    
        else:
            empty_regs.append(j.id)
    if bar!=False:
        bar.title('[INF] Getting Flights:')
        bar()

    temp_regnums=[]

def handle_internet_outage(temp_data,local_array):
    
    while True:
        try:
            response = requests.get('http://www.google.com', timeout=5)
            if response.status_code == 200:
                print("[DEBUG] IN HANDLE_NET_OUTAGE FUNCTION")
                for i,v in temp_data.items():
                    get_details(_id=v['id'],local_array=local_array)
                return
        except Exception as e:
            print(f"[DEBUG] Error in handle_outage {e}")
            pass


def update_path(reg_num,local_array):
    global temp_data
    try:
        flight = fr_api.get_flights(registration=reg_num) #see if you can just use the reg_nums list instead of fetching the data again
        # if not isinstance(flight,list):
        #     print("[DEBUG] in not instance (update_path)")
        #     handle_internet_outage(temp_data,local_array) 

        if flight:
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

                get_details(_id=flight[0].id,bar=False,local_array=local_array)
            
    except Exception as e:
        error = traceback.format_exc()
        #print(F"[DEBUG] ERROR IN update path FUNCTION: {reg_num}-{error}")

        with open('logfile','a+') as file:
            file.write(f"{error}-reg:{reg_num}\n")
        pass

def get_details(_id,bar=False,local_array=[]):
    global temp_data 

    if bar!=False:
        bar.title('[INF] Fetching Flight Data:')
        bar()
    try:
        flight = fr_api.get_flight_details(_id)
        # if not isinstance(flight,dict):
        #     print("[DEBUG] in not instance (get_details)")
        #     handle_internet_outage(temp_data,local_array) 
        
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
 
        with open(f"output/{reg_num}/{departure}", "wb") as file:
            file.write(bson.dumps(flight))
        local_array.value=[]

    except Exception as e:
        error = traceback.format_exc()
        #print(F"[DEBUG] ERROR IN VERBOUSE FUNCTION: {e}")
        with open('logfile','a+') as file:
            file.write(f"{error}\n")
        pass
def handle_nones(_id,local_array=[]):
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
     
def flight(
                v: bool = False ,
                airport: bool = False,
                getflights: bool = False,
                track: bool = False,
                qgis: str = 'false',
                intervals: int = 2,
                threads: int = 5,
                output: Optional[str] = "output.json",
                qgis_file: str = "qgis_output.json",
                debug = False
                
):
    global reg_nums
    global temp_regnums
    global departure
    global ids
    global counter
    global empty_regs
    if not os.path.exists(f"output/No-Registration"):
                os.makedirs(f"output/No-Registration")
    if v:
            
        local_array = threading.local()
        #open("flightNum.temp", "w").close()

        with alive_bar(len(flight_bounds),spinner='twirls') as bar:
            with ThreadPool(processes=threads) as pool:
                results = [pool.apply_async(get_flights, (bound,bar,reg_nums)) for bound in flight_bounds]
                for r in results:
                    r.get()
    

        ids = sorted(set(ids))
        print(f"[INF] FLIGHT COUNT: {len(ids)}")
        reg_nums = sorted(set(reg_nums))
        empty_regs = sorted(set(empty_regs))

        if debug:
            print(f"[DEBUG] EMPTY REGISTER COUNT: {len(empty_regs)}")
            ids=ids[20:30]
            reg_nums = reg_nums[20:30]

        with alive_bar(len(ids),theme='smooth') as bar:
            with ThreadPool(processes=threads) as pool:
                results = [pool.apply_async(get_details, (_id,bar,local_array)) for _id in ids]
                for r in results:
                    r.get()
        os.system('cls' if os.name == 'nt' else 'clear')
        counter=0
        with alive_bar(1,length=3,stats=False,monitor=False) as bar:
            bar.title('Tacking Flights')
            while True:
                reg_nums=[]
                ids=[]
                empty_regs=[]
                with ThreadPool(processes=threads) as pool:
                    results = [pool.apply_async(get_flights, (bound,False,reg_nums,local_array)) for bound in flight_bounds]
                    for r in results:
                        r.get()

                reg_nums = sorted(set(reg_nums))
                empty_regs = sorted(set(empty_regs))  
                #_id = sorted(set(_id))
                if debug:
                    reg_nums=reg_nums[20:30]
                for reg in reg_nums:
                    if not os.path.exists(f"output/{reg}"):
                        os.makedirs(f"output/{reg}")
                # with ThreadPool(processes=1) as pool:
                #     results = [pool.apply_async(update_list, (local_array,temp_regnums)) for bound in flight_bounds]
                #     for r in results:
                #         r.get()
                with ThreadPool(processes=threads) as pool:
                    results = [pool.apply_async(update_path, (reg_num,local_array)) for reg_num in reg_nums]
                    for r in results:
                        r.get()

                counter+=1
                if counter==20:
                    #print("[DEBUG] IN HANDLE-NONES FUNCTION")

                    with ThreadPool(processes=threads) as pool:
                        results = [pool.apply_async(handle_nones, (_id,local_array)) for _id in empty_regs]
                        for r in results:
                            r.get()
                        counter = 0
    def marine(
        threads: int = 5
    ):

        Headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
        "Vessel-Image": "000f4a9e1bs81e7e1fbe47024f3615125330","X-Requested-With": "XMLHttpRequest"}
        
        base_url='https://www.marinetraffic.com'







    if track:
        while True:
            with alive_bar(len(flight_bounds),spinner='twirls') as bar:
                with ThreadPool(processes=threads) as pool:
                    results = [pool.apply_async(get_flights, (bound,bar,reg_nums)) for bound in flight_bounds]
                    for r in results:
                        r.get()
            reg_nums = sorted(set(ids))
            print(len(ids))
            ids=[]
