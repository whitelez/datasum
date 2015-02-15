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

class Street(models.Model):
    sid = models.CharField(max_length = 20, primary_key = True)
    street_name = models.CharField(max_length = 100)
    coordinate = models.TextField()
    def __unicode__(self):
        return self.sid

class Streetparking(models.Model):
    street = models.ForeignKey(Street)
    date = models.DateField(db_index = True)
    occupancy = models.TextField()
    def __unicode__(self):
	    return self.date.ctime()


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

class Weather(models.Model):
    county = models.CharField(max_length = 20, primary_key = True)
    state = models.CharField(max_length = 2)
    api = models.CharField(max_length = 30)
    update_time = models.TimeField()
    geoJson = models.TextField()
    weather = models.TextField()
    def __unicode__(self):
        return self.county

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

class Trip(models.Model):
    route_id = models.ForeignKey(Route)
    service_id = models.CharField(max_length = 35)
    trip_id = models.CharField(max_length = 50, primary_key = True)
    headsign = models.CharField(max_length = 100)
    direction_id = models.CharField(max_length = 1)
    block_id = models.PositiveIntegerField()
    shape_id = models.CharField(max_length = 10)
    def __unicode__(self):
        return self.trip_id

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
    trip_id = models.ForeignKey(Trip)
    arrival_time = models.CharField(max_length = 8)
    departure_time = models.CharField(max_length = 8)
    stop_id = models.ForeignKey(Stop)
    stop_sequence = models.PositiveSmallIntegerField()
    pickup_type = models.CharField(max_length = 1)
    drop_off_type = models.CharField(max_length = 1)
    def __unicode__(self):
        return self.arrival_time

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
    blocka = models.CharField(max_length = 6)
    vehnoa = models.CharField(max_length = 4)
    date = models.DateField(db_index = True)
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

class GIS_links(models.Model):
    link_id = models.CharField(max_length = 20, primary_key = True)
    miles = models.FloatField()
    from_node = models.PositiveSmallIntegerField()
    to_node = models.PositiveSmallIntegerField()
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




    
    



