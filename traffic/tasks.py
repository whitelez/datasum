from __future__ import absolute_import

from celery import shared_task


import json
import urllib2

from traffic.models import Real_time_tmc_data,TMC_real_time
from datetime import datetime
import xml.etree.ElementTree as XMLET



@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def get_travel_time_tmc():
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
    while i*180 < n or (i-1)*180 <n: #max length of a url request is 2000 characters, can take about 180 tmcs in a request
        end = min(i*180,n)
        tmc_list = ",".join(record.tmc for record in tmc_set[(i-1)*180:end])
        link = urllib2.urlopen(url+tmc_list)
        url_rsps = link.read()
        root = XMLET.fromstring(url_rsps)
        time_str = root.iter("RoadSpeedResults").next().attrib["timestamp"]
        d_t = datetime.strptime(time_str,"%Y-%m-%dT%H:%M:%SZ")
        current_date = d_t.date()
        current_time = d_t.time()
        for record in root.iter("TMC"):
            data = Real_time_tmc_data()
            # efficiency is not so good
            data.tmc = record.attrib["code"]
            data.date = current_date
            data.time = current_time
            data.speed = float(record.attrib["speed"]) if record.attrib["speed"] != "" else -1.0
            data.avg_speed = float(record.attrib["average"]) if record.attrib["average"] != "" else -1.0
            data.ref_speed = float(record.attrib["reference"]) if record.attrib["reference"] != "" else -1.0
            data.delta = int(record.attrib["delta"]) if record.attrib["delta"] != "" else -100
            data.score = int(record.attrib["score"]) if record.attrib["score"] != "" else -1
            data.c_value = int(record.attrib["c-value"]) if record.attrib["c-value"] != "" else -1
            data.travel_time = float(record.attrib["travelTimeMinutes"]) if record.attrib["travelTimeMinutes"] != "" else -1.0
            data.cong_level = int(record.attrib["congestionLevel"])  if record.attrib["congestionLevel"] != "" else -1
            data.save()
        i += 1