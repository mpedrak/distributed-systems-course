from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
import requests
import json 
import base64
import matplotlib.pyplot as plot
import numpy
import os

# http://localhost:8000/docs

geocode_api_key = ""

if not os.path.exists("configuration.json"):
    print("No configuration.json file.")
    exit(1)

with open("configuration.json", "r", encoding="utf-8") as file:
    configuration = file.read()

configuration = json.loads(configuration)
geocode_api_key = configuration["geocode_api_key"]

if geocode_api_key == "":
    print("Wrong geocode_api_key.")
    exit(1)

app = FastAPI()

@app.get("/")
async def start():
    with open("request.html", "r", encoding="utf-8") as file:
        request_page = file.read()      
    return HTMLResponse(content=request_page, status_code=status.HTTP_200_OK)

@app.get("/result")
async def get_result(country : str, city : str, days : int = 14):
    if days < 2 or days > 90: 
        return get_error_page(status.HTTP_400_BAD_REQUEST, "Liczba dni do sprawdzenia musi być z zakresu od 2 do 90.")

    coordinates_json_response = await get_coordinates(country, city)

    if coordinates_json_response.status_code == status.HTTP_400_BAD_REQUEST: 
        return get_error_page(status.HTTP_400_BAD_REQUEST, "Podano złą nazwę kraju lub miasta.")
      
    if coordinates_json_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS: 
        return get_error_page(status.HTTP_429_TOO_MANY_REQUESTS, "Zbyt dużo jednoczesnych zapytań. Poczekaj 1s.")
    
    if coordinates_json_response.status_code != status.HTTP_200_OK: 
        return get_error_page(coordinates_json_response.status_code, "Błąd serwera https://geocode.maps.co/.")
        
    coordinates = json.loads(coordinates_json_response.body.decode("utf-8"))

    temperatures_json_response = await get_temperatures(coordinates["latitude"], coordinates["longitude"], days)

    if temperatures_json_response.status_code != status.HTTP_200_OK: 
        return get_error_page(temperatures_json_response.status_code, "Błąd serwera https://open-meteo.com/ : " + temperatures_json_response.body.decode("utf-8"))
    
    temperatures = json.loads(temperatures_json_response.body.decode("utf-8"))

    exceeded_count = get_exceeded_count(temperatures, days)
    month = temperatures["month"]

    with open("response.html", "r", encoding="utf-8") as file:
        response_page = file.read()

    with open("graph.png", "rb") as image:
        graph = base64.b64encode(image.read())

    graph = "data:image/png;base64," + str(graph)[2 : -1]
    response_page = response_page.replace("<img src=\"\">", "<img src=\"" + graph +"\">") 
    os.remove("graph.png")

    response_page = response_page.replace("<h1 id=\"location\"> </h1>", "<h1 id=\"location\">" + city + ", " + country +  "</h1>")

    if float(coordinates["latitude"]) < 0: xy = coordinates["latitude"][1 : ] + "°S, "
    else: xy = coordinates["latitude"] + "°N, "

    if float(coordinates["longitude"]) < 0: xy += coordinates["longitude"][1 : ] + "°W"
    else: xy += coordinates["longitude"] + "°E"

    response_page = response_page.replace("<div id=\"xy\"> </div>", "<div id=\"xy\">" + xy + "</div>")

    if month <= 8:
        return_message = "W ostatnich " + str(days) + " dniach, średnia dobowa temperatura była wyższa niż 7°C " + str(exceeded_count) + " razy" 
        if exceeded_count == days: return_message += ", a więc należy zmienić opony na letnie."
        else: return_message +=  ", a więc nie jest wskazana zmiana opon."

    else:
        return_message = "W ostatnich " + str(days) + " dniach, średnia dobowa temperatura była niższa niż 7°C " + str(exceeded_count) + " razy" 
        if exceeded_count == days: return_message += ", a więc należy zmienić opony na zimowe."
        else: return_message +=  ", a więc nie jest wskazana zmiana opon."

    response_page = response_page.replace("<div id=\"stats\"> </div>", "<div id=\"stats\">" + return_message + "</div>")

    return HTMLResponse(content=response_page, status_code=status.HTTP_200_OK)

@app.get("/coordinates")
async def get_coordinates(country : str, city : str):
    URL = "https://geocode.maps.co/search?country=" + country + "&city=" + city + "&api_key=" + geocode_api_key
    
    response = requests.get(URL)
    if response.status_code != status.HTTP_200_OK: return JSONResponse(status_code=response.status_code, content="")

    json_data = json.loads(response.text)
    if len(json_data) == 0: return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="")

    data = json_data[0]
    return JSONResponse(status_code=status.HTTP_200_OK, content={"latitude" : data["lat"], "longitude" : data["lon"]})

@app.get("/temperatures")
async def get_temperatures(latitude : str, longitude : str, days : int):
    URL = "https://api.open-meteo.com/v1/forecast?latitude=" + latitude + "&longitude=" + longitude +"&past_days=" + str(days) + "&hourly=temperature_2m"
    
    response = requests.get(URL)
    if response.status_code != status.HTTP_200_OK and response.status_code != status.HTTP_400_BAD_REQUEST: return JSONResponse(status_code=response.status_code, content="")

    if response.status_code == status.HTTP_400_BAD_REQUEST:
        error = json.loads(response.text)["reason"]
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error)

    data = json.loads(response.text)["hourly"]
    return JSONResponse(status_code=status.HTTP_200_OK, content={"temperatures" : data["temperature_2m"][0 : -(7 * 24)], "month" : int(data["time"][-(7 * 24) - 1][5 : 7])}) 

@app.exception_handler(404)
async def page_not_found(_, __):
    return get_error_page(status.HTTP_404_NOT_FOUND, "Nie znaleziono strony.")

@app.exception_handler(RequestValidationError)
async def unprocessable_entity(_, exception):
    details = ""
    for error in exception.errors():
        for key, value in error.items(): details += str(key) + " : " + str(value) + "<br>"
        details += "<br>"

    return get_error_page(status.HTTP_400_BAD_REQUEST, "Niepoprawne zapytanie. <br><br>" + details)

def get_error_page(status_code : int, text : str):
    with open("error.html", "r", encoding="utf-8") as file:
            error_page = file.read()

    error_page = error_page.replace("<h1> </h1>", " <h1>" + "Error " + str(status_code) +"</h1>")
    error_page = error_page.replace("<div> </div>", " <div>" + text + "</div>")

    return HTMLResponse(content=error_page, status_code=status_code)

def get_exceeded_count(temperatures, days):
    month = temperatures["month"]
    exceeded = 0
    means = []

    for day in range(0, days):
        mean = 0
        for hour in range(0, 24): mean += temperatures["temperatures"][day * 24 + hour]
        mean /= 24
        means.append(mean)
        if (month <= 8 and mean > 7) or (month > 8 and mean < 7): exceeded += 1

    plot.close()
    plot.plot(means, "ro")
    plot.axline([0, 7], [days - 1, 7])
    plot.xlabel("Dni")
    plot.ylabel("Średnia dobowa temperatura w °C")
    plot.xticks(numpy.arange(0, days, 1))
    plot.yticks(numpy.arange(min(int(min(means)) - 1, 6) , max(int(max(means)) + 3, 8), 1))
    plot.savefig("graph.png")

    return exceeded
