from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse, QueryDict
from django.db.models import Q
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required, permission_required

import json
import urllib2,urllib
import math,operator

from traffic.models import * #Meter, Parking, Street, Streetparking, TMC, TMC_data, Incidents, Weather
from datetime import date, time, datetime
import time as the_time
import xml.etree.ElementTree as XMLET

from django.db.models import Avg

import csv

def index(request):
    return render(request, 'traffic/index.html')

# Add by PXD - The new home page of Transit functions
def index2(request):
    return render(request, 'traffic/index2.html')
# +++++++++++++++++++++++++++++++++++++++++++++ #

@permission_required(perm= 'traffic.perm_camera', raise_exception= True)
def camera(request):
    return render(request, 'traffic/camera.html')

@permission_required(perm= 'traffic.perm_count', raise_exception= True)
def count(request):
    return render(request, 'traffic/count.html')

def ajaxtest(request):
    message = request.GET['time']
    result = {'message': message}
    j = json.dumps(result)
    return HttpResponse(j, content_type='application/json')

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def weather(request):
    return render(request, 'traffic/weather.html')

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def get_county_weather(request):
    state = request.GET['state']   
    county = request.GET['county']
    county = county.split(' ')
    county = '_'.join(word for word in county)
    url = 'http://api.wunderground.com/api/fa32a501f6cdbc7c/hourly/q/' + state + '/' + county + '.json'
    f = urllib2.urlopen(url)
    weather_info = f.read()
    weather_info = weather_info.split()
    weather_info = ''.join(item for item in weather_info)
    response = json.dumps(weather_info)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_weather', raise_exception= True)
def get_weather(request):
    #geo_list = []
    i=0
    now = datetime.now().time()
    for county in Weather.objects.all():
        if now.hour != county.update_time.hour:
            url = 'http://api.wunderground.com/api/fa32a501f6cdbc7c/hourly/q/' + county.state + '/' + urllib.quote(county.api) + '.json'
            f = urllib2.urlopen(url)
            #i=i+1
            #if i%5==0:
                #the_time.sleep(60)
            weather_info = f.read()
            weather_info = weather_info.split()
            weather_info = ''.join(item for item in weather_info)
            geo = json.loads(county.geoJson)
            weather_info = json.loads(weather_info)
            geo['properties']['weather'] = weather_info
            county.weather = json.dumps(geo)
            county.update_time = now
            county.save()
        #else:
            #weather_info = county.weather
        #geo = json.loads(county.geoJson)
        #weather_info = json.loads(weather_info)
        #geo['properties']['weather'] = weather_info
        #geo_list.append(json.dumps(geo))
    result = ','.join(county.weather for county in Weather.objects.all())
    result = '''{ "type": "FeatureCollection","features": [''' + result + ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_ev_station', raise_exception= True)
def ev_stations(request):
    return render(request, 'traffic/ev_stations.html')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def travel_time(request):
    tmcs = TMC.objects.all()
    return render(request, 'traffic/travel_time.html', {'n': range(1, 32), 'tmcs': tmcs})

#BY PXD
@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def travel_time_new(request):
    tmcs = TMC.objects.all()
    records = SPCCorridorNodeInfo.objects.all()
    corridors = []
    CorrNum = []
    for corridor in records:
        if not (corridor.Corridor_Number in CorrNum):
            flag = 0
            for temp in corridors:
                if corridor.Corridor_Number < temp.Corridor_Number:
                    break
                flag += 1
            CorrNum.append(corridor.Corridor_Number)
            corridors.insert(flag, corridor)
    return render(request, 'traffic/travel_time_new.html', {'corridors': corridors})

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def travel_time_corridorafter2013(request):
    records = SPCCorridorNodeInfo2013to2015.objects.all()
    corridors = []
    CorrNum = []
    for corridor in records:
        if not (corridor.Corridor_Number in CorrNum):
            flag = 0
            for temp in corridors:
                if corridor.Corridor_Number < temp.Corridor_Number:
                    break
                flag += 1
            CorrNum.append(corridor.Corridor_Number)
            corridors.insert(flag, corridor)
    return render(request, 'traffic/travel_time_corridorafter2013.html', {'corridors': corridors})

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_node_info(request):
    cornum = request.GET['cornum']
    nodes = SPCCorridorNodeInfo.objects.filter(Corridor_Number=cornum)
    result = '''{ "type": "FeatureCollection","features": ['''
    for node in nodes:
        result += '''{"type":"Feature","properties": {"Corridor_Number":''' + str(node.Corridor_Number) + \
                  ''',"Corridor_Name":"''' + node.Corridor_Name + '''","Node_Number":"''' + node.Node_Number + \
                  '''","Node_Name":"''' + node.Node_Name + '''"},"geometry": {"type": "Point", "coordinates": ['''\
                  + str(node.Longitude) + ',' + str(node.Latitude) + ']}},'
    result = result.rstrip(',')
    result += ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_node_info_2013to2015(request):
    cornum = request.GET['cornum']
    nodes = SPCCorridorNodeInfo2013to2015.objects.filter(Corridor_Number=cornum)
    result = '''{ "type": "FeatureCollection","features": ['''
    for node in nodes:
        result += '''{"type":"Feature","properties": {"Corridor_Number":''' + str(node.Corridor_Number) + \
                  ''',"Corridor_Name":"''' + node.Corridor_Name + '''","Node_Number":"''' + node.Node_Number + \
                  '''","Node_Name":"''' + node.Node_Name + '''"},"geometry": {"type": "Point", "coordinates": ['''\
                  + str(node.Longitude) + ',' + str(node.Latitude) + ']}},'
    result = result.rstrip(',')
    result += ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_spcyears(request):
    cornum = request.GET['cornum']
    records = SPCtraveltime.objects.filter(Corridor_Number=cornum)
    years = []
    for record in records:
        if not(record.Year in years):
            years.append(record.Year)
    result = '''{"features":['''
    for year in years:
        result += str(year) + ','
    result = result.rstrip(',')
    result += ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_spctraveltime_2013to2015(request):
    cornum0 = request.GET['cornum']
    Snode = request.GET['Snode']
    Enode = request.GET['Enode']

    if Snode <= Enode:
        delta = 1
    else:
        delta = -1

    info = {}
    for hour in range(24):
        for min in [0.0, 0.25, 0.5, 0.75]:
            info[hour+min] = [0, 0]

    cornum = int(cornum0)
    Currentnode = Snode
    while Currentnode != Enode:
        nextnode = chr(ord(Currentnode) + delta)
        records = SPCtraveltime2013to2015.objects.filter(Corridor_Number=cornum, Start_Node=Currentnode, End_Node=nextnode)
        for record in records:
            if (info[record.Time][0] == 'NULL') or (not(isinstance(record.Travel_Time, (int, long, float, complex)))):
                info[record.Time][0] = 'NULL'
                info[record.Time][1] = 'NULL'
            else:
                info[record.Time][0] += record.Travel_Time
                info[record.Time][1] += record.Travel_Time - record.Travel_Time_At_Posted_Speed_Limit
        Currentnode = nextnode

    response = '''['''
    for hour in range(24):
        for min in [0.0, 0.25, 0.5, 0.75]:
            time = hour + min
            if info[time][0] == "NULL":
                response += '''{"spctraveltime":"''' + info[time][0]
            else:
                response += '''{"spctraveltime":"''' + str(info[time][0]/60)[0:5]
            if info[time][1] == "NULL":
                response += '''", "spcdelay":"''' + info[time][1] + '''"},'''
            else:
                response += '''", "spcdelay":"''' + str(info[time][1]/60)[0:5] + '''"},'''
    response = response.rstrip(',')
    response += ']'
    response2 = json.dumps(response)
    return HttpResponse(response2, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_spctraveltime(request):
    cornum = request.GET['cornum']
    year = request.GET['year']
    Snode = request.GET['Snode']
    Enode = request.GET['Enode']
    isam = request.GET['isam']
    if Snode <= Enode:
        records = SPCtraveltime.objects.filter(Corridor_Number=cornum, Year=year, Direction='A')
    else:
        records = SPCtraveltime.objects.filter(Corridor_Number=cornum, Year=year, Direction='Z')

    result = []
    total = 0
    for record in records:
        total += 1
        flag = 0
        for temp in result:
            if record.id < temp.id:
                break
            flag += 1
        result.insert(flag, record)

    spctraveltime = 0
    spcdelay = 0
    flag_traveltime = True
    Snode = int(Snode)
    Enode = int(Enode)
    isam = int(isam)
    if Snode > Enode:
        Snode = total - Snode + 2
        Enode = total - Enode + 2
    for i in range(Snode-1, Enode-1):
        if i >= total:
            i = total - 1
        if isam == 1:
            if result[i].AM_Travel_Time != None:
                spctraveltime += result[i].AM_Travel_Time
            else:
                flag_traveltime = False
            if result[i].AM_Delay_Per_Vehicle != None:
                spcdelay += result[i].AM_Delay_Per_Vehicle
            else:
                spcdelay += result[i].AM_Travel_Time - result[i].Travel_Time_At_Posted_Speed_Limit
        else:
            if result[i].PM_Travel_Time != None:
                spctraveltime += result[i].PM_Travel_Time
            else:
                flag_traveltime = False
            if result[i].PM_Delay_Per_Vehicle != None:
                spcdelay += result[i].PM_Delay_Per_Vehicle
            else:
                spcdelay += result[i].PM_Travel_Time - result[i].Travel_Time_At_Posted_Speed_Limit

    response = '''{"spctraveltime":"'''
    if flag_traveltime:
        response += str(spctraveltime)[0:4] + '''", "spcdelay":"''' + str(spcdelay)[0:4] + '''"'''
    else:
        response += '''N/A", "spcdelay":"N/A"'''

    response += '}'
    response2 = json.dumps(response)
    return HttpResponse(response2, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_spctraveltimeformanyyears(request):
    cornum = request.GET['cornum']
    years = request.GET['years']
    Snode = request.GET['Snode']
    Enode = request.GET['Enode']
    isam = request.GET['isam']

    response = "["
    allyear = years.split("+")
    for year2 in allyear:
        year = int(year2)
        if Snode <= Enode:
            records = SPCtraveltime.objects.filter(Corridor_Number=cornum, Year=year, Direction='A')
        else:
            records = SPCtraveltime.objects.filter(Corridor_Number=cornum, Year=year, Direction='Z')

        result = []
        total = 0
        for record in records:
            total += 1
            flag = 0
            for temp in result:
                if record.id < temp.id:
                    break
                flag += 1
            result.insert(flag, record)

        spctraveltime = 0
        spcdelay = 0
        flag_traveltime = True
        # flag_delay = True
        Snode = int(Snode)
        Enode = int(Enode)
        isam = int(isam)
        if Snode > Enode:
            Snode = total - Snode + 2
            Enode = total - Enode + 2
        for i in range(Snode-1, Enode-1):
            if i >= total:
                i = total - 1
            if isam == 1:
                if result[i].AM_Travel_Time != None:
                    spctraveltime += result[i].AM_Travel_Time
                else:
                    flag_traveltime = False
                if result[i].AM_Delay_Per_Vehicle != None:
                    spcdelay += result[i].AM_Delay_Per_Vehicle
                else:
                    spcdelay += result[i].AM_Travel_Time - result[i].Travel_Time_At_Posted_Speed_Limit
            else:
                if result[i].PM_Travel_Time != None:
                    spctraveltime += result[i].PM_Travel_Time
                else:
                    flag_traveltime = False
                if result[i].PM_Delay_Per_Vehicle != None:
                    spcdelay += result[i].PM_Delay_Per_Vehicle
                else:
                    spcdelay += result[i].PM_Travel_Time - result[i].Travel_Time_At_Posted_Speed_Limit

        response += '''{"spctraveltime":"'''
        if flag_traveltime:
            response += str(spctraveltime)[0:4] + '''", "spcdelay":"''' + str(spcdelay)[0:4] + '''"},'''
        else:
            response += '''N/A", "spcdelay":"N/A"},'''

    response = response.rstrip(',')
    response += ']'
    response2 = json.dumps(response)
    return HttpResponse(response2, content_type='application/json')
#END

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_travel_time(request):
    t1 = request.GET['tmc1']
    t2 = request.GET['tmc2']
    s_date = request.GET['s_date']
    s_time = request.GET['s_time']
    s_month = int(s_date[0:2])
    s_day = int(s_date[2:4])
    s_hour = int(s_time[0:2])
    s_minute = int(s_time[2:4])
    e_date = request.GET['e_date']
    e_time = request.GET['e_time']
    e_month = int(e_date[0:2])
    e_day = int(e_date[2:4])
    e_hour = int(e_time[0:2])
    e_minute = int(e_time[2:4])
    start_date = date(2013, s_month, s_day)
    end_date = date(2013, e_month, e_day)
    start_time = time(s_hour, s_minute)
    end_time = time(e_hour, e_minute)
    tmc1 = TMC.objects.get(tmc=t1)
    tmc2 = TMC.objects.get(tmc=t2)
    rd = tmc1.road
    dir = tmc1.direction
    if rd != tmc2.road or dir != tmc2.direction:
        return
    o1 = tmc1.road_order
    o2 = tmc2.road_order
    if o1 > o2:
        max_o = o1
        min_o = o2
    else:
        max_o = o2
        min_o = o1
    tmc_set = TMC.objects.filter(road = rd, direction = dir, road_order__range=(min_o,max_o))
    tmc_geometry_list = [{"type":"Feature","properties": {"TMC": tmc.tmc ,"road": tmc.road,"direction":tmc.direction ,"intersection":tmc.intersection ,"miles":tmc.miles,"road_order":tmc.road_order},"geometry": {"type": "MultiPoint", "coordinates": [[tmc.s_lon ,tmc.s_lat],[tmc.e_lon ,tmc.e_lat]]}} for tmc in tmc_set]
    #tmc_geometry = ','.join('''{"type":"Feature","properties": {"TMC":"''' + tmc.tmc + '''","road":"''' + tmc.road +'''","direction":"''' + tmc.direction + '''","intersection":"''' + tmc.intersection + '''","miles":''' + str(tmc.miles) + ''',"road_order":''' + str(tmc.road_order) + '''},"geometry": {"type": "MultiPoint", "coordinates": [[''' + str(tmc.s_lon) + ',' + str(tmc.s_lat) + '],[' + str(tmc.e_lon) + ',' + str(tmc.e_lat) +']]}}' for tmc in tmc_set)
    tmc_geometry = {"type": "FeatureCollection","features":tmc_geometry_list}
    tmc_number = tmc_set.count()
    total = 0
    miles = 0
    alltimeavg = {}
    alltime95 = {}
    freeflowtime = 0
    for tmc in tmc_set:
        avg = 0
        miles += tmc.miles
        data = TMC_data.objects.filter(tmc_id=tmc.tmc, date__range=(start_date, end_date))
        #avg = TMC_data.objects.filter(tmc_id=tmc.tmc, date__range=(start_date, end_date),time__range=(start_time, end_time)).aggregate(Avg('travel_time'))['travel_time__avg']
        #data_time_range = data.filter(time__range=(start_time, end_time))
        #n = data_time_range.count()
        # for record in data_time_range:
        #     #pass
        #     avg += record.travel_time
        #avg = sum([record.travel_time for record in data_time_range])
        avg = data.filter(time__range=(start_time, end_time)).aggregate(Avg('travel_time'))['travel_time__avg']
        #avg = avg/n
        total += avg
        # By PXD
        difftime = {}
        for record in data:
            key = str(record.time)
            if key not in difftime.keys():
                difftime[key] = [record.travel_time]
            else:
                difftime[key].append(record.travel_time)
        for key in difftime.keys():
            s2 = sorted(difftime[key])
            temp = 0
            for entry in s2:
                temp += entry
            if key not in alltimeavg.keys():
                alltimeavg[key] = temp/len(s2)
                alltime95[key] = s2[int(len(s2)*0.95)]
            else:
                alltimeavg[key] += temp/len(s2)
                alltime95[key] += s2[int(len(s2)*0.95)]
        freeflowtime += (tmc.miles/tmc.reference_speed)*60
        #End

    speed = miles/total*60
    truck_total = total*(1+max(speed-40, 0)/50)
    truck_speed = miles/truck_total*60
    result = {"travel_time": total,"speed": speed,"truck_travel_time":truck_total ,"truck_speed":truck_speed,"tmc_geometry":tmc_geometry}
    #By PXD
    result["freeflowtime"] = freeflowtime
    result["allavg"] =[{"key":key,"value":alltimeavg[key]} for key in alltimeavg.keys()]
    result["all95"] = [{"key":key,"value":alltime95[key]} for key in alltime95.keys()]
    #End
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_travel_time_prediction(request):
    t1 = request.GET['tmc1']
    t2 = request.GET['tmc2']
    p_date = request.GET['date']
    s_time = request.GET['s_time']
    e_time = request.GET['e_time']
    month = int(p_date[0:2])
    day = int(p_date[2:4])
    s_hour = int(s_time[0:2])
    s_minute = int(s_time[2:4])
    e_hour = int(e_time[0:2])
    e_minute = int(e_time[2:4])
    h_date = date(2013, month, day)
    start_time = time(s_hour, s_minute)
    end_time = time(e_hour, e_minute)
    tmc1 = TMC.objects.get(tmc=t1)
    tmc2 = TMC.objects.get(tmc=t2)
    rd = tmc1.road
    dir = tmc1.direction
    if rd != tmc2.road or dir != tmc2.direction:
        return
    o1 = tmc1.road_order
    o2 = tmc2.road_order
    if o1 > o2:
        max = o1
        min = o2
    else:
        max = o2
        min = o1
    tmc_set = TMC.objects.filter(road = rd, direction = dir, road_order__range=(min,max))
    tmc_number = tmc_set.count()
    total = 0
    for tmc in tmc_set:
        avg = 0
        #data = tmc.tmc_data_set.filter(date__range=(start_date,end_date), time__range=(start_time, end_time))
        data = TMC_data.objects.filter(tmc_id=tmc.tmc, date=h_date, time__range=(start_time, end_time))
        n = data.count()
        for record in data:
            avg += record.travel_time
            avg = avg/n
        total += avg
    result = '{"travel_time":' + str(total) + '}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')  

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def get_road_tmc(request):
    input_tmc = request.GET['tmc']
    s_tmc = TMC.objects.get(tmc = input_tmc)
    tmc_set = TMC.objects.filter(road = s_tmc.road, direction = s_tmc.direction)
    result = { "type": "FeatureCollection","features": []}
    result["features"] = [{"type":"Feature","properties": {"TMC":tmc.tmc,"road":tmc.road,"direction":tmc.direction,"intersection":tmc.intersection,"miles":tmc.miles,"road_order":tmc.road_order},"geometry": {"type": "MultiPoint", "coordinates": [[tmc.s_lon,tmc.s_lat],[tmc.e_lon,tmc.e_lat]]}} for tmc in tmc_set]
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

##def get_incidents_rcrs(request):
##    s_date = request.GET['s_date']
##    e_date = request.GET['e_date']
##    s_time = request.GET['s_time']
##    e_time = request.GET['e_time']
##    s_hour = int(s_time[0:2])
##    s_minute = int(s_time[2:4])
##    e_hour = int(e_time[0:2])
##    e_minute = int(e_time[2:4])
##    start_date = date(int(s_date[0:4]),int(s_date[4:6]), int(s_date[6:8]))
##    end_date = date(int(e_date[0:4]),int(e_date[4:6]), int(e_date[6:8]))
##    start_time = time(s_hour, s_minute)
##    end_time = time(e_hour, e_minute)
##    incidents = Incidents.objects.filter(close_date__range=(start_date, end_date), close_time__range=(start_time, end_time))
##    result = '''{ "type": "FeatureCollection","features": ['''
##    for inc in incidents:
##        s_dt = datetime(inc.close_date.year, inc.close_date.month, inc.close_date.day, inc.close_time.hour, inc.close_time.minute, inc.close_time.second)
##        e_dt = datetime(inc.open_date.year, inc.open_date.month, inc.open_date.day, inc.open_time.hour, inc.open_time.minute, inc.open_time.second)
##        result += '''{"type":"Feature","properties": {"eventid":"'''+ inc.eventid +'''","start":"''' + str(s_dt) + '''","end":"''' + str(e_dt) +'''","duration":"''' + str(e_dt-s_dt) + '''","cause":"''' + inc.cause + '''","status":"''' + inc.status + '''","sr":"'''+ inc.sr +'''"},"geometry": {"type": "MultiPoint", "coordinates": [[''' + str(inc.s_lon) + ',' + str(inc.s_lat) + '],[' + str(inc.e_lon) + ',' + str(inc.e_lat) +']]}},'
##    result = result.rstrip(',')
##    result += ']}'
##    response = json.dumps(result)
##    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_incident', raise_exception= True)
def get_incidents_rcrs(request):
    s_date = request.GET['s_date']
    e_date = request.GET['e_date']
    s_time = request.GET['s_time']
    e_time = request.GET['e_time']
    s_hour = int(s_time[0:2])
    s_minute = int(s_time[2:4])
    e_hour = int(e_time[0:2])
    e_minute = int(e_time[2:4])
    start_date = date(int(s_date[0:4]),int(s_date[4:6]), int(s_date[6:8]))
    end_date = date(int(e_date[0:4]),int(e_date[4:6]), int(e_date[6:8]))
    start_time = time(s_hour, s_minute)
    end_time = time(e_hour, e_minute)
    incidents = Incidents.objects.filter(close_date__range=(start_date, end_date), close_time__range=(start_time, end_time))
    result = ','.join(inc.geoJson for inc in incidents)
    result = '''{ "type": "FeatureCollection","features": [''' + result + ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_incident', raise_exception= True)
def incidents(request):
    return render(request, 'traffic/incidents.html',{'n':range(1,32)})

@permission_required(perm= 'traffic.perm_download', raise_exception= True)
def download(request):
    return render(request, 'traffic/download.html',{'months':range(1,13), 'months14': range(1,9) ,'days':range(1,32)})


# +++++++++++++++++++++++++++++++++++++  Views for Transit function begin here:  +++++++++++++++++++++++++++++++++++++++++++

# Aggregate the shape and stop information of each bus route
# To run this function: 1. Create a url and run it in explorer (will cause no response, just save in database)
#                       2. Write If name == "__main__": run transit_data() and run this view.py
def transit_data(request):
    for route in Route.objects.all():
        print route.route_id
        trips = route.trip_set.filter(headsign__contains='Inbound')
        if trips.count() > 0:
            trip_inbound = trips[0]
            if trip_inbound.shape_id:
                coordinates = ','.join('[' + str(shape.lon) + ',' + str(shape.lat) +']' for shape in Transit_shape.objects.filter(shape_id = trip_inbound.shape_id))
                coordinates ='''{"type":"Feature","properties": {"route_id":"'''+ route.route_id +'''","short_name":"''' + route.short_name + '''","long_name":''' + route.long_name +''',"type":''' + route.route_type + '''},"geometry": {"type": "LineString", "coordinates": [''' + coordinates + ']}}'
            else:
                coordinates = ''
            stops = ','.join( '''{"type":"Feature","properties": {"stop_id":"'''+ stop.stop_id.stop_id +'''","name":''' + stop.stop_id.name + ''',"order":''' + str(stop.stop_sequence) + '''},"geometry": {"type": "Point", "coordinates": [''' + str(stop.stop_id.lon) + ',' + str(stop.stop_id.lat) + ']}}' for stop in trip_inbound.stop_time_set.all())
            stops = '''{ "type": "FeatureCollection","features": [''' + stops + ']}'
            route.inbound_geoJson = coordinates
            route.inbound_stops_geoJson = stops
        trips = route.trip_set.filter(headsign__contains='Outbound')
        if trips.count() > 0:
            trip_outbound = trips[0]
            if trip_outbound.shape_id:
                coordinates = ','.join('[' + str(shape.lon) + ',' + str(shape.lat) +']' for shape in Transit_shape.objects.filter(shape_id = trip_outbound.shape_id))
                coordinates ='''{"type":"Feature","properties": {"route_id":"'''+ route.route_id +'''","short_name":"''' + route.short_name + '''","long_name":''' + route.long_name +''',"type":''' + route.route_type + '''},"geometry": {"type": "LineString", "coordinates": [''' + coordinates + ']}}'
            else:
                coordinates = ''
            stops = ','.join( '''{"type":"Feature","properties": {"stop_id":"'''+ stop.stop_id.stop_id +'''","name":''' + stop.stop_id.name + ''',"order":''' + str(stop.stop_sequence) + '''},"geometry": {"type": "Point", "coordinates": [''' + str(stop.stop_id.lon) + ',' + str(stop.stop_id.lat) + ']}}' for stop in trip_outbound.stop_time_set.all())
            stops = '''{ "type": "FeatureCollection","features": [''' + stops + ']}'
            route.outbound_geoJson = coordinates
            route.outbound_stops_geoJson = stops
        route.save()

def get_route(request):
    route_name = request.GET['route']
    direction = request.GET['direction']
    route = Route.objects.filter(short_name=route_name)[0]
    if direction == 'I':
        result = route.inbound_geoJson
    else:
        result = route.outbound_geoJson
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def get_stops(request):
    route_name = request.GET['route']
    direction = request.GET['direction']
    route = Route.objects.filter(short_name=route_name)[0]
    if direction == 'I':
        result = route.inbound_stops_geoJson
    else:
        result = route.outbound_stops_geoJson
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def get_trips(request):
    route = request.GET["route"]
    gtfs_name = request.GET["gtfs_name"]
    if request.GET["direction"] == 'I':
        direction = '1'
    else:
        direction = '0'
    result = []
    trip_data = Trip.objects.filter(route_id=route, direction_id=direction, GTFS=gtfs_name)
    for item in trip_data:
        temp = {}
        a = Stop_time.objects.filter(trip_id=item.trip_id, stop_sequence=1, GTFS=gtfs_name)[0]
        if a:
            temp["initial_time"] = a.departure_time
        else:
            temp["initial_time"] = 'N/A'
        temp["trip_id"] = item.trip_id
        if len(item.service_id) != 1:
            temp["day_of_week"] = item.service_id.split('-')[2]
        else:
            if item.service_id == 'W':
                temp["day_of_week"] = "Weekday"
            elif item.service_id == 'S':
                temp["day_of_week"] = "Saturday"
            else:
                temp["day_of_week"] = "Sunday"
        result.append(temp)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_ontimeperformance_byroute(request):
    routes = [{"route_value": route.short_name+"+"+route.route_id, "route_shortname": route.short_name} for route in Route.objects.all()]
    return render(request, 'traffic/transit_ontimeperformance_byroute.html', {'routes': routes})

def transit_ontimeperformance_bystop(request):
    stops = [{"stop_id": stop.stop_id, "stop_name": stop.name} for stop in Stop.objects.all()]
    return render(request, 'traffic/transit_ontimeperformance_bystop.html', {'stops': stops})

def transit_schedule(request):
    gtfs = [record['GTFS'] for record in GTFS_calendar.objects.all().values('GTFS').distinct()]
    routes = [{"route_value": route.short_name+"+"+route.route_id, "route_shortname": route.short_name} for route in Route.objects.all()]
    return render(request, 'traffic/transit_schedule.html', {'routes': routes, 'GTFS':gtfs})

def transit_waitingtime_byroute(request):
    gtfs = [record['GTFS'] for record in GTFS_calendar.objects.all().values('GTFS').distinct()]
    routes = [{"route_value": route.short_name+"+"+route.route_id, "route_shortname": route.short_name} for route in Route.objects.all()]
    return render(request, 'traffic/transit_waitingtime_byroute.html', {'routes': routes, 'GTFS':gtfs})

def transit_waitingtime_bystop(request):
    gtfs = [record['GTFS'] for record in GTFS_calendar.objects.all().values('GTFS').distinct()]
    stops = [{"stop_id": stop.stop_id, "stop_name": stop.name} for stop in Stop.objects.all()]
    return render(request, 'traffic/transit_waitingtime_bystop.html', {'stops': stops, 'GTFS':gtfs})

def transit_crowding(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit_crowding.html', {'routes': routes})

def transit_crowding_hm(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit_crowding_hm.html', {'routes': routes})

def transit_bunching(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit_bunching.html', {'routes': routes})

def transit_bunching_hm(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit_busbunching_hm.html', {'routes': routes})

def transit_bustraveltime(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit_bustraveltime.html', {'routes': routes})

def get_stop_routes(request):
    stop_id = request.GET["stop"]
    routes = Stop_route.objects.filter(stop_id=stop_id)
    result = {"type": "FeatureCollection", "features": []}
    for route in routes:
        r = Route.objects.filter(route_id=route.route_id)[0]
        if route.direction == "I":
            load = json.loads(r.inbound_geoJson)
            load["properties"]["dir"] = "Inbound"
            result["features"].append(load)
        else:
            load = json.loads(r.outbound_geoJson)
            load["properties"]["dir"] = "Outbound"
            result["features"].append(load)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

# Temporarily no use ################################################
def get_range_routes(request):
    stop1 = request.GET["stop1"]
    stop2 = request.GET["stop2"]
    routes1 = Stop_route.objects.filter(stop_id = stop1)
    route_set1 = set()
    for route in routes1:
        route_set1.add(route.route_id+route.direction)
    routes2 = Stop_route.objects.filter(stop_id = stop2)
    route_set2 = set()
    for route in routes2:
        route_set2.add(route.route_id+route.direction)
    routes = route_set1.intersection(route_set2)
    result = {"type": "FeatureCollection", "features": []}
    for route in routes:
        route_id = route[:-1]
        direction = route[-1]
        r = Route.objects.filter(route_id = route_id)[0]
        if direction == "I":
            result["features"].append(json.loads(r.inbound_geoJson))
        else:
            result["features"].append(json.loads(r.outbound_geoJson))
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')
#####################################################################

#bus_real_time
def bus_real_time(request):
    route = request.GET["rt"]
    url = "http://truetime.portauthority.org/bustime/api/v1/getvehicles?key=AX2AUxF9WBp8xdjHBTXEr8gn5&format=json&rt=" + route
    link = urllib2.urlopen(url)
    url_rsps = link.read()
    vehicles = json.loads(url_rsps)
    result = {"status": "", "msg": "", "geoJson": {}}
    if "error" in vehicles["bustime-response"]:
        result["status"] = "error"
        result["msg"] = vehicles["bustime-response"]["error"]["msg"]
    else:
        result["status"] = "success"
        geoJson = {"type": "FeatureCollection", "features": []}
        if isinstance(vehicles["bustime-response"]["vehicle"], dict):
            feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(vehicles["bustime-response"]["vehicle"]["lon"]), float(vehicles["bustime-response"]["vehicle"]["lat"])]}, "properties": vehicles["bustime-response"]["vehicle"]}
            geoJson["features"].append(feature)
        else:
            for vehicle in vehicles["bustime-response"]["vehicle"]:
                feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(vehicle["lon"]), float(vehicle["lat"])]}, "properties": vehicle}
                geoJson["features"].append(feature)
        result["geoJson"] = geoJson
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_op_byroute(request):
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"].split('+')[0]:
            route = item.route_number_in_APCAVL
            break
    # route_id = request.GET["rt"].split('+')[1]
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stops = request.GET["stops"].split(",")

    result = {}
    for stopid in stops:
        result[stopid] = []
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(route), dir=str(direction), date__range=(s_date, e_date))
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                mystr = str(item.schtim)
                scheduled_time = int(mystr[:-2])*3600 + int(mystr[-2:])*60
                if item.stopa == 1:
                    result[stopid].append(float(item.dhour*3600 + item.dminute*60 + item.dsecond - scheduled_time)/60.0)
                else:
                    result[stopid].append(float(item.hour*3600 + item.minute*60 + item.second - scheduled_time)/60.0)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_op_bystop(request):
    routedict = Route_dict.objects.all()
    routes = request.GET["routes"].split(",")
    stopid = request.GET["stop"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    result = {}
    for route in routes:
        routename = ''
        for item in routedict:
            if item.short_name == route.split("-")[0]:
                routename = item.route_number_in_APCAVL
                break
        direction = route.split("-")[1]
        if direction == "Inbound":
            direction = "1"
        else:
            direction = "0"
        result[route] = []
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(routename), dir=str(direction), date__range=(s_date, e_date))
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                mystr = str(item.schtim)
                scheduled_time = int(mystr[:-2])*3600 + int(mystr[-2:])*60
                if item.stopa == 1:
                    result[route].append(float(item.dhour*3600 + item.dminute*60 + item.dsecond - scheduled_time)/60.0)
                else:
                    result[route].append(float(item.hour*3600 + item.minute*60 + item.second - scheduled_time)/60.0)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_schedule_opt(request):
    # gtfs_name = request.GET["gtfs_name"]
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"]:
            route = item.route_number_in_APCAVL
            break
    day = request.GET["tripinfo"].split("+")[0]
    if day == "Weekday":
        day = "1"
    elif day == "Saturday":
        day = "2"
    else:
        day = "3"
    time = request.GET["tripinfo"].split("+")[1]
    time = str(int(time.split(":")[0])*100 + int(time.split(":")[1]))
    # tripid = request.GET["tripinfo"].split("+")[2]
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stops = request.GET["stops"].split(",")
    result = {}
    for stopid in stops:
        result[stopid] = []
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(dow=day, tripa=time, qstopa='  '+str(stopid), route=str(route), dir=str(direction), date__range=(s_date, e_date))
        for item in data:
            if item.schtim != 9999:
                # if 1st stop, deviation = departure_time - schedule_time; if not, dev = arrival_time - schedule time (in minutes)
                mystr = str(item.schtim)
                scheduled_time = int(mystr[:-2])*3600 + int(mystr[-2:])*60
                if item.stopa == 1:
                    result[stopid].append(float(item.dhour*3600 + item.dminute*60 + item.dsecond - scheduled_time)/60.0)
                else:
                    result[stopid].append(float(item.hour*3600 + item.minute*60 + item.second - scheduled_time)/60.0)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_wt_byroute(request):
    gtfs_name = request.GET["gtfs_name"]
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"].split('+')[0]:
            route = item.route_number_in_APCAVL
            break
    route_id = request.GET["rt"].split('+')[1]
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stops = request.GET["stops"].split(",")

    # Obtain all trip IDs of selected route, direction and GTFS version for next stop_time query in the for loop below
    tripdata = Trip.objects.filter(GTFS=gtfs_name, route_id=route_id, direction_id=str(direction))
    tripid = {"Weekday": [], "Saturday": [], "Sunday": []}
    for item in tripdata:
        if item.service_id == "W":
            tripid["Weekday"].append(item.trip_id)
        elif item.service_id == "S":
            tripid["Saturday"].append(item.trip_id)
        elif item.service_id.split("-")[2] in ["Weekday", "Saturday", "Sunday"]:
            tripid[str(item.service_id.split("-")[2])].append(item.trip_id)
        elif item.service_id == "U":
            tripid["Sunday"].append(item.trip_id)

    result = {}
    for stopid in stops:
        # In list: 0 - SWT; 1 - AWT; 2 - EWT;
        result[stopid] = {"Weekday": [], "Saturday": [], "Sunday": []}

        # Calculate Scheduled Waiting Time for each selected stop
        stoptimedata = Stop_time.objects.filter(GTFS=gtfs_name, stop_id=stopid)
        stoptime = {"Weekday": [], "Saturday": [], "Sunday": []}
        for item2 in stoptimedata:
            scheduled_time = int(item2.arrival_time.split(":")[0]+item2.arrival_time.split(":")[1])
            if scheduled_time >= s_time and scheduled_time <= e_time:
                temp = int(item2.arrival_time.split(":")[0])*60 + int(item2.arrival_time.split(":")[1])
                if item2.trip_id in tripid["Weekday"]:
                    stoptime["Weekday"].append(temp)
                elif item2.trip_id in tripid["Saturday"]:
                    stoptime["Saturday"].append(temp)
                elif item2.trip_id in tripid["Sunday"]:
                    stoptime["Sunday"].append(temp)
        for token in ["Weekday", "Saturday", "Sunday"]:
            if len(stoptime[token]) > 1:
                new = sorted(stoptime[token])
                pre = new[0]
                nu = 0
                de = 0
                for item3 in new:
                    nu += float((item3 - pre)**2)/2.0
                    de += item3 - pre
                    pre = item3
                result[stopid][token].append(float(nu)/float(de))
            else:
                result[stopid][token].append(0)

        # Calculate Actual Waiting Time for each selected stop
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(route), dir=str(direction), date__range=(s_date, e_date))
        stoptime = {"Weekday": {}, "Saturday": {}, "Sunday": {}}
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                temp = int(item.hour)*60 + int(item.minute)
                if item.dow == "1":
                    if stoptime["Weekday"].has_key(item.date):
                        stoptime["Weekday"][item.date].append(temp)
                    else:
                        stoptime["Weekday"][item.date] = []
                        stoptime["Weekday"][item.date].append(temp)
               # Temporarily no APC/AVL data for Saturday and Sunday !!
                # elif item2.dow == "2":
                #     stoptime["Saturday"].append(temp)
                # elif item2.dow == "3":
                #     stoptime["Sunday"].append(temp)
        avg = 0
        daycount = 0
        for token in stoptime["Weekday"].keys():
            if len(stoptime["Weekday"][token]) > 1:
                new = sorted(stoptime["Weekday"][token])
                pre = new[0]
                nu = 0
                de = 0
                for item3 in new:
                    nu += float((item3 - pre)**2)/2.0
                    de += item3 - pre
                    pre = item3
                if float(de) != 0:
                    avg += float(nu)/float(de)
                    daycount += 1
        if daycount > 0:
            result[stopid]["Weekday"].append(float(avg)/float(daycount))
        else:
            result[stopid]["Weekday"].append(0)

        # Temporarily no APC/AVL data for Saturday and Sunday, so use SWT ratio to estimate AWT on weekend.
        if result[stopid]["Weekday"][0] == 0:
            result[stopid]["Saturday"].append(0)
            result[stopid]["Sunday"].append(0)
        else:
            result[stopid]["Saturday"].append(result[stopid]["Weekday"][1] * (result[stopid]["Saturday"][0]/result[stopid]["Weekday"][0]))
            result[stopid]["Sunday"].append(result[stopid]["Weekday"][1] * (result[stopid]["Sunday"][0]/result[stopid]["Weekday"][0]))

        # Calculate Excess Waiting Time for each selected stop
        for token in ["Weekday", "Saturday", "Sunday"]:
            result[stopid][token].append(result[stopid][token][1] - result[stopid][token][0])

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_wt_bystop(request):
    gtfs_name = request.GET["gtfs_name"]
    routedict = Route_dict.objects.all()
    routes = request.GET["routes"].split(",")
    stopid = request.GET["stop"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))

    stoptimedata = Stop_time.objects.filter(GTFS=gtfs_name, stop_id=stopid)

    result = {}
    for route in routes:
        routename = ''
        for item in routedict:
            if item.short_name == route.split("-")[0]:
                routename = item.route_number_in_APCAVL
                break
        direction = route.split("-")[1]
        if direction == "Inbound":
            direction = "1"
        else:
            direction = "0"

        route_id = ''
        for item in Route.objects.filter(short_name=route.split("-")[0]):
            route_id = item.route_id
            break

        # Obtain all trip IDs of selected route, direction and GTFS version for next stop_time query in the for loop below
        tripdata = Trip.objects.filter(GTFS=gtfs_name, route_id=route_id, direction_id=str(direction))
        tripid = {"Weekday": [], "Saturday": [], "Sunday": []}
        for item in tripdata:
            if item.service_id == "W":
                tripid["Weekday"].append(item.trip_id)
            elif item.service_id == "S":
                tripid["Saturday"].append(item.trip_id)
            elif item.service_id.split("-")[2] in ["Weekday", "Saturday", "Sunday"]:
                tripid[str(item.service_id.split("-")[2])].append(item.trip_id)
            elif item.service_id == "U":
                tripid["Sunday"].append(item.trip_id)

        # In list: 0 - SWT; 1 - AWT; 2 - EWT;
        result[route.split("-")[0]] = {"Weekday": [], "Saturday": [], "Sunday": []}

        # Calculate Scheduled Waiting Time for each selected stop
        stoptime = {"Weekday": [], "Saturday": [], "Sunday": []}
        for item2 in stoptimedata:
            scheduled_time = int(item2.arrival_time.split(":")[0]+item2.arrival_time.split(":")[1])
            if scheduled_time >= s_time and scheduled_time <= e_time:
                temp = int(item2.arrival_time.split(":")[0])*60 + int(item2.arrival_time.split(":")[1])
                if item2.trip_id in tripid["Weekday"]:
                    stoptime["Weekday"].append(temp)
                elif item2.trip_id in tripid["Saturday"]:
                    stoptime["Saturday"].append(temp)
                elif item2.trip_id in tripid["Sunday"]:
                    stoptime["Sunday"].append(temp)
        for token in ["Weekday", "Saturday", "Sunday"]:
            if len(stoptime[token]) > 1:
                new = sorted(stoptime[token])
                pre = new[0]
                nu = 0
                de = 0
                for item3 in new:
                    nu += float((item3 - pre)**2)/2.0
                    de += item3 - pre
                    pre = item3
                result[route.split("-")[0]][token].append(float(nu)/float(de))
            else:
                result[route.split("-")[0]][token].append(0)

        # Calculate Actual Waiting Time for each selected stop
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(routename), dir=str(direction), date__range=(s_date, e_date))
        stoptime = {"Weekday": {}, "Saturday": {}, "Sunday": {}}
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                temp = int(item.hour)*60 + int(item.minute)
                if item.dow == "1":
                    if stoptime["Weekday"].has_key(item.date):
                        stoptime["Weekday"][item.date].append(temp)
                    else:
                        stoptime["Weekday"][item.date] = []
                        stoptime["Weekday"][item.date].append(temp)
               # Temporarily no APC/AVL data for Saturday and Sunday !!
                # elif item2.dow == "2":
                #     stoptime["Saturday"].append(temp)
                # elif item2.dow == "3":
                #     stoptime["Sunday"].append(temp)
        avg = 0
        daycount = 0
        for token in stoptime["Weekday"].keys():
            if len(stoptime["Weekday"][token]) > 1:
                new = sorted(stoptime["Weekday"][token])
                pre = new[0]
                nu = 0
                de = 0
                for item3 in new:
                    nu += float((item3 - pre)**2)/2.0
                    de += item3 - pre
                    pre = item3
                if float(de) != 0:
                    avg += float(nu)/float(de)
                    daycount += 1
        if daycount > 0:
            result[route.split("-")[0]]["Weekday"].append(float(avg)/float(daycount))
        else:
            result[route.split("-")[0]]["Weekday"].append(0)

        # Temporarily no APC/AVL data for Saturday and Sunday, so use SWT ratio to estimate AWT on weekend.
        if result[route.split("-")[0]]["Weekday"][0] == 0:
            result[route.split("-")[0]]["Saturday"].append(0)
            result[route.split("-")[0]]["Sunday"].append(0)
        else:
            result[route.split("-")[0]]["Saturday"].append(result[route.split("-")[0]]["Weekday"][1] * (result[route.split("-")[0]]["Saturday"][0]/result[route.split("-")[0]]["Weekday"][0]))
            result[route.split("-")[0]]["Sunday"].append(result[route.split("-")[0]]["Weekday"][1] * (result[route.split("-")[0]]["Sunday"][0]/result[route.split("-")[0]]["Weekday"][0]))

        # Calculate Excess Waiting Time for each selected stop
        for token in ["Weekday", "Saturday", "Sunday"]:
            result[route.split("-")[0]][token].append(result[route.split("-")[0]][token][1] - result[route.split("-")[0]][token][0])

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_crowding(request):
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"]:
            route = item.route_number_in_APCAVL
            break
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stops = request.GET["stops"].split(",")
    threshold = float(request.GET["thres"])/float(100)

    # The map from "bus model" to "number of seats", "bus model" in APC/AVL has 4 digits, only first 2 represent models
    bus_map = {"30": 63, "31": 60, "50": 37, "51": 37, "52": 37, "53": 37, "54": 37, "55": 40, "56": 40,
               "19": 57, "32": 56, "33": 56, "39": 60, "57": 40, "58": 40, "59": 40}

    result = {}
    for stopid in stops:
        result[stopid] = {"absmax": 0, "avgmax": 0, "avgavg": 0, "avgmin": 0, "ocpro": 0}
        temp = {}
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(route), dir=str(direction), date__range=(s_date, e_date))
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                load = float(item.load_num)
                capacity = float(bus_map[item.vehnoa[:2]])
                pro = load/capacity
                if temp.has_key(item.date):
                    temp[item.date].append(pro)
                else:
                    temp[item.date] = [pro]
        avgavg = 0
        avgmax = 0
        avgmin = 0
        occount = 0
        absmax = 0
        totalcount = 0
        for key in temp.keys():
            avgavg += float(sum(temp[key]))/float(len(temp[key]))
            avgmax += max(temp[key])
            avgmin += min(temp[key])
            if max(temp[key]) > absmax:
                absmax = max(temp[key])
            for item in temp[key]:
                if item > threshold:
                    occount += 1
            totalcount += len(temp[key])
        numofdate = float(len(temp))
        result[stopid]["absmax"] = absmax
        if numofdate != 0:
            result[stopid]["avgmax"] = float(avgmax)/numofdate
            result[stopid]["avgavg"] = float(avgavg)/numofdate
            result[stopid]["avgmin"] = float(avgmin)/numofdate
        if totalcount != 0:
            result[stopid]["ocpro"] = float(occount)/float(totalcount)

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_bunching(request):
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"]:
            route = item.route_number_in_APCAVL
            break
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stops = request.GET["stops"].split(",")
    threshold = float(request.GET["thres"])/float(100)

    result = {}
    for stopid in stops:
        result[stopid] = {"max": 0, "avg": 0}
        temp = {}
        # the field qstopa now has 2 blank spaces in the beginning of every line, if database changed, remember to revise the filter condition!!
        data = Transit_data.objects.filter(qstopa='  '+str(stopid), route=str(route), dir=str(direction), date__range=(s_date, e_date))
        for item in data:
            if item.schtim >= s_time and item.schtim <= e_time:
                if temp.has_key(item.date):
                    temp[item.date][int(item.tripa)] = int(item.hour*3600 + item.minute*60 + item.second)
                else:
                    temp[item.date] = {int(item.tripa): int(item.hour*3600 + item.minute*60 + item.second)}
        onestop = {}
        for key in temp.keys():
            if len(temp[key]) > 1:
                oneday = temp[key]
                count = 0
                pre_init = 0
                pre_arr = 0
                b_num = 0
                for key2 in sorted(oneday.keys()):
                    if count != 0:
                        s_headway = (((key2 % 100) + (key2 // 100) * 60) - ((pre_init % 100) + (pre_init // 100) * 60)) * 60
                        a_headway = oneday[key2] - pre_arr
                        if float(a_headway)/float(s_headway) < threshold:  # Actual Headway/Scheduled Headway < Threshold
                            b_num += 1
                    count += 1
                    pre_init = key2
                    pre_arr = oneday[key2]
                if b_num != 0:
                    onestop[key] = float(b_num + 1)/float(len(temp[key]))
                else:
                    onestop[key] = 0
        bavg = 0
        bmax = 0
        for key in onestop.keys():
            if onestop[key] > bmax:
                bmax = onestop[key]
            bavg += onestop[key]
        if len(onestop) != 0:
            bavg = float(bavg)/float(len(onestop))
        else:
            bavg = -1
        result[stopid]["max"] = bmax
        result[stopid]["avg"] = bavg

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit_metrics_bustraveltime(request):
    routedict = Route_dict.objects.all()
    route = ''
    for item in routedict:
        if item.short_name == request.GET["rt"]:
            route = item.route_number_in_APCAVL
            break
    direction = request.GET["dir"]
    s_date = request.GET["s_date"]
    e_date = request.GET["e_date"]
    s_time = int(request.GET["s_time"])
    e_time = int(request.GET["e_time"])
    s_date = date(int(s_date[6:10]), int(s_date[0:2]), int(s_date[3:5]))
    e_date = date(int(e_date[6:10]), int(e_date[0:2]), int(e_date[3:5]))
    stopid1 = request.GET["stop1"]
    stopid2 = request.GET["stop2"]

    result = []
    temp = {}
    data1 = Transit_data.objects.filter(qstopa='  '+str(stopid1), route=str(route), dir=str(direction), date__range=(s_date, e_date))
    for item in data1:
        if item.schtim >= s_time and item.schtim <= e_time:
            temp[str(item.date)+item.tripa] = item.hour*60 + item.minute + float(item.second)/60

    data2 = Transit_data.objects.filter(qstopa='  '+str(stopid2), route=str(route), dir=str(direction), date__range=(s_date, e_date))
    for item in data2:
        if item.schtim >= s_time and item.schtim <= e_time:
            if temp.has_key(str(item.date)+item.tripa):
                result.append(abs(temp[str(item.date)+item.tripa] - (item.hour*60 + item.minute + float(item.second)/60)))

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')


# Temporarily no use ################################################
def transit_metrics_route_range(request):
# s_datetime:s_datetime, e_datetime:e_datetime, origin:origin,destination:destination,route:route,direction:direction
    # s_date = request.GET["s_datetime"]
    # e_date = request.GET["e_datetime"]
    # s_datetime = datetime(int(s_date[0:4]),int(s_date[4:6]),int(s_date[6:]))
    # e_datetime = datetime(int(e_date[0:4]),int(e_date[4:6]),int(e_date[6:]))
    s_datetime = datetime.strptime(request.GET["s_datetime"],"%Y-%m-%d %I:%M %p")
    e_datetime = datetime.strptime(request.GET["e_datetime"],"%Y-%m-%d %I:%M %p")
    origin = request.GET["origin"]
    destination = request.GET["destination"]
    route_name = request.GET["route"]
    direction = request.GET["direction"]

    route = Route.objects.filter(short_name = route_name)[0]
    if direction == 'I':
        stops = route.inbound_stops_geoJson
    else:
        stops = route.outbound_stops_geoJson
    stops = json.loads(stops)

    origin_order = -1
    destination_order = -1
    for stop in stops["features"]:
        if stop["properties"]["stop_id"] == origin:
            origin_order = stop["properties"]["order"]
        if stop["properties"]["stop_id"] == destination:
            destination_order = stop["properties"]["order"]
    num = destination_order - origin_order

    result = {"ontime":str(s_datetime) + " " + str(e_datetime),"crowding":num,"waiting": route_name + " " + direction}

    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')
#####################################################################


# ++++++++++++++++++++++++++++++++++++++++++++  Views of Transit Function End  +++++++++++++++++++++++++++++++++++++++++++++++



#routing
@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def routing(request):
    return render(request,'traffic/routing.html',{'n':range(1,32)})


def distance_lnglat(x,y): # in meters
    R = 6371000.0
    lon1 = math.radians(x[0])
    lon2 = math.radians(y[0])
    lat1 = math.radians(x[1])
    lat2 = math.radians(y[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (math.sin(dlat/2))**2 + math.cos(lat1) * math.cos(lat2) * (math.sin(dlon/2))**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def routing_path(request):
    s_lon = float(request.GET['s_lon'])
    s_lat = float(request.GET['s_lat'])
    d_lon = e_lon = float(request.GET['e_lon'])
    d_lat = e_lat = float(request.GET['e_lat'])
    p_date = request.GET['date']
    p_time = request.GET['time']
    find_lots = request.GET['find_lots']
    rad = request.GET['rad']
    nearest_lot ={}

    if find_lots == 'true' and rad:
        min_dist = float(rad)
        lots = Parking_lots.objects.all()
        for lot in lots:
            dist = distance_lnglat([d_lon,d_lat],[lot.lon,lot.lat])
            if dist <= min_dist:
                min_dist = dist
                e_lon = lot.lon
                e_lat = lot.lat
                nearest_lot['lon'] = lot.lon
                nearest_lot['lat'] = lot.lat
                nearest_lot['name'] = lot.name
                nearest_lot['max_spots'] = lot.max_spots
    #origin = {'id':'', 'node':'', 'lon':0.0, 'lat':0.0}
    #destination = {'id':'', 'node':'', 'lon':0.0, 'lat':0.0}

        #get traffic pattern
    weekday = date(2015,int(p_date[0:2]), int(p_date[2:4])).weekday()
    if weekday == 0:
        pattern = 1
    elif weekday == 4:
        pattern = 3
    elif weekday > 4:
        pattern = 4
    else:
        pattern = 2

    interval =  int(p_time[0:2])*60 + int(p_time[2:4]) + 1
    url = 'http://ec2-54-152-117-200.compute-1.amazonaws.com/travel_time_hierachy.php?s_lng='+ str(s_lon) + '&s_lat=' + str(s_lat) + '&e_lng=' + str(e_lon) + '&e_lat=' + str(e_lat) + '&interval=' + str(interval) + '&pattern=' + str(pattern)
    rsps = urllib2.urlopen(url)
    info = rsps.read().strip(',\r\n')
    info = info.split('\t')
    if not info[1]: #no rsps
        response = json.dumps({"success":"no","path":{},"lot":{"find_lot":0,"geoJson":{}},"travel_time":-1})
        return HttpResponse(response, content_type='application/json')
    origin, destination = info[0].split(";")
    origin = json.loads(origin)
    destination = json.loads(destination)
    time = float(info[1])
    path = info[2].split(',')
    path_coor = []
    for p in path:
       link_record = GIS_links.objects.filter(link_id = p)
       path_coor.append(json.loads(link_record[0].geometries.strip()))
    #path_coor = path_coor.rstrip(',')
    #path_coor = json.loads(path_coor)
    rsps_json = {"success":"yes","path":{},"lot":{"find_lot":0,"geoJson":{}},"travel_time":-1}
    rsps_json["travel_time"] = time
    result = {"type":"FeatureCollection","features":[]}
    path_geoJson =  {"type":"Feature","geometry":{"type":"MultiLineString","coordinates":path_coor}}
    origin_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[s_lon,s_lat],origin]},"properties":{"position":"origin"}}
    #origin_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([s_lon,s_lat],[origin['lon'],origin['lat']],'driving')},"properties":{"position":"origin","id":str(origin['id'])}}
    destination_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[e_lon,e_lat],destination]},"properties":{"position":"destination"}}
    #destination_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([e_lon,e_lat],[destination['lon'],destination['lat']],'driving')},"properties":{"position":"destination","id":str(destination['id'])}}
    result['features'] = [origin_geoJson,destination_geoJson,path_geoJson]
    #result['features'] = [path_geoJson]
    if nearest_lot:
        path_to_lot_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([e_lon, e_lat],[d_lon,d_lat],'walking')},"properties":{"position":"path to parking lot"}}
        result['features'].append(path_to_lot_geoJson)
        lot_geoJson = {"type":"Feature","geometry":{"type":"Point","coordinates":[e_lon, e_lat]},"properties":nearest_lot}
        rsps_json["lot"]["geoJson"] = lot_geoJson
        rsps_json["lot"]["find_lot"] = 1
    rsps_json["path"] = result
    response = json.dumps(rsps_json)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_travel', raise_exception= True)
def routing_path_nodes(request):
    s_lon = float(request.GET['s_lon'])
    s_lat = float(request.GET['s_lat'])
    d_lon = e_lon = float(request.GET['e_lon'])
    d_lat = e_lat = float(request.GET['e_lat'])
    p_date = request.GET['date']
    p_time = request.GET['time']
    find_lots = request.GET['find_lots']
    rad = request.GET['rad']
    nearest_lot ={}

    if find_lots == 'true' and rad:
        min_dist = float(rad)
        lots = Parking_lots.objects.all()
        for lot in lots:
            dist = distance_lnglat([d_lon,d_lat],[lot.lon,lot.lat])
            if dist <= min_dist:
                min_dist = dist
                e_lon = lot.lon
                e_lat = lot.lat
                nearest_lot['lon'] = lot.lon
                nearest_lot['lat'] = lot.lat
                nearest_lot['name'] = lot.name
                nearest_lot['max_spots'] = lot.max_spots
    origin = {'id':'', 'node':'', 'lon':0.0, 'lat':0.0}
    destination = {'id':'', 'node':'', 'lon':0.0, 'lat':0.0}
    dist_min_origin = 10000000000.0
    dist_min_destination = 10000000000.0
    links = GIS_links.objects.all()
    for link in links:
        dist = (link.s_lon - s_lon)**2 + (link.s_lat-s_lat)**2
        if dist < dist_min_origin:
            dist_min_origin = dist
            origin['id'] = link.link_id
            origin['node'] = link.from_node
            origin['lon'] = link.s_lon
            origin['lat'] = link.s_lat
        dist = (link.e_lon - s_lon)**2 + (link.e_lat-s_lat)**2
        if dist < dist_min_origin:
            dist_min_origin = dist
            origin['id'] = link.link_id
            origin['node'] = link.to_node
            origin['lon'] = link.e_lon
            origin['lat'] = link.e_lat
        dist = (link.s_lon - e_lon)**2 + (link.s_lat-e_lat)**2
        if dist < dist_min_destination:
            dist_min_destination = dist
            destination['id'] = link.link_id
            destination['node'] = link.from_node
            destination['lon'] = link.s_lon
            destination['lat'] = link.s_lat
        dist = (link.e_lon - e_lon)**2 + (link.e_lat-e_lat)**2
        if dist < dist_min_destination:
            dist_min_destination = dist
            destination['id'] = link.link_id
            destination['node'] = link.to_node
            destination['lon'] = link.e_lon
            destination['lat'] = link.e_lat

        #get traffic pattern
    weekday = date(2015,int(p_date[0:2]), int(p_date[2:4])).weekday()
    if weekday == 0:
        pattern = 1
    elif weekday == 4:
        pattern = 3
    elif weekday > 4:
        pattern = 4
    else:
        pattern = 2

    interval =  int(p_time[0:2])*60 + int(p_time[2:4]) + 1
    url = 'http://ec2-54-152-117-200.compute-1.amazonaws.com/travel_time.php?start='+ str(origin['node']) + '&end=' + str(destination['node']) + '&interval=' + str(interval) + '&pattern=' + str(pattern)
    rsps = urllib2.urlopen(url)
    info = rsps.read().strip(',\r\n')
    info = info.split('\t')
    time = float(info[0])
    path = info[1].split(',')
    path_coor = []
    for p in path:
       link_record = GIS_links.objects.filter(link_id = p)
       path_coor.append(json.loads(link_record[0].geometries.strip()))
    #path_coor = path_coor.rstrip(',')
    #path_coor = json.loads(path_coor)
    rsps_json = {"path":{},"lot":{"find_lot":0,"geoJson":{}},"travel_time":-1}
    rsps_json["travel_time"] = time
    result = {"type":"FeatureCollection","features":[]}
    path_geoJson =  {"type":"Feature","geometry":{"type":"MultiLineString","coordinates":path_coor}}
    origin_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[s_lon,s_lat],[origin['lon'],origin['lat']]]},"properties":{"position":"origin","id":str(origin['id'])}}
    #origin_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([s_lon,s_lat],[origin['lon'],origin['lat']],'driving')},"properties":{"position":"origin","id":str(origin['id'])}}
    destination_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[e_lon,e_lat],[destination['lon'],destination['lat']]]},"properties":{"position":"destination","id":str(destination['id'])}}
    #destination_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([e_lon,e_lat],[destination['lon'],destination['lat']],'driving')},"properties":{"position":"destination","id":str(destination['id'])}}
    result['features'] = [origin_geoJson,destination_geoJson,path_geoJson]
    if nearest_lot:
        path_to_lot_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":get_google_direction([e_lon, e_lat],[d_lon,d_lat],'walking')},"properties":{"position":"path to parking lot"}}
        result['features'].append(path_to_lot_geoJson)
        lot_geoJson = {"type":"Feature","geometry":{"type":"Point","coordinates":[e_lon, e_lat]},"properties":nearest_lot}
        rsps_json["lot"]["geoJson"] = lot_geoJson
        rsps_json["lot"]["find_lot"] = 1
    rsps_json["path"] = result
    response = json.dumps(rsps_json)
    return HttpResponse(response, content_type='application/json')

def get_google_direction(origin, destination, mode): #using google direction api to get path, origin, destination: [lng,lat# ], mode:walking, driving(default)
    url = 'http://maps.googleapis.com/maps/api/directions/json?origin='+ str(origin[1]) + ',' + str(origin[0]) + '&destination=' + str(destination[1]) + ',' + str(destination[0])
    if mode == 'walking' or mode == "walk":
        url += "&mode=walking"
    p = urllib2.urlopen(url)
    info = p.read()
    info = json.loads(info)
    path = []
    if info['status'] == 'OK':
        path.append([info['routes'][0]['legs'][0]['start_location']['lng'],info['routes'][0]['legs'][0]['start_location']['lat']])
        for step in info['routes'][0]['legs'][0]['steps']:
            path.append([step['end_location']['lng'],step['end_location']['lat']])
    return path


def routing_path_old(request):
    s_lon = float(request.GET['s_lon'])
    s_lat = float(request.GET['s_lat'])
    d_lon = e_lon = float(request.GET['e_lon'])
    d_lat = e_lat = float(request.GET['e_lat'])
    find_lots = request.GET['find_lots']
    rad = request.GET['rad']
    nearby_lots = {}
    if find_lots == 'true' and rad:
        rad = float(rad)
        lots = Parking_lots.objects.all()
        for lot in lots:
            dist = distance_lnglat([e_lon,e_lat],[lot.lon,lot.lat])
            if dist <= rad:
                nearby_lots[lot.lot_id] = dist
    sorted_lots = sorted(nearby_lots.items(), key=operator.itemgetter(1))
    nearest_lot = {}
    for lot in sorted_lots: #lot is a tuple (id,dist)
        url = 'http://parkpgh.org/index.php/api/getLotById?lotId=' + str(lot[0])
        p = urllib2.urlopen(url)
        info = p.read()
        info = json.loads(info)
        if 'id' in info and info['available_spots'] > 10:
            nearest_lot['id'] = info['id']
            nearest_lot['properties'] = info
            break
    if nearest_lot: # direct to nearest parking lot
        e_lon = nearest_lot['properties']['lon']
        e_lat = nearest_lot['properties']['lat']
    origin = {'id':'', 'lon':0.0, 'lat':0.0}
    destination = {'id':'', 'lon':0.0, 'lat':0.0}
    dist_min_origin = 10000000000.0
    dist_min_destination = 10000000000.0
    links = GIS_links.objects.all()
    for link in links:
        dist = (link.s_lon - s_lon)**2 + (link.s_lat-s_lat)**2
        if dist < dist_min_origin:
            dist_min_origin = dist
            origin['id'] = link.link_id
            origin['lon'] = link.s_lon
            origin['lat'] = link.s_lat
        dist = (link.e_lon - s_lon)**2 + (link.e_lat-s_lat)**2
        if dist < dist_min_origin:
            dist_min_origin = dist
            origin['id'] = link.link_id
            origin['lon'] = link.e_lon
            origin['lat'] = link.e_lat
        dist = (link.s_lon - e_lon)**2 + (link.s_lat-e_lat)**2
        if dist < dist_min_destination:
            dist_min_destination = dist
            destination['id'] = link.link_id
            destination['lon'] = link.s_lon
            destination['lat'] = link.s_lat
        dist = (link.e_lon - e_lon)**2 + (link.e_lat-e_lat)**2
        if dist < dist_min_destination:
            dist_min_destination = dist
            destination['id'] = link.link_id
            destination['lon'] = link.e_lon
            destination['lat'] = link.e_lat
    path = []
    url = 'http://maps.googleapis.com/maps/api/directions/json?origin='+ str(origin['lat']) + ',' + str(origin['lon']) + '&destination=' + str(destination['lat']) + ',' + str(destination['lon'])
    p = urllib2.urlopen(url)
    info = p.read()
    info = json.loads(info)
    result = {"type":"FeatureCollection","features":[]}
    origin_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[s_lon,s_lat],[origin['lon'],origin['lat']]]},"properties":{"position":"origin","id":str(origin['id'])}}
    destination_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[e_lon,e_lat],[destination['lon'],destination['lat']]]},"properties":{"position":"destination","id":str(destination['id'])}}
    if info['status'] != 'OK':
        result['features'] = [origin_geoJson,destination_geoJson]
    else:
        path.append([info['routes'][0]['legs'][0]['start_location']['lng'],info['routes'][0]['legs'][0]['start_location']['lat']])
        for step in info['routes'][0]['legs'][0]['steps']:
            path.append([step['end_location']['lng'],step['end_location']['lat']])
        path_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":path},"properties":{"position":"path"}}
        result['features'] = [origin_geoJson,destination_geoJson,path_geoJson]
    if nearest_lot:
        lot_geoJson = {"type":"Feature","geometry":{"type":"Point","coordinates":[nearest_lot['properties']['lon'], nearest_lot['properties']['lat']]},"properties":nearest_lot['properties']}
        path_to_lot_geoJson = {"type":"Feature","geometry":{"type":"LineString","coordinates":[[nearest_lot['properties']['lon'], nearest_lot['properties']['lat']],[d_lon,d_lat]]},"properties":{"position":"path to parking lot"}}
        result['features'].append(lot_geoJson)
        result['features'].append(path_to_lot_geoJson)
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def test(request):
    return HttpResponse("hi world")

@permission_required(perm= 'traffic.perm_incident', raise_exception= True)
def get_incidents_rcrs_area(request):
    s_date = request.GET['s_date']
    e_date = request.GET['e_date']
    s_time = request.GET['s_time']
    e_time = request.GET['e_time']
    lon1 = float(request.GET['lon1'])
    lat1 = float(request.GET['lat1'])
    lon2 = float(request.GET['lon2'])
    lat2 = float(request.GET['lat2'])
    s_lon = min(lon1,lon2)
    e_lon = max(lon1,lon2)
    s_lat = min(lat1,lat2)
    e_lat = max(lat1,lat2)
    s_hour = int(s_time[0:2])
    s_minute = int(s_time[2:4])
    e_hour = int(e_time[0:2])
    e_minute = int(e_time[2:4])
    start_date = date(int(s_date[0:4]),int(s_date[4:6]), int(s_date[6:8]))
    end_date = date(int(e_date[0:4]),int(e_date[4:6]), int(e_date[6:8]))
    start_time = time(s_hour, s_minute)
    end_time = time(e_hour, e_minute)
    incidents = Incidents.objects.filter(close_date__range=(start_date, end_date), close_time__range=(start_time, end_time))
    if lon1 != 200 and lat1 != 200 and lon2 != 200 and lat2 != 200:
        incidents = incidents.filter(Q(s_lon__range=(s_lon,e_lon),s_lat__range=(s_lat,e_lat))|Q(e_lon__range=(s_lon,e_lon),e_lat__range=(s_lat,e_lat)))
    result = ','.join(inc.geoJson for inc in incidents)
    causes={}
    for inc in incidents:
        if inc.cause not in causes:
            causes[inc.cause] = 1
        else:
            causes[inc.cause] += 1
    geoJson = '''{ "type": "FeatureCollection","features": [''' + result + ']}'
    data = []
    for key,value in causes.items():
        data.append({"label":key,"data":value})
    rsps = {"geoJson":geoJson,"data":data}
    response = json.dumps(rsps)
    return HttpResponse(response, content_type='application/json')

@permission_required(perm= 'traffic.perm_incident', raise_exception= True)
def real_time_incidents_rcrs(request):
    events = {"type":"FeatureCollection","features":[]}
    url = 'https://www.dot511.state.pa.us/RCRS_Data_Feed/RCRSDataService.asmx/GetEventFeed?keyValue=RCRSdataFeedsPA@prod&userName=SEAN_QIAN&userPass=CMU_MOBILITY_DATA_ANALYTICS'
    f = urllib2.urlopen(url)
    xml_str = f.read()
    xml_str = xml_str.replace('&lt;','<').replace('&gt;','>') #replace html to get the right xml format
    root = XMLET.fromstring(xml_str)
    if root.find('{http://bpr.dot.state.pa.us/}success').text == 'Y': #look up by tag
        for child in root:
            if 'success' in child.tag: #skip the success element in xml
                continue
            this_event = {"type":"Feature","geometry":{"type":"MultiPoint","coordinates":[]},"properties":{}}
            info = {"id":"" , "facility":"" , "type":"" , "direction":"" , "from_loc":"" , "to_loc":"" , "last_update":"" , "lane_status":"" , "description":""}
            info["id"] = child.find('{http://bpr.dot.state.pa.us/}EventID').text
            info["facility"] = child.find('{http://bpr.dot.state.pa.us/}Facility').text
            info["type"] = child.find('{http://bpr.dot.state.pa.us/}EventType').text
            info["direction"] = child.find('{http://bpr.dot.state.pa.us/}Direction').text
            info["from_loc"] = child.find('{http://bpr.dot.state.pa.us/}FromLoc').text
            info["to_loc"] = child.find('{http://bpr.dot.state.pa.us/}ToLoc').text
            info["last_update"] = child.find('{http://bpr.dot.state.pa.us/}LastUpdate').text
            info["lane_status"] = child.find('{http://bpr.dot.state.pa.us/}LaneStatus').text
            info["description"] = child.find('{http://bpr.dot.state.pa.us/}Description').text
            this_event["properties"] = info
            from_lat_lng = child.find('{http://bpr.dot.state.pa.us/}FromLocLatLog').text
            to_lat_lng = child.find('{http://bpr.dot.state.pa.us/}ToLocLatLog').text
            if from_lat_lng and to_lat_lng: #some events do not have lng lat, cannot be displayed
                from_lat_lng = from_lat_lng.split(',')
                to_lat_lng = to_lat_lng.split(',')
                this_event["geometry"]["coordinates"] = [[float(from_lat_lng[1]),float(from_lat_lng[0])] , [float(to_lat_lng[1]), float(to_lat_lng[0])]]
                events['features'].append(this_event)
    response = json.dumps(events)
    return HttpResponse(response, content_type='application/json')


def real_time_tmc(request):
    token_url = "http://api.inrix.com/Traffic/Inrix.ashx?action=getsecuritytoken&Vendorid=1346213929&consumerid=30c227fe-93ab-4f30-9408-362645f33730"
    token_link = urllib2.urlopen(token_url)
    token_rsps = token_link.read()
    token_root = XMLET.fromstring(token_rsps)
    token = token_root.find("AuthResponse").find("AuthToken").text
    api_path = "http://na.api.inrix.com/Traffic/Inrix.ashx"
    url = api_path + "?Action=GetRoadSpeedInTMCs&Token=" + token + "&Tmcs="
    tmc_set = TMC_real_time.objects.all()
    i=1
    n=len(tmc_set)
    result_data = {"type":"FeatureCollection","features":[]}
    while i*180 < n or (i-1)*180 <n: #max length of a url request is 2000 characters, can take about 180 tmcs in a request
        end = min(i*180,n)
        tmc_list = ",".join(record.tmc for record in tmc_set[(i-1)*180:end])
        link = urllib2.urlopen(url+tmc_list)
        url_rsps = link.read()
        root = XMLET.fromstring(url_rsps)
        for record in root.iter("TMC"):
            this_tmc = tmc_set.filter(tmc = record.attrib["code"])[0]
            # efficiency is not so good
            # this_tmc.speed = float(record.attrib["speed"])
            # this_tmc.reference = float(record.attrib["reference"])
            # this_tmc.average = float(record.attrib["average"])
            # this_tmc.ttm = float(record.attrib["travelTimeMinutes"])
            # this_tmc.congestion = float(record.attrib["congestionLevel"])
            # this_tmc.save()
            this_data = {"type":"Feature","geometry":{"type":"MultiPoint","coordinates":[[this_tmc.s_lon,this_tmc.s_lat],[this_tmc.e_lon,this_tmc.e_lat]]},"properties":{"tmc":this_tmc.tmc,"road":this_tmc.road,"direction":this_tmc.direction,"miles":this_tmc.miles,"order":this_tmc.road_order,"speed":float(record.attrib["speed"]),"reference":float(record.attrib["reference"]),"tt":float(record.attrib["travelTimeMinutes"]),"sp_ref_ratio":float(record.attrib["speed"])/float(record.attrib["reference"])}}
            result_data["features"].append(this_data)
        i+=1
    response = json.dumps(result_data)
    return HttpResponse(response,content_type="application/json")


def TMC_GIS(request):
    # data = {"gis":{},"tmc":{}}

    GIS = {"type":"FeatureCollection","features":[]}
    links = GIS_links.objects.all()
    features = [0]*len(links)
    for i,link in enumerate(links):
        features[i] = {"type":"Feature","geometry":{"type":"LineString","coordinates":json.loads(link.geometries.strip())},"properties":{"lid":link.link_id}}
    GIS["features"] = features
    #data["gis"] = GIS

    # TMC = {"type":"FeatureCollection","features":[]}
    # tmcs = TMC_real_time.objects.all()
    # features = [0]*len(tmcs)
    # for i,tmc in enumerate(tmcs):
    #     features[i] = {"type":"Feature","geometry":{"type":"MultiPoint","coordinates":[[tmc.s_lon,tmc.s_lat],[tmc.e_lon,tmc.e_lat]]},"properties":{"id":tmc.tmc}}
    # TMC["features"] = features
    # data["tmc"] = TMC

    response = json.dumps(GIS)
    return HttpResponse(response,content_type="application/json")

def real_time_tt(request):
    return render(request, 'traffic/real_time_tt.html')


def device_render(request):
    return render(request, 'traffic/devices.html')

@permission_required(perm= 'traffic.perm_count', raise_exception= True)
def sensors_counts_webpage(request):
    return render(request, 'traffic/sensors_counts.html')

@permission_required(perm= 'traffic.perm_count', raise_exception= True)
def get_sensors_counts(request):
    sensors_data = {"type":"FeatureCollection","features":[]}
    sensors = Counts_sensors.objects.all()
    features = [0]*len(sensors)
    for i, sensor in enumerate(sensors):
        features[i] = {"type":"Feature","geometry":{"type":"Point","coordinates":json.loads(sensor.coordinates.strip())},"properties":{"sid":sensor.sid,"data":[] if sensor.counts == "" else [float(num_str) for num_str in sensor.counts.split(",")]}} #some of the sensors do not have counts data
    sensors_data["features"] = features
    response = json.dumps(sensors_data)
    return HttpResponse(response,content_type = "application/json")

@permission_required(perm= 'traffic.perm_count', raise_exception= True)
def get_sensors_links(request):
    sensors_links = {"type":"FeatureCollection","features":[]}
    links = Counts_sensors_links.objects.all()
    features = [0]*len(links)
    for i, link in enumerate(links):
        features[i] = {"type":"Feature","geometry":{"type":"LineString","coordinates":json.loads(link.coordinates.strip())},"properties":{"sid":link.sid}}
    sensors_links["features"] = features
    response = json.dumps(sensors_links)
    return HttpResponse(response,content_type = "application/json")

#SGYang
def closure(request):
    return render(request, 'traffic/closure.html')


def get_road_closure_query(request):
    #eee = Closed_roads.objects.filter(location__icontains='FORBES AVE')
    #print eee.rdline
    if request.GET['first'] == '1':
        entry = Closed_roads.objects.exclude(type__in=[0])
    else:
        weekday = request.GET['weekday']
        hour = int(request.GET['hour'])
        datin = date(int(request.GET['yy']), int(request.GET['mm']), int(request.GET['dd']))
        entry = Closed_roads.objects.filter(start_date__lte=datin, end_date__gte=datin).exclude(type__in=[0])
        print len(entry)
        throw = []
        for t in entry:
            timeslot = []
            within = False
            if weekday == '0':
                timeslot = t.wkend_hrs.split('-')
            else:
                timeslot = t.wkday_hrs.split('-')
            for i in range(len(timeslot)/2):
                if (float(timeslot[2*i]) <= hour and float(timeslot[2*i+1]) >= hour):
                    within = True
            if not within:
                throw.append(t.perm_no)
            entry = Closed_roads.objects.filter(start_date__lte=datin, end_date__gte=datin).exclude(perm_no__in=throw).exclude(type__in=[0])

    datarender = '{ "points" : '+ serializers.serialize('json', entry) + '}'
    datarender = datarender.replace('\n', '')
    print len(entry)
    return HttpResponse(datarender, content_type='application/json')

def map_displayer(request):
    return render(request, 'traffic/map_displayer.html')
