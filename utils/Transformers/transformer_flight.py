import geojson
from geojson import Feature, FeatureCollection,LineString, MultiPoint,Point
from utils.set_details import set_detail
import bson
import os
import datetime
import traceback

#import mysql.connector
  
# dataBase = mysql.connector.connect(
#   host ="localhost",
#   user ="testuser",
#   passwd ="password",
#   database="Flights"
# )
 
# # preparing a cursor object
# cursorObject = dataBase.cursor()
 
# creating database

class transformer(object):

    """
    This class will transform the flight or marine data into a Geojson file/object
    
    it can read data from files (giving it the directory name it will iterate through the files itself) or straight from an object

    """
    def __init__(self, directory='output',
     obj=None,
     country=None,
     airline=None,
     feature_collection=True):

        self.directory = os.path.join(os.getcwd(),directory)
        self.obj = obj
        self.country = country
        self.airline = airline
        self.feature_collection = feature_collection
        if not os.path.exists(f"{self.directory}/GeoFiles/Flight"):
                os.makedirs(f"{self.directory}/GeoFiles/Flight")



    def trans_flight(self):
        #global _dict
        self._dict={}
        for root, dirs, files in os.walk(self.directory):
            if root==f"{self.directory}/GeoFiles/Flight":
                continue
            for file in files:
                try:
                    trail_list=[]
                    file_path = os.path.join(root, file)
                    output_path = os.path.join(self.directory,f"/GeoFiles/Flight/{file}")

                    with open(file_path, 'rb+') as openfile :
                        props = bson.loads(openfile.read())
                        if self.country:
                            output_path = os.path.join(self.directory,f"/GeoFiles/Flight/{self.country}/{file}")
                            try:
                                if props["airport"]["origin"]["position"]["country"]["name"] != self.country :
                                    continue 
                            except:
                                continue
                        if self.airline:
                            output_path = os.path.join(self.directory,f"/GeoFiles/Flight/{self.airline}/{file}")
                            try:
                                if props["airline"]["name"] != self.airline :
                                    continue 
                            except:
                                continue
                        trails = props.pop('trail')  
                        props = vars(set_detail(props))
                        self.extract_values(props)
                        if trails:
                            for trail in trails:
                                for i in trail:
                                    if i=='N/A':
                                        trail[trail.index('N/A')]=0

                                trail_list.append((trail[1], trail[0], trail[4], trail[5]))

                                """
                                Note:
                                In GeoJSON format, coordinates are ordered in longitude-latitude format, 
                                the same as X-Y coordinates in mathematics. But this is the opposite of Google Maps and some other web map tools, 
                                which place coordinate values in latitude-longitude format.
                                """
                        else:
                            continue
                        
                        transformed_data = self.line_transform(trail_list, self._dict)
                        if not os.path.exists(output_path):
                            os.makedirs(output_path)
                        with open(f"{output_path}/LineString.geojson","w+",encoding='utf-8') as openfile:
                            openfile.write(str(transformed_data))
                        
                        if self.feature_collection:
                            collection = self.Feature_collection(trail_list)
                            with open(f"{output_path}/Feature_Collection.geojson","w+",encoding='utf-8') as openfile:
                                openfile.write(str(collection))
                except Exception as e:
                    error = traceback.format_exc()
                    print(f"[DEBUG] ERROR IN FileTransformerer2 :\n {file_path} {error}")
                    # with open('logfile','a+') as file:
                    #     file.write(f"{error}\nFlight={flight}-{_id}"):
                    continue # REMOVE THIS AND FIX THE NULL PROBLEM

                    

    def line_transform(self,trail_list,props):
        points = LineString(trail_list)
        data_dict = Feature(geometry=points, properties=props)
        return data_dict
    def Feature_collection(self,trail_list):
        _list=[]
        for i in trail_list:
            f = Feature(geometry=Point((i[0], i[1])),properties={"lat":i[0],"lon":i[1],"timeStamp":f"{datetime.datetime.utcfromtimestamp(i[2]).strftime('%Y%m%d%H%M%S')}","heading":i[3]})
            _list.append(f)
        features = FeatureCollection(_list)
        return features


    # def save_to_sql(self):
    #     self._dict={}
    #     for root, dirs, files in os.walk(self.directory):
    #         if root==f"{self.directory}/GeoFiles/Flight":
    #             continue
    #         for file in files:
    #             trail_list=[]
    #             file_path = os.path.join(root, file)
    #             with open(file_path, 'rb+') as openfile:
    #                 props = bson.loads(openfile.read())
    #                 trails = props.pop('trail')  
    #                 props = vars(deset(props))
    #                 self.extract_values(props)
    #                 sql = "INSERT INTO Aircrafts (FlightNumber, OriginAirport, DestinationAirport, CurrentLatitude, CurrentLongitude, CurrentAltitude, CurrentSpeed, Timestamp)\
    #                 VALUES (%s,%s,%s,%s,%s,%s,%s,NOW());"

    #                 val = (str(self._dict['id'])[0:6], str(self._dict['origin_airport_country_name']), str(self._dict['destination_airport_name'])[0:19], self._dict['destination_airport_altitude'], self._dict['destination_airport_latitude'], self._dict['destination_airport_longitude'], 500)

    #                 cursorObject.execute(sql, val)
    #                 dataBase.commit()

    #                 # if trails:
    #                 #     for trail in trails:
    #                 #         trail_list.append((trail[0], trail[1], trail[4], trail[5])) 
    #                 # else:
    #                 #     continue



# geojson_statics = '"type": "FeatureCollection", "features": ['
    def extract_values(self,obj):
        #global self._dict
        # if not hasattr(local_array, 'value'):
        #     local_array.value = []
        if isinstance(obj, dict):
            for k, v in obj.items():

                if v is not None:
                    if isinstance(v, (int, float, str)):
                        self._dict.update({k:v})
                    elif isinstance(v, (dict, list)):
                        self.extract_values(v)
                else:
                    self._dict.update({k:'N/A'})  
        elif isinstance(obj, list):
            for item in obj:
                self.extract_values(item)
    