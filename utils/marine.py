import time
import datetime
from geojson import Feature, Point, FeatureCollection
import sys
import threading
import os
from .api.request import APIRequest     
import bson
from alive_progress import alive_bar
from multiprocessing.pool import ThreadPool
import traceback


class marine(object):


    def __init__(self,
    output: str = 'marine_output'
    ):
        self.output = os.path.join(os.getcwd(),output)
        self.Headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Origin":"https://marinetraffic.com","Vessel-Image": "000f4a9e1bs81e7e1fbe47024f3615125330","X-Requested-With": "XMLHttpRequest"}
        self.cookies = {"__cf_bm":"BU3Es3ROtILyqGVRZ8TRwGRCHNvTQMmGE02CuCC.wk0-1709039154-1.0-ATDcWbU7BgSvu7AEv/yrJlufKY1QiOSzqyuRwn5yaY8vKdrM3suCaKKB5qQfTW4MNpN1GRmFfjwxhO+nGtnaRbA="}
        self.base_url = 'https://www.marinetraffic.com'
        self.time = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')

    def req(self,bound):

        self.res = APIRequest(f"{self.base_url}{bound}",headers=self.Headers,cookies=self.cookies)
        for i in self.res._APIRequest__response.headers["Set-Cookie"].split(";"):
            #print(i)
            if "__cf_bm" in i:
                print(f"[DEBUG] New cookies:{self.cookies}")
                self.cookies.update({"__cf_bm":i.split("=")[2]})
        #print(res._APIRequest__response.headers["Set-Cookie"])

    def get_details(self,bound=None,bar=False):
        self.req(bound=bound)

        bar()
        print(vars(self.res._APIRequest__response))
        res2 = self.res.get_content()["data"]["rows"]
        for data in res2:
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
                    #self.output = os.path.join(self.output,'No_IDs')
                    with open(f"{self.output}/{data['SHIP_ID']}_{self.time}.bson", 'wb') as file:
                        file.write(bson.dumps(data))

                else:
                    if not os.path.exists(f"{self.output}/{data['SHIP_ID']}"):
                        os.makedirs(f"{self.output}/{data['SHIP_ID']}")
                    with open(f"{self.output}/{data['SHIP_ID']}/Radar_Data.bson", 'wb') as file:
                        file.write(bson.dumps(data))
            except Exception as e:
                #TO-DO: ADD LOGGING HERE
                error = traceback.format_exc()
                print(f"[DEBUG]Marine get_details function Error: {error}")

def update(self, bound=None,bar=False):
    req(bound=bound)

    



    
