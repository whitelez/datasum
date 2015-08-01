__author__ = 'bread'

from django.http import HttpResponse, QueryDict
from django.db.models import Q
from django.shortcuts import render

import json

from traffic.models import * #Meter, Parking, Street, Streetparking, TMC, TMC_data, Incidents, Weather


def crash(request):
    return render(request, 'traffic/crash.html', {'n': range(1, 32)})


def crash_query(request):
    sever = int(request.GET['sev'])
    weather = int(request.GET['wea'])
    roadcon = int(request.GET['rod'])
    entry_num = 1
    cr = []
    for i in range(3):
        cr.append(0)
    if sever == 0:
        cr[0] = Q(Severe=0)
    elif sever == 1:
        cr[0] = Q(Severe=1)
    else:
        entry_num *= 2
        cr[0] = Q(Severe__gte=0)

    if weather == 0:
        cr[1] = Q(Weather=0)
    elif weather == 1:
        cr[1] = Q(Weather=1)
    else:
        entry_num *= 2
        cr[1] = Q(Weather__gte=0)

    if roadcon == 0:
        cr[2] = Q(Roadcon=0)
    elif roadcon == 1:
        cr[2] = Q(Roadcon=1)
    else:
        entry_num *= 2
        cr[2] = Q(Roadcon__gte=0)
    result = '''{"type":"FeatureCollection","features":['''
    p = Crashdata.objects.filter(cr[0] & cr[1] & cr[2])
    road = iter(PAroad.objects.all())
    if p:
        dc = [0]*6
        cnt = 1
        for entry in p:
            if cnt == entry_num:
                t = road.next()
                print t.pid
                result += '''{"type":"Feature","properties":{"Sid":"''' + str(t.pid) + '''","ST":"''' + t.street_name + '''","LN":"''' + t.length +'''","CR":[''' + ",".join(str(ic) for ic in dc) + ''']},"geometry":{"type":"LineString","coordinates":''' + t.coordinate + "}},"
                cnt = 1
                dc = [0]*6
            else:
                cnt += 1
                dc[0] += int(entry.Y2010)
                dc[1] += int(entry.Y2011)
                dc[2] += int(entry.Y2012)
                dc[3] += int(entry.Y2013)
                dc[4] += int(entry.Y2014)
                dc[5] += float(entry.Ypre)
    result = result.rstrip(',')
    result += "]}"
    response = json.dumps(result)
    return HttpResponse(response, content_type='application/json')

#
#
# def crash_query(request):
#     sever = int(request.GET['sev'])
#     weather = int(request.GET['wea'])
#     roadcon = int(request.GET['rod'])
#     cr = []
#     for i in range(3):
#         cr.append(0)
#     if sever == 0:
#         cr[0] = Q(Severe=0)
#     elif sever == 1:
#         cr[0] = Q(Severe=1)
#     else:
#         cr[0] = Q(Severe__gte=0)
#
#     if weather == 0:
#         cr[1] = Q(Weather=0)
#     elif weather == 1:
#         cr[1] = Q(Weather=1)
#     else:
#         cr[1] = Q(Weather__gte=0)
#
#     if roadcon == 0:
#         cr[2] = Q(Roadcon=0)
#     elif roadcon == 1:
#         cr[2] = Q(Roadcon=1)
#     else:
#         cr[2] = Q(Roadcon__gte=0)
#
#
#     result = '''{"type":"FeatureCollection","features":['''
#     for t in PAroad.objects.all():
#         p = t.crashdata_set.filter(cr[0] & cr[1] & cr[2])
#         if p:
#             dc = [0]*6
#             for entry in p:
#                 dc[0] += int(entry.Y2010)
#                 dc[1] += int(entry.Y2011)
#                 dc[2] += int(entry.Y2012)
#                 dc[3] += int(entry.Y2013)
#                 dc[4] += int(entry.Y2014)
#                 dc[5] += float(entry.Ypre)
#             result += '''{"type":"Feature","properties":{"Sid":"''' + t.pid + '''","ST":"''' + t.street_name + '''","CR":[''' + ",".join(str(ic) for ic in dc) + ''']},"geometry":{"type":"LineString","coordinates":''' + t.coordinate + "}},"
#     result = result.rstrip(',')
#     result += "]}"
#     response = json.dumps(result)
#     return HttpResponse(response, content_type='application/json')
# # # A few things to do: (1) Add road length; (2) Add two way slider; (3)read everything from a file