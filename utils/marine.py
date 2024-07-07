import time
import datetime
from geojson import Feature, Point, FeatureCollection
import sys
import threading
import os
from .api.request import APIRequest     
import bson
from .api.cookie_jar import cookie
from alive_progress import alive_bar
from multiprocessing.pool import ThreadPool
import traceback


class marine(object):


    def __init__(self,
    output: str = 'marine_output',
    debug: bool = False
    ):
        self.output = os.path.join(os.getcwd(),output)
        self.Headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Origin":"https://marinetraffic.com","Vessel-Image": "00c7885e5cc1f67312156576569fa2f77a30","X-Requested-With": "XMLHttpRequest"}
        self.cookies = cookie
        self.base_url = 'https://www.marinetraffic.com'
        self.time = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        self.debug = debug
        self.ship_list = []
    
    def req(self,bound):

        self.res = APIRequest(f"{self.base_url}{bound}",headers=self.Headers,cookies=self.cookies,debug=self.debug)
        if self.res._APIRequest__response.headers.get("Set-Cookie"):
            for i in self.res._APIRequest__response.headers["Set-Cookie"].split(";"):
                if "__cf_bm" in i:
                    #print(i)
                    cf = i.split("=")
                    if '.marinetraffic.com, __cf_bm' in cf:
                        self.cookies.update({"__cf_bm":cf[cf.index('.marinetraffic.com, __cf_bm')+1]})
                    else:
                        self.cookies.update({"__cf_bm":cf[cf.index('__cf_bm')+1]})

                    with open('utils/api/cookie_jar.py', 'w+') as file:
                        file.write(f"cookie={self.cookies}")

            
    def save_details(self,data):
        try:
            points = Point((float(data['LON']), float(data['LAT'])))
            
            temp_list=[]
            data.update({"trail":[]})
            temp_list.append(data.pop('LAT'))
            temp_list.append(data.pop('LON'))
            temp_list.append(data.pop('HEADING'))
            temp_list.append(data.pop('SPEED'))
            temp_list.append(self.time)
            data['trail'].append(temp_list)

            if len(data['SHIP_ID']) > 10:
                return
                #self.output = os.path.join(self.output,'No_IDs')
                with open(f"{self.output}/{data['SHIP_ID']}_{self.time}.bson", 'wb') as file:
                    file.write(bson.dumps(data))

            else:
                output = os.path.join(self.output,data['SHIP_ID'])
                if not os.path.exists(output):
                    os.makedirs(output)
                with open(f"{output}/Radar_Data.bson", 'wb') as file:
                    file.write(bson.dumps(data))
        except Exception as e:
            error = f"[DEBUG-MARINE]Marine get_details function Error: {traceback.format_exc()}\n"
            print(error)
            with open('../logfile', 'a+') as file:
                file.write(error)

    def update_details(self,data,output):
        try:
            points = Point((float(data['LON']), float(data['LAT'])))

            temp_list=[]
            temp_list.append(data.pop('LAT'))
            temp_list.append(data.pop('LON'))
            temp_list.append(data.pop('HEADING'))
            temp_list.append(data.pop('SPEED'))
            temp_list.append(self.time)
            with open(f"{output}/Radar_Data.bson", 'rb') as file:
                    a = bson.loads(file.read())
                    if temp_list[0] == a['trail'][0] and temp_list[1] == a['trail'][1]:
                        return
                    a['trail'].append(temp_list)
                    a = bson.dumps(a)
            with open(f"{output}/Radar_Data.bson", 'wb') as file:
                file.write(a)
        except Exception as e:
            error = f"[DEBUG-MARINE]Marine update_details function Error: {traceback.format_exc()}\n"
            print(error)
            with open('../logfile', 'a+') as file:
                file.write(error)

    def fetcher(self, bound=None,bar=False):
        self.req(bound=bound)

        res2 = self.res.get_content()["data"]["rows"]

        for data in res2:
            output = os.path.join(self.output,data['SHIP_ID'])
            if len(data['SHIP_ID']) < 10:
                if not data['SHIP_ID'] in self.ship_list:
                    self.ship_list.append(data['SHIP_ID'])
                    if not os.path.exists(f"{output}"):
                        self.save_details(data=data)
                    else:
                        self.update_details(data=data,output=output)
        print(len(self.ship_list))
        bar.title('[INF] Tracking Marines:')
        bar()
            
    def get_details(self,bound=None,bar=False):
        self.req(bound=bound)

        bar()
        #print(vars(self.res._APIRequest__response))
        res2 = self.res.get_content()["data"]["rows"]
        for data in res2:
            self.save_details(data=data)

    



    
