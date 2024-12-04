from .api.request import APIRequest     
from .api.cookie_jar import cookie
from geojson import Point
import traceback
import datetime
import redis
import json
import bson
import time
import math
import os

class marine(object):

    def __init__(self,
    request_mode: str = "curl_cffi",
    output: str = 'marine_output',
    redis_ip: str = "127.0.0.1",
    debug: bool = False,
    redis_db: int = 0,
    proxies: list = []
    ):
        self.Headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Origin":"https://marinetraffic.com","Vessel-Image": "00f0ff2a29c8a706c125c587294eb530cc10",
        "X-Requested-With": "XMLHttpRequest","Connection":"close"}
        self.time = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
        self.red = redis.Redis(host=redis_ip, port=6379, db=redis_db)
        self.base_url = 'https://www.marinetraffic.com'
        self.output = os.path.join(os.getcwd(),output)
        self.request_mode = request_mode
        self.cookies = cookie
        self.debug = debug
        #self.ship_list = []
    
    def request_api(self, bound=None,bar=False):
        
        self.send_request(bound=bound)
        response_object = self.res.get_content()["data"]["rows"]

        for data in response_object:
            output = os.path.join(self.output,data['SHIP_ID'])
            """
            note: Some ships are not trackable, meaning they dont have one id to track them for their coordinates
            these ships have a randomized base64 id which is 68 characters long, and are not trackable so in order
            to skip these ships only check for ship_ids that are less than 10 characters
            """
            if len(data['SHIP_ID']) < 10:
                self.save_data(data=data)

                # if data['SHIP_ID'] not in self.ship_list:
                #     self.ship_list.append(data['SHIP_ID'])
                # else:
                #     self.update_details(data=data,output=output)

        bar.title('[INF] Tracking Marines:')
        bar()
            
    def send_request(self,bound):
        try:
            self.res = APIRequest(f"{self.base_url}{bound}",headers=self.Headers,debug=self.debug)
            if self.res._APIRequest__response.headers.get("Set-Cookie"):
                for i in self.res._APIRequest__response.headers["Set-Cookie"].split(";"):
                    if "__cf_bm" in i:
                        cf = i.split("=")
                        if '.marinetraffic.com, __cf_bm' in cf:
                            self.cookies.update({"__cf_bm":cf[cf.index('.marinetraffic.com, __cf_bm')+1]})
                        else:
                            self.cookies.update({"__cf_bm":cf[cf.index('__cf_bm')+1]})

                        with open('utils/api/cookie_jar.py', 'w+') as file:
                            file.write(f"cookie={self.cookies}")
        except Exception as e:
            print(e)
            print(f"status code:{self.res.status_code}")
    def save_data(self,data):
        try:
            Point((float(data['LON']), float(data['LAT'])))
            
            temp_list=[]
            temp_list.append(float(data.pop('LAT')))
            temp_list.append(float(data.pop('LON')))
            temp_list.append(data.pop('HEADING'))
            temp_list.append(data.pop('SPEED'))
            temp_list.append(self.time)
            data.update({"trail":[temp_list]})
            #print(temp_list)

            if self.red.get(f"stale_ship:{data['SHIP_ID']}") != None:
                ship_data = json.loads(self.red.get(f"stale_ship:{data['SHIP_ID']}"))
                if not math.isclose(float(ship_data['trail'][0][0]), temp_list[0], rel_tol=1e-9, abs_tol=0.0) or not math.isclose(float(ship_data['trail'][0][1]), temp_list[1], rel_tol=1e-4, abs_tol=0.0):
                    print(f"set NEW_outofstale {data['SHIP_ID']}")
                    self.red.setex(f"ship:{data['SHIP_ID']}",1800,json.dumps(data))
                # else:
                #     print(f"set STALE {data['SHIP_ID']}")
                #     self.red.delete(f"ship:{data['SHIP_ID']}")
                #     self.red.setex(f"stale_ship:{data['SHIP_ID']}",1800,json.dumps(data))
            
            # elif self.red.get(f"stale_ship:{data['SHIP_ID']}") != None:
            #     ship_data = json.loads(self.red.get(f"stale_ship:{data['SHIP_ID']}"))
            #     if not math.isclose(float(ship_data['trail'][0][0]), temp_list[0], rel_tol=1e-4, abs_tol=0.0) or not math.isclose(float(ship_data['trail'][0][1]), temp_list[1], rel_tol=1e-4, abs_tol=0.0):
            #         self.red.setex(f"ship:{data['SHIP_ID']}",1800,json.dumps(data))
            #         self.red.delete(f"stale_ship:{data['SHIP_ID']}")

                # else:
                #     #DELETE THIS LSTER
                #     print(f"same coords: SHIP_ID:{data["SHIP_ID"]}=, {ship_data['trail'][0][0]}={temp_list[0]} or {ship_data['trail'][0][1]}={temp_list[1]}")
            else:
                print(f"set NEW {data['SHIP_ID']}")
                self.red.setex(f"ship:{data['SHIP_ID']}",1800,json.dumps(data))


            # if not os.path.exists(output):
            #     os.makedirs(output)
            # with open(f"{output}/Radar_Data.bson", 'wb') as file:
            #     file.write(bson.dumps(data))

        except Exception:
            error = f"[DEBUG-MARINE]Marine get_details function Error: {traceback.format_exc()}\n"
            print(error)
            # with open('../logfile', 'a+') as file:
            #     file.write(error)

    def update_details(self,data,output):
        try:
            Point((float(data['LON']), float(data['LAT'])))

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
                    file.close()
            with open(f"{output}/Radar_Data.bson", 'wb') as file:
                file.write(a)
                file.close()
        except Exception:
            error = f"[DEBUG-MARINE]Marine update_details function Error: {traceback.format_exc()}\n"
            print(error)
            with open('../logfile', 'a+') as file:
                file.write(error)


    # def get_details(self,bound=None,bar=False):
    #     self.req(bound=bound)

    #     bar()
    #     #print(vars(self.res._APIRequest__response))
    #     res2 = self.res.get_content()["data"]["rows"]
    #     for data in res2:
    #         self.save_details(data=data)

    



    
