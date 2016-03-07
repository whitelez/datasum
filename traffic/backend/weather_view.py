from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.utils import timezone # use timezone aware date, default timezone is set in settings.py
import json
import requests  # an http library for python
from datetime import date, time, datetime
from traffic.models import Weather_zipcode, Weather_zipcode_data

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def weather(request):
    return render(request, 'traffic/new_weather.html')

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def get_zipcode_areas(request):
    zipcodes = Weather_zipcode.objects.all()
    result = {"type": "FeatureCollection","features": []}
    for zip in zipcodes:
        feature = {"type":"Feature","properties": {"zipcode": zip.zipcode},"geometry": {"type": "Polygon", "coordinates": [json.loads(zip.geoJson)]}}
        result["features"].append(feature)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def get_weather(request):
    result = {"data":[]}
    # use Yahoo weather API
    url = "https://query.yahooapis.com/v1/public/yql"
    zips = [zip.zipcode for zip in Weather_zipcode.objects.all()]
    query = '''select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text in (%s))''' %",".join(zips)  # YQL query of Yahoo
    api_rsps = requests.get(url,{"q": query, "format": "json", "env": "store://datatables.org/alltableswithkeys"})
    weather_json = api_rsps.json()
    query_results = weather_json["query"]["results"]
    if query_results:
        result["status"] = "success"
        for i, zip_data in enumerate(query_results["channel"]):
            crnt_zip_data = {"zip": zips[i],"cond": zip_data["item"]["condition"]}
            result["data"].append(crnt_zip_data)
    else:
        result["status"] = "failed"
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

# interact with database
# for larger set of zipcode areas and larger user requests
# @permission_required(perm= 'traffic.perm_weather', raise_exception= True)
# def get_weather(request):
#     result = {"data":[]}
#     # use Yahoo weather API
#     url = "https://query.yahooapis.com/v1/public/yql"
#     # use timezone aware datetime to keep consistency, current timezone(set in settings.py) is used
#     # the MySQL database use UTC timezone, the datetime will be converted to UTC time when insert into the table
#     now = timezone.make_aware(datetime.now(), timezone.get_current_timezone())
#     for zip in Weather_zipcode_data.objects.all():
#         query_time = zip.query_time
#         # query api only when last query was at least 1 hour ago, due to api limitation (around 2000 times per day)
#         if query_time.date() != now.date() or query_time.time().hour != now.time().hour:
#             query = '''select item.condition from weather.forecast where woeid in (select woeid from geo.places(1) where text="%s")''' %zip.zipcode.zipcode  # YQL query of Yahoo
#             api_rsps = requests.get(url,{"q": query, "format": "json", "env": "store://datatables.org/alltableswithkeys"})
#             weather_json = api_rsps.json()
#             #zip.query_time = datetime.strptime(weather_json["query"]["created"], '%Y-%m-%dT%H:%M:%SZ')
#             zip.query_time = now
#             query_results = weather_json["query"]["results"]
#             if query_results:
#                 weather_data = query_results["channel"]["item"]["condition"]
#                 zip.code = int(weather_data["code"])
#                 zip.timestamp = weather_data["date"]
#                 zip.temp = int(weather_data["temp"])
#                 zip.text = weather_data["text"]
#             zip.save()
#         crnt_zip_data = {"zip":zip.zipcode.zipcode, "code": zip.code, "timestamp": zip.timestamp, "temp": zip.temp, "text": zip.text}
#         result["data"].append(crnt_zip_data)
#     response = json.dumps(result)
#     return HttpResponse(response, content_type='application/json')

