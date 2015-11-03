__author__ = 'bread'

from django.http import HttpResponse, QueryDict
from django.db.models import Q
from django.shortcuts import render
from cStringIO import StringIO
import json

from traffic.models import * #Meter, Parking, Street, Streetparking, TMC, TMC_data, Incidents, Weather

from django.contrib.auth.decorators import login_required, permission_required

@permission_required(perm= 'traffic.perm_crash', raise_exception= True)
def crash(request):
    counties = [{"code": county.county_code, "name": county.county_name} for county in PAcounty.objects.all()]
    return render(request, 'traffic/crash.html', {'counties': counties})


@permission_required(perm= 'traffic.perm_crash', raise_exception= True)
def crash_query(request):
    cntystr = str(request.GET['cnty'])
    sever = int(request.GET['sev'])
    weather = int(request.GET['wea'])
    roadcon = int(request.GET['rod'])
    entry_num = 1
    print cntystr
    cr = []
    for i in range(4):
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

    if cntystr == "-1":    # first query, only display part of the roads to avoid frontend crashes
        cr[3] = Q(First=1)

    else:       # select roads by counties
       cnty = map(int, cntystr.split("*"))
       cr[3] = Q(Cnty__in=cnty)
    print cr
    outp = []
    outp.append('''{"type":"Feature","properties":{"Sid":"''')
    outp.append('')
    outp.append('''","ST":"''')
    outp.append('')
    outp.append('''","LN":"''')
    outp.append('')
    outp.append('''","CR":[''')
    outp.append('')
    outp.append(''']},"geometry":{"type":"LineString","coordinates":''')
    outp.append('')
    outp.append("}}")
    resultio = StringIO()
    resultio.write('''{"type":"FeatureCollection","features":[''')

    p = Crashdata.objects.filter(cr[0] & cr[1] & cr[2] & cr[3])
    road = iter(PAroad.objects.filter(cr[3]))
    if p:
        dc = [0]*6
        cnt = 1
        for entry in p:
            if cnt == entry_num:
                t = road.next()
                outp[1] = str(t.pid)
                outp[3] = t.street_name
                outp[5] = t.length
                outp[7] = ",".join(str(ic) for ic in dc)
                outp[9] = t.coordinate
                resultio.write(("".join(i for i in outp)))
                resultio.write(",")
                cnt = 1
                dc = [0]*6
            else:
                cnt += 1
                dc[0] += entry.Y2010
                dc[1] += entry.Y2011
                dc[2] += entry.Y2012
                dc[3] += entry.Y2013
                dc[4] += entry.Y2014
                dc[5] += entry.Ypre
    result = resultio.getvalue()
    result = result[:-1]
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