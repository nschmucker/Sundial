# Python program to find current  
# weather details of any city 
# using openweathermap api 
  
# import required modules 
import requests

# Independence Hall
LAT =  39.95
LON = -75.15

# Enter your API key here 
API_KEY = "KEY"
  
# base_url variable to store url 
base_url = "http://api.openweathermap.org/data/2.5/weather?"

# complete url address 
url = base_url + "lat=" + str(LAT) + "&lon=" + str(LON) + "&appid=" + API_KEY 
  
# get method of requests module 
# return response object and convert to python-friendly type
r = requests.get(url).json()

if r["cod"] != 401 and r["cod"] != 404:
    cloud_cover = r["clouds"]["all"]/100
else:
    cloud_cover = 0

print(cloud_cover)