from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

import json
import urllib2,urllib
import math,operator

from traffic.models import * #Meter, Parking, Street, Streetparking, TMC, TMC_data, Incidents, Weather
from datetime import date, time, datetime
import time as the_time
import xml.etree.ElementTree as XMLET

import csv

def index(request):
    return render(request, 'traffic/index.html')

def parking(request):
    return render(request, 'traffic/parking.html',{'n':range(1,32)})

def camera(request):
    return render(request, 'traffic/camera.html')

def count(request):
    return render(request, 'traffic/count.html')

def ajaxtest(request):
    message = request.GET['time']
    result = {'message':message}
    j = json.dumps(result)
    return HttpResponse(j, content_type='application/json')


def street_parking_geojson(request):
    intervals = 144
    #single_day = request.GET['single']
    weekday = int(request.GET['wd'])
    sy = 2014
    sm = request.GET['sm']
    sd = request.GET['sd']
    start = date(sy, int(sm), int(sd))
    ey = 2014
    em = request.GET['em']
    ed = request.GET['ed']
    end = date(ey, int(em), int(ed))
    result = '''{"type":"FeatureCollection","features":['''
    for t in Street.objects.all():
        if weekday == -1:
            p = t.streetparking_set.filter(date__range=(start, end))
        else:
            p = t.streetparking_set.filter(date__range=(start, end), date__week_day=weekday)
        if p:
            n = p.count()
            c = [0]*intervals
            for day in p:
                dc = day.occupancy.split(',')
                for i in range(intervals):
                    c[i]+=float(dc[i])/n
            result += '''{"type":"Feature","properties":{"streetID":"''' + t.sid + '''","street":"''' + t.street_name + '''","occupancy":[''' + ",".join(str(ic) for ic in c) + ''']},"geometry":{"type":"LineString","coordinates":''' + t.coordinate + "}},"
    result = result.rstrip(',')
    result += "]}"
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def street_parking_geojson_prediction(request):
    intervals = 144
    py = 2014
    pm = request.GET['pm']
    pd = request.GET['pd']
    pdate = date(py, int(pm), int(pd))
    weekday = (pdate.weekday()+1)%7+1
    result = '''{"type":"FeatureCollection","features":['''
    for t in Street.objects.all():
        p = t.streetparking_set.filter(date__week_day=weekday)
        if p:
            n = p.count()
            c = [0]*intervals
            for day in p:
                dc = day.occupancy.split(',')
                for i in range(intervals):
                    c[i]+=float(dc[i])/n
            result += '''{"type":"Feature","properties":{"streetID":"''' + t.sid + '''","street":"''' + t.street_name + '''","occupancy":[''' + ",".join(str(ic) for ic in c) + ''']},"geometry":{"type":"LineString","coordinates":''' + t.coordinate + "}},"
    result = result.rstrip(',')
    result += "]}"
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')


def weather(request):
    return render(request, 'traffic/weather.html')

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

def get_weather(request):
    #geo_list = []
    i=0
    now = datetime.now().time()
    for county in Weather.objects.all():
        if now.hour != county.update_time.hour:
            url = 'http://api.wunderground.com/api/fa32a501f6cdbc7c/hourly/q/' + county.state + '/' + urllib.quote(county.api) + '.json'
            f = urllib2.urlopen(url)
            i=i+1
            if i%5==0:
                the_time.sleep(60)
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

def ev_stations(request):
    return render(request, 'traffic/ev_stations.html')

def travel_time(request):
    tmcs = TMC.objects.all()
    return render(request, 'traffic/travel_time.html',{'n':range(1,32),'tmcs':tmcs})

#BY PXD
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
    # nodes = SPCCorridorNodeInfo.objects.filter(Corridor_Number=13)
    return render(request, 'traffic/travel_time_new.html', {'n': range(1, 32), 'tmcs': tmcs, 'corridors': corridors})

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
    flag_delay = True
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
                flag_delay = False
        else:
            if result[i].PM_Travel_Time != None:
                spctraveltime += result[i].PM_Travel_Time
            else:
                flag_traveltime = False
            if result[i].PM_Delay_Per_Vehicle != None:
                spcdelay += result[i].PM_Delay_Per_Vehicle
            else:
                flag_delay = False

    response = '''{"spctraveltime":"'''
    if flag_traveltime:
        response += str(spctraveltime)[0:4] + ''' minutes", "spcdelay":"'''
    else:
        response += '''N/A", "spcdelay":"'''
    if flag_delay:
        response += str(spcdelay)[0:4] + ''' minutes"'''
    else:
        response += '''N/A"'''
    response += '}'
    response2 = json.dumps(response)
    return HttpResponse(response2, content_type='application/json')
#END


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
    tmc_geometry = ','.join('''{"type":"Feature","properties": {"TMC":"''' + tmc.tmc + '''","road":"''' + tmc.road +'''","direction":"''' + tmc.direction + '''","intersection":"''' + tmc.intersection + '''","miles":''' + str(tmc.miles) + ''',"road_order":''' + str(tmc.road_order) + '''},"geometry": {"type": "MultiPoint", "coordinates": [[''' + str(tmc.s_lon) + ',' + str(tmc.s_lat) + '],[' + str(tmc.e_lon) + ',' + str(tmc.e_lat) +']]}}' for tmc in tmc_set)
    tmc_geometry = '''{ "type": "FeatureCollection","features": [''' + tmc_geometry + ']}'
    tmc_number = tmc_set.count()
    total = 0
    miles = 0
    for tmc in tmc_set:
        avg = 0
        miles += tmc.miles
        #data = tmc.tmc_data_set.filter(date__range=(start_date,end_date), time__range=(start_time, end_time))
        data = TMC_data.objects.filter(tmc_id=tmc.tmc, date__range=(start_date,end_date), time__range=(start_time, end_time))
        n = data.count()
        for record in data:
            avg += record.travel_time
        avg = avg/n
        total += avg
    speed = miles/total*60
    truck_total = total*(1+max(speed-40,0)/50)
    truck_speed = miles/truck_total*60
    result = '{"travel_time":' + str(total) + ',"speed":' + str(speed) +',"truck_travel_time":' + str(truck_total) + ',"truck_speed":' + str(truck_speed) +',"tmc_geometry":'+ tmc_geometry +'}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

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

def get_road_tmc(request):
    input_tmc = request.GET['tmc']
    s_tmc = TMC.objects.get(tmc = input_tmc)
    tmc_set = TMC.objects.filter(road = s_tmc.road, direction = s_tmc.direction)
    result = '''{ "type": "FeatureCollection","features": ['''
    for tmc in tmc_set:
        result += '''{"type":"Feature","properties": {"TMC":"''' + tmc.tmc + '''","road":"''' + tmc.road +'''","direction":"''' + tmc.direction + '''","intersection":"''' + tmc.intersection + '''","miles":''' + str(tmc.miles) + ''',"road_order":''' + str(tmc.road_order) + '''},"geometry": {"type": "MultiPoint", "coordinates": [[''' + str(tmc.s_lon) + ',' + str(tmc.s_lat) + '],[' + str(tmc.e_lon) + ',' + str(tmc.e_lat) +']]}},'
    result = result.rstrip(',')
    result += ']}'
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

def incidents(request):
    return render(request, 'traffic/incidents.html',{'n':range(1,32)})

def download(request):
    return render(request, 'traffic/download.html',{'months':range(1,13), 'months14': range(1,9) ,'days':range(1,32)})

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
    route = Route.objects.filter(short_name = route_name)[0]
    if direction == 'I':
        result = route.inbound_geoJson
    else:
        result = route.outbound_geoJson
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def get_stops(request):
    route_name = request.GET['route']
    direction = request.GET['direction']
    route = Route.objects.filter(short_name = route_name)[0]
    if direction == 'I':
        result = route.inbound_stops_geoJson
    else:
        result = route.outbound_stops_geoJson
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

def transit(request):
    routes = ','.join(route.short_name for route in Route.objects.all())
    routes = routes.split(',')
    return render(request, 'traffic/transit.html',{'routes':routes})

def transit_metrics(request):
    #jackson
    #test out filtering
    #need two spaces before the stop ID, We should strip them out
    all_trips_my_stop = Transit_data.objects.filter(qstopa='  E29105')
    #####pull out some data from object

    #access first record, aname field is 10th element, giving error that list index is out of range
    first_record = all_trips_my_stop.get(pk=1).values()
    #print all key names
    #for x in first_record.keys()
     #   print(x)
    #set stopname to fielf from queryset object
    stop_name = first_record['aname']


    #stop_name =  all_trips_my_stop[0][9]
    #stop_name = "test"

    #how many times did the bus stop at my stop
    trip_count = all_trips_my_stop.count()

    return HttpResponse("The bus stopped at my stop " + str(trip_count) + " times. The stop name is " + stop_name + ".")

def routing(request):
    return render(request,'traffic/routing.html')


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

def routing_path(request):
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

def parking_lots(request):
    lots = {"type":"FeatureCollection","features":[]}
    for i in range(2,43):
        url = 'http://parkpgh.org/index.php/api/getLotById?lotId=' + str(i)
        p = urllib2.urlopen(url)
        info = p.read()
        info = json.loads(info)
        this_lot = {"type":"Feature","geometry":{"type":"Point","coordinates":[]},"properties":{}}
        if 'id' in info:
            this_lot['geometry']['coordinates'] = [info['lon'] , info['lat']]
            this_lot['properties'] = info
            lots['features'].append(this_lot)
    response = json.dumps(lots)
    return HttpResponse(response, content_type='application/json')

def test(request):
    s_date = request.GET['s_date']
    e_date = request.GET['e_date']
    start_date = date(int(s_date[0:4]),int(s_date[4:6]), int(s_date[6:8]))
    end_date = date(int(e_date[0:4]),int(e_date[4:6]), int(e_date[6:8]))
    incidents = Incidents.objects.filter(close_date__range=(start_date, end_date))
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="incidents' + s_date + '-' + e_date + '.csv"'
    writer = csv.writer(response)
    writer.writerow(['event_id','st_rt_no','sr','cause','status','close_date','close_time','open_date','open_time','begin_lat','begin_lon','end_lat','end_lon'])
    for incident in incidents:
        writer.writerow([incident.eventid,incident.st_rt_no,incident.sr,incident.cause,incident.status,incident.close_date,incident.close_time,incident.open_date,incident.open_time,incident.s_lat,incident.s_lon,incident.e_lat,incident.e_lon])
    return response

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
    result = '''{ "type": "FeatureCollection","features": [''' + result + ']}'
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

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
# Create your views here.
