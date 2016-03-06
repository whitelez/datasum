from django.db import models

class Meter(models.Model):
    mid = models.CharField(max_length = 20, primary_key = True)
    street_name = models.CharField(max_length = 20)
    block = models.CharField(max_length = 5)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
	    return self.mid

class Parking(models.Model):
    meter = models.ForeignKey(Meter)
    date = models.DateField(db_index = True)
    weekday = models.CharField(max_length = 3)
    occupancy = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()
# Create your models here.



####################################################################################### Crash
# class PAroad(models.Model):
#     pid = models.IntegerField(primary_key = True)
#     street_name = models.CharField(max_length = 100)
#     length = models.CharField(max_length = 10)
#     coordinate = models.TextField()
#     def __unicode__(self):
#         return self.pid
#     class Meta:
#         ordering = ['pid']
#
# class PAcounty(models.Model):
#     county_code = models.IntegerField(primary_key = True)
#     county_name = models.CharField(max_length = 100)
#     def __unicode__(self):
#         return self.county_code
#
#
# class Crashdata(models.Model):
#     pid = models.ForeignKey(PAroad)
#     Severe = models.SmallIntegerField()
#     Weather = models.SmallIntegerField()
#     Roadcon = models.SmallIntegerField()
#     ##########################
#     Y2010 = models.SmallIntegerField()
#     Y2011 = models.SmallIntegerField()
#     Y2012 = models.SmallIntegerField()
#     Y2013 = models.SmallIntegerField()
#     Y2014 = models.SmallIntegerField()
#     Ypre = models.FloatField()
#     Ystd = models.FloatField()
#
#     def __unicode__(self):
#         return self.pid
#
#     class Meta:
#         index_together = [["Severe", "Weather", "Roadcon"], ]
#         ordering = ['pid_id']


class PAroad(models.Model):
    pid = models.IntegerField(primary_key = True)
    street_name = models.CharField(max_length = 100)
    Cnty = models.SmallIntegerField(db_index = True)
    First = models.SmallIntegerField(db_index = True)
    length = models.CharField(max_length = 10)
    coordinate = models.TextField()
    def __unicode__(self):
        return self.pid
    class Meta:
        ordering = ['pid']

class PAcounty(models.Model):
    county_code = models.IntegerField(primary_key = True)
    county_name = models.CharField(max_length = 100)
    def __unicode__(self):
        return self.county_code


class Crashdata(models.Model):
    pid = models.ForeignKey(PAroad)
    Cnty = models.SmallIntegerField()
    First = models.SmallIntegerField(db_index = True)
    Severe = models.SmallIntegerField()
    Weather = models.SmallIntegerField()
    Roadcon = models.SmallIntegerField()
    ##########################
    Y2010 = models.SmallIntegerField()
    Y2011 = models.SmallIntegerField()
    Y2012 = models.SmallIntegerField()
    Y2013 = models.SmallIntegerField()
    Y2014 = models.SmallIntegerField()
    Ypre = models.FloatField()
    Ystd = models.FloatField()

    def __unicode__(self):
        return self.pid

    class Meta:
        index_together = [["Severe", "Weather", "Roadcon", "Cnty"], ]
        ordering = ['pid_id']
####################################################################################### End of Crash



#######################################################################################  Parking
class Street(models.Model): #Street coordinates with street name
    sid = models.CharField(max_length = 20, primary_key = True)
    street_name = models.CharField(max_length = 100)
    coordinate = models.TextField()
    def __unicode__(self):
        return self.sid

class Streetpre(models.Model):  # parking occupancy prediction data
    street = models.ForeignKey(Street)
    date = models.DateField(db_index = True)
    occupancy = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()

class Streetparking(models.Model):  # parking occupancy historical data
    street = models.ForeignKey(Street)
    date = models.DateField(db_index = True)
    occupancy = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()

class Streetrate(models.Model):   # parking rate historical data
    street = models.ForeignKey(Street)
    date = models.DateField(db_index = True)
    rate = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()

class Streetratepre(models.Model):  # parking rate prediction data
    street = models.ForeignKey(Street)
    date = models.DateField(db_index = True)
    rate = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()
#######################################################################################  End of Parking



# ~~~~~~~~~~~~~~~ Start Yiming ~~~~~~~~~~~~~~
class TwitterEvents(models.Model):
    eventid = models.CharField(max_length = 15, primary_key = True)
    st_rt_no = models.PositiveSmallIntegerField()
    sr = models.CharField(max_length = 255)
    cause = models.CharField(max_length = 25)
    status = models.CharField(max_length = 20)
    close_date = models.DateField()
    close_time = models.TimeField()
    open_date = models.DateField()
    open_time = models.TimeField()
    s_lat = models.FloatField()
    s_lon = models.FloatField()
    e_lat = models.FloatField()
    e_lon = models.FloatField()
    geoJson = models.TextField()
    def __unicode__(self):
        return self.eventid

# ~~~~~~~~~~~~~~~~ End Yiming~~~~~~~~~~~~~~



#BY PXD
class SPCCorridorNodeInfo(models.Model):
    Corridor_Number = models.PositiveSmallIntegerField()
    Corridor_Name = models.CharField(max_length=50)
    Node_Number = models.CharField(max_length=5)
    Node_Name = models.CharField(max_length=50)
    Latitude = models.FloatField()
    Longitude = models.FloatField()

    def __unicode__(self):
        return 'Corridor' + str(self.Corridor_Number) + '-' + self.Corridor_Name

class SPCCorridorNodeInfo2013to2015(models.Model):
    Corridor_Number = models.PositiveSmallIntegerField()
    Corridor_Name = models.CharField(max_length=50)
    Node_Number = models.CharField(max_length=5)
    Node_Name = models.CharField(max_length=50)
    Latitude = models.FloatField()
    Longitude = models.FloatField()

    def __unicode__(self):
        return 'Corridor' + str(self.Corridor_Number) + '-' + self.Corridor_Name

class SPCtraveltime(models.Model):
    Year = models.PositiveSmallIntegerField()
    Corridor_Number = models.PositiveSmallIntegerField()
    Start_Node = models.CharField(max_length=50)
    End_Node = models.CharField(max_length=50)
    AM_Peak_Hour_Volume = models.PositiveSmallIntegerField()
    PM_Peak_Hour_Volume = models.PositiveSmallIntegerField()
    Speed_Limit = models.PositiveSmallIntegerField()
    Distance = models.FloatField()
    Travel_Time_At_Posted_Speed_Limit = models.FloatField()
    Weighted_Avg_Speed = models.FloatField()
    AM_Travel_Time = models.FloatField()
    PM_Travel_Time = models.FloatField()
    AM_Avg_Speed = models.FloatField()
    AM_Weighted_Speed = models.FloatField()
    AM_Delay_Per_Vehicle = models.FloatField()
    PM_Avg_Speed = models.FloatField()
    PM_Weighted_Speed = models.FloatField()
    PM_Delay_Per_Vehicle = models.FloatField()
    AM_Total_Delay = models.FloatField()
    PM_Total_Delay = models.FloatField()
    Direction = models.CharField(max_length=5)  # Direction = 'A'(means direction from node A to node Z) or 'Z'

class SPCtraveltime2013to2015(models.Model):
    Year = models.PositiveSmallIntegerField()
    Corridor_Number = models.PositiveSmallIntegerField()
    Start_Node = models.CharField(max_length=50)
    End_Node = models.CharField(max_length=50)
    Time = models.FloatField()
    Travel_Time = models.FloatField()
    Speed = models.FloatField()
    Travel_Time_At_Posted_Speed_Limit = models.FloatField()
    Posted_Speed_Limit = models.PositiveSmallIntegerField()
#END


class TMC(models.Model):
    tmc = models.CharField(max_length = 9, primary_key = True)
    road = models.CharField(max_length = 50, db_index = True)
    DIRECTION_CHOICES = (('N', 'Northbound'),('S', 'Southbound'),('E', 'Eastbound'),('W', 'Westbound'))
    direction = models.CharField(max_length=1, choices = DIRECTION_CHOICES)
    intersection = models.CharField(max_length = 100)
    state = models.CharField(max_length = 2)
    county = models.CharField(max_length = 20)
    zip = models.CharField(max_length = 5)
    s_lat = models.FloatField()
    s_lon = models.FloatField()
    e_lat = models.FloatField()
    e_lon = models.FloatField()
    miles = models.FloatField()
    road_order = models.PositiveSmallIntegerField()
    reference_speed = models.FloatField()
    def __unicode__(self):
            return self.tmc

class TMC_Here(models.Model):
    tmc = models.CharField(max_length = 9, primary_key = True)
    state = models.CharField(max_length = 2)
    county = models.CharField(max_length = 20)
    miles = models.FloatField()
    road_number = models.CharField(max_length = 20)
    road_name = models.CharField(max_length = 100)
    lat = models.FloatField();
    lon = models.FloatField();
    DIRECTION_CHOICES = (('N', 'Northbound'),('S', 'Southbound'),('E', 'Eastbound'),('W', 'Westbound'))
    direction = models.CharField(max_length=1, choices = DIRECTION_CHOICES)
    coordinates = models.TextField();
    def __unicode__(self):
            return self.tmc

class TMC_Here_data(models.Model):
    tmc = models.ForeignKey(TMC_Here)
    date = models.DateField(db_index = True)
    epoch = models.PositiveSmallIntegerField()
    tt_all = models.PositiveSmallIntegerField(default = 0)
    tt_pv = models.PositiveSmallIntegerField(default = 0) # passenger vehicles
    tt_ft = models.PositiveSmallIntegerField(default = 0) # freight trucks
    spd_all = models.FloatField(default = -1.0)
    spd_pv = models.FloatField(default = -1.0)
    spd_ft = models.FloatField(default = -1.0)

class TMC_Ritis(models.Model):
    tmc = models.CharField(max_length = 9, primary_key = True)
    road_name = models.CharField(max_length = 50, db_index = True)
    DIRECTION_CHOICES = (('N', 'Northbound'),('S', 'Southbound'),('E', 'Eastbound'),('W', 'Westbound'))
    direction = models.CharField(max_length=1, choices = DIRECTION_CHOICES)
    intersection = models.CharField(max_length = 100)
    state = models.CharField(max_length = 2)
    county = models.CharField(max_length = 20)
    zip = models.CharField(max_length = 5)
    s_lat = models.FloatField(); # start lat
    s_lon = models.FloatField(); # start lon
    e_lat = models.FloatField(); # end lat
    e_lon = models.FloatField(); # end lon
    miles = models.FloatField()
    road_order = models.PositiveSmallIntegerField();
    coordinates = models.TextField();
    class Meta:
        index_together = [['road_name','road_order'],]
    def __unicode__(self):
            return self.tmc

class TMC_real_time(models.Model):
    tmc = models.CharField(max_length = 9, primary_key = True)
    road = models.CharField(max_length = 50, db_index = True)
    DIRECTION_CHOICES = (('N', 'Northbound'),('S', 'Southbound'),('E', 'Eastbound'),('W', 'Westbound'))
    direction = models.CharField(max_length=1, choices = DIRECTION_CHOICES)
    intersection = models.CharField(max_length = 100)
    state = models.CharField(max_length = 2)
    county = models.CharField(max_length = 20)
    zip = models.CharField(max_length = 5)
    s_lat = models.FloatField()
    s_lon = models.FloatField()
    e_lat = models.FloatField()
    e_lon = models.FloatField()
    miles = models.FloatField()
    road_order = models.PositiveSmallIntegerField()
    reference = models.FloatField()
    speed = models.FloatField()
    average = models.FloatField()
    ttm = models.FloatField() # travel time in minute
    congestion = models.PositiveSmallIntegerField() # congestion level
    def __unicode__(self):
            return self.tmc

class TMC_data(models.Model):
    tmc = models.ForeignKey(TMC)
    date = models.DateField()
    time = models.TimeField()
    speed = models.FloatField()
    avg_speed = models.FloatField()
    travel_time = models.FloatField()
    class Meta:
        index_together = [['tmc','date','time'],]

class Incidents(models.Model):
    eventid = models.CharField(max_length = 15, primary_key = True)
    st_rt_no = models.PositiveSmallIntegerField()
    sr = models.CharField(max_length = 255)
    cause = models.CharField(max_length = 25)
    status = models.CharField(max_length = 20)
    close_date = models.DateField()
    close_time = models.TimeField()
    open_date = models.DateField()
    open_time = models.TimeField()
    s_lat = models.FloatField()
    s_lon = models.FloatField()
    e_lat = models.FloatField()
    e_lon = models.FloatField()
    geoJson = models.TextField()
    def __unicode__(self):
        return self.eventid
    class Meta:
        index_together = [['close_date','close_time'],]

# models for weather
class Weather(models.Model):
    county = models.CharField(max_length = 20, primary_key = True)
    state = models.CharField(max_length = 2)
    api = models.CharField(max_length = 30)
    update_time = models.TimeField()
    geoJson = models.TextField()
    weather = models.TextField()
    def __unicode__(self):
        return self.county

# model for weather zipcode areas
class Weather_zipcode(models.Model):
    zipcode = models.CharField(max_length = 5, primary_key = True) # five digits zipcode
    geoJson = models.TextField()
    def __unicode__(self):
        return self.zipcode

class Weather_zipcode_data(models.Model):
    zipcode = models.ForeignKey(Weather_zipcode)
    query_time = models.DateTimeField()
    code = models.PositiveSmallIntegerField()
    timestamp = models.TextField()
    temp = models.SmallIntegerField() # temperature Farenheit
    text = models.TextField()
    def __unicode__(self):
        return self.zipcode.zipcode + "\n" + self.timestamp


# ============================================== Models for Transit BEGIN =============================================
class Route(models.Model):
    route_id = models.CharField(max_length = 10, primary_key = True)
    agency_id = models.CharField(max_length = 10)
    short_name = models.CharField(max_length = 5, unique = True)
    long_name = models.CharField(max_length = 50)
    inbound_stops_geoJson = models.TextField()
    route_type = models.CharField(max_length = 1)
    outbound_stops_geoJson = models.TextField()
    inbound_geoJson = models.TextField()
    outbound_geoJson = models.TextField()
    def __unicode__(self):
        return self.route_id

class Route_dict(models.Model):
    short_name = models.CharField(max_length = 5, primary_key = True)
    route_number_in_APCAVL = models.CharField(max_length = 5, unique = True)
    def __unicode__(self):
        return self.short_name

class GTFS_calendar(models.Model):
    service_id = models.CharField(max_length=50)
    monday = models.CharField(max_length=1)
    tuesday = models.CharField(max_length=1)
    wednesday = models.CharField(max_length=1)
    thursday = models.CharField(max_length=1)
    friday = models.CharField(max_length=1)
    saturday = models.CharField(max_length=1)
    sunday = models.CharField(max_length=1)
    start_date = models.DateField()
    end_date = models.DateField()
    GTFS = models.CharField(max_length=50)
    def __unicode__(self):
        return self.GTFS + ": " + self.service_id
    class Meta:
        unique_together = (("service_id", "GTFS"),)

class Trip(models.Model):
    route = models.ForeignKey(Route)
    service_id = models.CharField(max_length = 35)
    trip_id = models.CharField(max_length = 50)
    headsign = models.CharField(max_length = 100)
    direction_id = models.CharField(max_length = 1)
    block_id = models.CharField(max_length = 20)
    shape_id = models.CharField(max_length = 10)
    GTFS = models.CharField(max_length=50)
    def __unicode__(self):
        return self.trip_id
    class Meta:
        index_together = [['route', 'GTFS', 'direction_id'],]
        unique_together = (("trip_id", "GTFS"),)

class Stop(models.Model):
    stop_id = models.CharField(max_length = 10, primary_key = True)
    code = models.CharField(max_length = 10)
    name = models.CharField(max_length = 60)
    geoJson = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()
    zone_id = models.CharField(max_length = 5)
    def __unicode__(self):
        return self.stop_id

class Stop_time(models.Model):
    trip_id = models.CharField(max_length = 50)
    arrival_time = models.CharField(max_length = 8)
    departure_time = models.CharField(max_length = 8)
    stop_id = models.CharField(max_length = 10)
    stop_sequence = models.PositiveSmallIntegerField()
    pickup_type = models.CharField(max_length = 1)
    drop_off_type = models.CharField(max_length = 1)
    GTFS = models.CharField(max_length=50)
    def __unicode__(self):
        return self.arrival_time
    class Meta:
        index_together = [['trip_id', 'stop_id', 'GTFS'], ['stop_id','GTFS']]
        unique_together = (("trip_id", "stop_sequence", "GTFS"),)

class Stop_route(models.Model):
    stop_id =  models.CharField(max_length = 10, db_index = True)
    route_id =  models.CharField(max_length = 10, db_index = True)
    direction = models.CharField(max_length = 1)
    order = models.PositiveSmallIntegerField()

class Transit_shape(models.Model):
    shape_id = models.CharField(max_length = 10, db_index = True)
    lat = models.FloatField()
    lon = models.FloatField()
    sequence = models.PositiveIntegerField()
    def __unicode__(self):
        return self.shape_id + '' + self.sequence

class Transit_data(models.Model):
    dow = models.CharField(max_length = 1)
    dir = models.CharField(max_length = 1)
    route = models.CharField(max_length = 4)
    tripa = models.CharField(max_length = 4)
    blocka = models.CharField(max_length = 10)
    vehnoa = models.CharField(max_length = 4)
    date = models.DateField()
    stopa = models.PositiveSmallIntegerField()
    qstopa = models.CharField(max_length = 8)
    aname = models.TextField()
    hour = models.PositiveSmallIntegerField()
    minute = models.PositiveSmallIntegerField()
    second = models.PositiveSmallIntegerField()
    dhour = models.PositiveSmallIntegerField()
    dminute = models.PositiveSmallIntegerField()
    dsecond = models.PositiveSmallIntegerField()
    on_num = models.PositiveSmallIntegerField()
    off_num = models.PositiveSmallIntegerField()
    load_num = models.PositiveSmallIntegerField()
    dlmiles = models.FloatField()
    dlmin = models.FloatField()
    dlpmls = models.FloatField()
    dwtime = models.FloatField()
    delta = models.PositiveSmallIntegerField()
    schtim = models.PositiveSmallIntegerField()
    schdev = models.FloatField()
    srtime = models.FloatField()
    artime = models.FloatField()
    def __unicode__(self):
        return self.route + ' ' + self.tripa
    # class Meta:
    #     index_together = [["route", "dir", "qstopa", "date"],]
# =============================================== Models for Transit END ===============================================

class GIS_links(models.Model):
    link_id = models.CharField(max_length = 20, primary_key = True)
    miles = models.FloatField()
    from_node = models.CharField(max_length = 10)
    to_node = models.CharField(max_length = 10)
    s_lon = models.FloatField()
    s_lat = models.FloatField()
    e_lon = models.FloatField()
    e_lat = models.FloatField()
    geometries = models.TextField()
    def __unicode__(self):
        return self.link_id

class Parking_lots(models.Model):
    lot_id = models.PositiveSmallIntegerField(primary_key = True)
    name = models.CharField(max_length = 100)
    max_spots = models.PositiveSmallIntegerField()
    lon = models.FloatField()
    lat = models.FloatField()
    def __unicode__(self):
        return self.lot_id

class Real_time_tmc_data(models.Model):
    tmc = models.CharField(max_length = 9)
    date = models.DateField()
    time = models.TimeField()
    speed = models.FloatField()
    avg_speed = models.FloatField()
    ref_speed = models.FloatField()
    delta = models.SmallIntegerField()
    score = models.SmallIntegerField()
    c_value = models.SmallIntegerField()
    travel_time = models.FloatField() #in minutes
    cong_level = models.SmallIntegerField() # congestion level
    def __unicode__(self):
            return self.tmc


class Closed_roads(models.Model):
    perm_no = models.PositiveIntegerField(primary_key=True)
    type = models.SmallIntegerField()
    location = models.CharField(max_length=100)
    neighbor = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    note = models.CharField(max_length=500)
    start_date = models.DateField()  #in format mm/dd/yy
    end_date = models.DateField()
    wkday_hrs = models.CharField(max_length=30)  #store the closure hours on weekdays, split by"," two fields as a time range
    wkend_hrs = models.CharField(max_length=30)
    wkday_hrsfull = models.CharField(max_length=50)  #store the closure hours on weekdays, split by"," two fields as a time range
    wkend_hrsfull = models.CharField(max_length=50)

    backfill = models.BooleanField(default=True)
    coordinate = models.BooleanField(default=True)
    traffic_ctl = models.BooleanField(default=True)
    closure = models.BooleanField(default=True)
    onelane = models.BooleanField(default=True)
    postno = models.BooleanField(default=True)
    pat = models.BooleanField(default=True)
    ctl_plan = models.BooleanField(default=True)
    emerge = models.BooleanField(default=True)
    buss = models.BooleanField(default=True)
    ped_clean = models.BooleanField(default=True)
    off_police = models.BooleanField(default=True)
    flagper = models.BooleanField(default=True)
    penndot = models.BooleanField(default=True)
    rdline = models.CharField(max_length=50000)

    def __unicode__(self):
        return self.perm_no

class Counts_sensors(models.Model):
    sid = models.CharField(max_length = 10, primary_key = True)
    coordinates = models.TextField()
    counts = models.TextField()

    def __unicode__(self):
        return self.sid

class Counts_sensors_links(models.Model):
    sid = models.CharField(max_length = 10, primary_key = True)
    coordinates = models.TextField()

    def __unicode__(self):
        return self.sid
# class Counts(models.Model):
#     sid = models.ForeignKey(Counts_sensors)
#     counts = models.TextField()

# ==================== Models for Permission start ================== #
class Permissions(models.Model):
    class Meta:
        permissions = (
            ('test_pc', 'test_permission'),
            ('perm_weather', 'permission to access weather section'),
            ('perm_camera', 'permission to access camera section'),
            ('perm_count', 'permission to access traffic counts section'),
            ('perm_travel', 'permission to access travel time and trip planner section'),
            ('perm_incident', 'permission to access incidents section'),
            ('perm_ev_station', 'permission to access EV stations section'),
            ('perm_download', 'permission to access download section'),
            ('perm_transit', 'permission to access transit section'),
            ('perm_parking', 'permission to access parking section'),
            ('perm_crash', 'permission to access crash section'),
            ('perm_closure', 'permission to access closure section')
        )


# ==================== Models for Permission end   ================== #





