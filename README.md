# radar 
Radar is an scraping tool that gathers Flight and Marine data from trusted sources like FlightRadar24 and marinetraffic.com and stores them in bson format for the least storage usage.

# Usage:
1. Clone the package
2. go to the radar directory and run `python -r requirements.txt`.
3. Run `python radar.py [-flight,-marine] -t (number) [-debug]` to start the radar.

features:
- You can determine the number of threads
- Flight data will be saved in flight_output folder and marine will be in marine_output
- You can transform the raw data into Geojson format (Incase you want to use them in Qgis and Arcgis apps),  
- All the limitation are bypassed and incase of internet outage, the program will complete the data on the next connection.
- Use -debug to see debug status.

