from flask import Flask, request,jsonify
from datetime import datetime, date
import logging
from typing import List, Tuple, Dict, Optional
import time
import re
import pymysql
import requests
import json
import pprint

import csv

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

username = "pdtpatrick"
password = "u3!WL2uC0dxu"
# in seconds
current_time = int(time.time()) #currentTime in second
start_time   =  3600 * 48 # 48h in the past  
end_time = int(time.time())
# airport code
# airport = "KSEA" # Frankfurt


airport = "EDDF"  # Frankfurt


def read_airport(filename: str) -> Dict[str, str]:
    keys = [
        "id",
        "name",
        "city",
        "country",
        "IATA",
        "ICAO",
        "latitude",
        "longitude",
        "altitude",
        "timezone",
        "dst",
        "tz",
        "type",
        "source",
    ]
    airports = csv.DictReader(
        open(filename,encoding="utf-8"), delimiter=",", quotechar='"', fieldnames=keys
    )
    d = {airport["ICAO"]: airport for airport in airports}
    return d


def call_api(airport: str = None) -> Dict[str, str]:
    """Call opensky API and return all departures

    begin = now - days ago
    end = now
    """
    current_time = time.time()
    URL = f"https://opensky-network.org/api/flights/departure?airport={airport}&begin={int(current_time) - start_time}&end={int(current_time)}"
    logging.info(f"URL is now: {URL}")
    r = requests.get(URL, auth=(username, password))
    if r.status_code == 404:
        logging.error("Cannot find data")
        
        return None
    assert len(r.json()) != 0
    return r.json()

def process_coordinates(start_time: int, end_time: int) -> List[Dict[str, str]]:
    """Process Coordinates
    Pull data from opensky api, read the csv and create an output like:
    List[Dict[Dict[str, str]]]
    Meaning, we'll have a List[Airport[Coordinates[longitude, latitude]]]
    """
    
    #read data from csv file and store in variable
    data_from_csv = read_airport("airports.csv")
    
    #initialize a list with an empty dictionary
    outputData = [{}]
    
  
    
    
    #make a call to the api and iterate through the data it is sending back to us
    for departures in call_api(airport):
        #from the data we got from the api we retrieve the departureAirport and arrivalAirports and store in a variable 
        arrival_airport = departures["estArrivalAirport"]
        departure_airport = departures["estDepartureAirport"]
        
        #check to see if the arrivalAirport is present in our dictionary we got from the csv file to avoid keyError
        if arrival_airport in data_from_csv:
            #if the key exists in our dictionary then we get the longitude and latitudes of the arrivalAirport
            arr_longitude = data_from_csv[arrival_airport]['longitude']
            arr_latitude = data_from_csv[arrival_airport]['latitude']
        
         
        #check to see if the departureAirport is present in our dictionary we got from the csv file to avoid keyError
        if departure_airport in data_from_csv:
             #if the key exists in our dictionary then we get the longitude and latitudes of the departureAirport
            dep_longitude = data_from_csv[departure_airport]['longitude']
            dep_latitude = data_from_csv[departure_airport]['latitude']
        
        #after getting the lats. and long. of both arrival and departureAirports we then check in our list if the arrival airport exists if not we append it to the list to avoid keyError
        if arrival_airport not in outputData[0]:
            outputData.append({arrival_airport:{
                "latitude" : arr_latitude,
                "longitude" : arr_longitude
                
            }})
        
    #return the list of dict of dict in a json format [{{}}]
    return json.dumps(outputData)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

def process_flights(start_time: int, end_time: int) -> List[Dict[str, str]]:
    """Process flight information
    Call the opensky api; this will return List[Dict[str, sr]]  
    Remember our final output, we want to return:
    List[Dict[str, str]]
    In the Dict, we'll have departure, arrival. So something like:
    Dict[departure, arrival]
    The shouldn't be duplicates in your json returned. 
    """
   
   #delare an empty list 
    outputData = []
    
    #make a call to the api and store the returned data
    data_from_api = call_api(airport)
   
    #loop through the returned data
    for flight in data_from_api:
        #get the departure and arrival Flights 
        dept = flight['estDepartureAirport']
        arrival = flight['estArrivalAirport']
        
        #append them to the list in a dictionary object
        outputData.append({dept : arrival})
              
    #return output in json format
    return json.dumps(outputData)
    

@app.route('/')
def index() -> str:
    """use this as a test to show your app works"""
    
    #to test if my api is working a make a call when the page is being loaded
    return jsonify(call_api(airport))


#url: http://localhost/flights?start_time={startTime}&end_time={endTime}
@app.route('/flights' )
def flights() -> str:
    """API for flight information

    your API will receive `start_time` and `end_time`
    Your API will return a json in the form of
    [
        {departure_airport: destination_airport},
        {departure_airport: destination_airport}
    ]

    Remember to add some logging so it is easy for you
    to troubleshoot. 

    Once you have your initial version, think about how you can
    scale your API. Also think about how you can speed it up
    """
    request.args.get('start_time')
    request.args.get('end_time')
    
    start_time   =  3600 * 48 # 48h in the past  
    end_time = int(time.time())
    return process_flights(start_time, end_time)


#url: http://localhost/coordinates?start_time={startTime}&end_time={endTime}
@app.route('/coordinates')
def coordinates() -> str:
    """API for coordinate information

    your API will receive `start_time` and `end_time`
    Your API will return a json in the form of
    [
        {departure_airport: 
            {
                "longitude": long,
                "latitude": lat
            }
        },
        {departure_airport: 
            {
                "longitude": long,
                "latitude": lat
            }
        },
    ]

    Remember to add some logging so it is easy for you
    to troubleshoot. 

    Once you have your initial version, think about how you can
    scale your API. Also think about how you can speed it up
    """
    request.args.get('start_time')
    request.args.get('end_time')
    start_time   =  3600 * 48 # 48h in the past  
    end_time = int(time.time())
    
    return process_coordinates(start_time, end_time)



if __name__ == "__main__":
    app.run(debug=True)
