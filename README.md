# radar 
Radar is an scraping tool that gathers Flight and Marine data from trusted sources like FlightRadar24 and marinetraffic.com and stores them in bson format for the least storage usage.

# To gather Flight data:
`python radar.py -flight`

features:
- You can determine the number of threads
- Flight data will be saved in flight_output folder and marine will be in marine_output
- You can transform the raw data into Geojson format (Incase you want to use them in Qgis and Arcgis apps),  
- All the limitation are bypassed and incase of internet outage, the program will complete the data on the next connection.
- Use -debug to see debug status.

# To gather marine data:
`python radar.py -marine`
