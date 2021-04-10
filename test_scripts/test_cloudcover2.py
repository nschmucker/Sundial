# Python program to find current  
# weather details of any city 
# using climacell api 
  
# import required modules 
import requests

# Independence Hall
LAT =  39.95
LON = -75.15

# Enter your API key here 
API_KEY = "KEY"

# base_url variable to store url 
base_url = "https://data.climacell.co/v4/timelines?"

# complete url address 
url = base_url + \
      "location=" + str(LAT) + "," + str(LON) + \
      "&fields=cloudCover" + \
      "&timesteps=current" + \
      "&apikey=" + API_KEY 
  
# get method of requests module 
# return response object and convert to python-friendly type
r = requests.get(url)
j = r.json()

cloud_cover = j["data"]["timelines"][0]["intervals"][0]["values"]["cloudCover"]/100

print(cloud_cover)
