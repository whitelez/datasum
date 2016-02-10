# get real time travel time of tomtom

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2, xml.etree.ElementTree as ET, MySQLdb
from datetime import datetime

# database connection
db = MySQLdb.connect("localhost","root","dataproject","Travel_Time_Data" ) # (port, user, password, database)
cursor = db.cursor()

while True:
    # read TomTom real time travel time data in XML format
    try:
        url = "http://traffic.tomtom.com/tsq/hdf/USA-HDF-TMC/2f398080-3324-45aa-b102-e2a13f999d04/content.xml?flowType=nff"
        req = urllib2.urlopen(url)
        CHUNK = 16 * 1024
        with open("non_freeflow.xml", "w") as fp:
            while True:
                chunk = req.read(CHUNK)
                if not chunk:
                    break
                fp.write(chunk)
    except Exception, e:
        print e
        continue

    # find data in response XML
    # parsing xml with namespace: https://docs.python.org/2/library/xml.etree.elementtree.html#parsing-xml-with-namespaces
    ns = {'standard':'http://datex2.eu/schema/1_0/1_0'}

    tree = ET.parse("non_freeflow.xml")
    root = tree.getroot()
    payload = root.find("standard:payloadPublication", ns)

    timestamp = payload.find("standard:publicationTime", ns).text
    timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S") # convert timestamp in UTC format to format of MySQL database

    for data in payload.findall("standard:elaboratedData", ns):
        # tmc
        tmc = data.attrib["id"]

        dataValue = data.find("standard:basicDataValue",ns)
        # data quality
        quality = float(dataValue.find("standard:supplierCalculatedDataQuality",ns).text)
        # travel time
        tt = float(dataValue.find("standard:travelTime",ns).text) # in seconds
        speed = float(dataValue.find("standard:travelTimeValueExtension",ns).find("standard:averageSpeed",ns).text) # in km/h
        values = [tmc, timestamp, tt, speed, quality]
        try:
            cursor.execute("INSERT INTO tomtom_travel_time VALUES (%s,%s,%s,%s,%s)", values)
            db.commit()
        except:
            db.rollback()


# will not reach here if operating correctly
db.close()
