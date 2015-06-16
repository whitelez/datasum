from django.conf.urls import patterns, url
from traffic import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^parking/$', views.parking, name='parking'),
    url(r'^camera/$', views.camera, name='camera'),
    url(r'^ajaxtest/$',views.ajaxtest, name='ajaxtest'),
    url(r'^parking_geoJSON/$', views.street_parking_geojson, name='parking_geoJSON' ),
    url(r'^parking_geoJSON_prediction/$', views.street_parking_geojson_prediction, name='parking_geoJSON_prediction'),

    url(r'^count/$', views.count, name='count'),

    url(r'^weather/$', views.weather, name='weather'),
    url(r'^get_county_weather/$', views.get_county_weather, name = 'get_county_weather'),
    url(r'^get_weather/$', views.get_weather, name = 'get_weather'),

    url(r'^ev_stations/$', views.ev_stations, name='ev_stations'),

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++  Travel  +++++++++++++++++++++++++++++++++++++++++++++++++++++++
    url(r'^travel_time/$', views.travel_time, name='travel_time'),
    url(r'^travel_time_new/$', views.travel_time_new, name='travel_time_new'),
    url(r'^get_node_info_for_one_corridor/$', views.get_node_info, name='get_node_info'),
    url(r'^get_spc_traveltime/$', views.get_spctraveltime, name='get_spctraveltime'),
    url(r'^get_spc_traveltimeformanyyears/$', views.get_spctraveltimeformanyyears, name='get_spctraveltimeformanyyears'),
    url(r'^get_spc_years/$', views.get_spcyears, name='get_spcyears'),
    url(r'^travel_time_corridorafter2013/$', views.travel_time_corridorafter2013, name='travel_time_corridorafter2013'),
    url(r'^get_node_info_2013to2015/$', views.get_node_info_2013to2015, name='get_node_info_2013to2015'),
    url(r'^get_spc_traveltime_2013to2015/$', views.get_spctraveltime_2013to2015, name='get_spctraveltime2013to2015'),
    url(r'^get_travel_time/$', views.get_travel_time, name='get_travel_time'),
    url(r'^get_travel_time_prediction/$', views.get_travel_time_prediction, name='get_travel_time_prediction'),
    url(r'^get_road_tmc/$', views.get_road_tmc, name='get_road_tmc'),
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++  Transit  +++++++++++++++++++++++++++++++++++++++++++++++++++++++
    url(r'^get_route/$', views.get_route, name='get_route'),
    url(r'^get_stops/$', views.get_stops, name='get_stops'),
    url(r'^transit_data/$', views.transit_data, name='transit_data'),

    url(r'^transit_ontimeperformance_byroute/$', views.transit_ontimeperformance_byroute, name='transit_ontimeperformance_byroute'),
    url(r'^transit_ontimeperformance_bystop/$', views.transit_ontimeperformance_bystop, name='transit_ontimeperformance_bystop'),
    url(r'^transit_waitingtime_byroute/$', views.transit_waitingtime_byroute, name='transit_waitingtime_byroute'),
    url(r'^transit_waitingtime_bystop/$', views.transit_waitingtime_bystop, name='transit_waitingtime_bystop'),
    url(r'^transit_crowding/$', views.transit_crowding, name='transit_crowding'),
    url(r'^transit_busbunching/$', views.transit_bunching, name='transit_busbunching'),
    url(r'^transit_bustraveltime/$', views.transit_bustraveltime, name='transit_bustraveltime'),

    url(r'^transit_metrics/$', views.transit_metrics, name='transit_metrics'),
    url(r'^transit_metrics_route_range/$', views.transit_metrics_route_range, name='transit_metrics_route_range'),
    url(r'^transit_metrics_stop_routes/$', views.transit_metrics_stop_routes, name='transit_metrics_stop_routes'),
    url(r'^transit_metrics_range_routes/$', views.transit_metrics_range_routes, name='transit_metrics_range_routes'),
    url(r'^get_stop_routes/$', views.get_stop_routes, name='get_stop_route'),

    url(r'^bus_real_time/$', views.bus_real_time, name='bus_real_time'),
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  End  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    url(r'^incidents/$', views.incidents, name='incidents'),
    url(r'^get_incidents_rcrs/$', views.get_incidents_rcrs, name='get_incidents_rcrs'),

    url(r'^download/$', views.download, name='download'),

    url(r'^routing/$', views.routing, name='routing'),
    url(r'^routing_path/$', views.routing_path, name='routing_path'),

    url(r'^parking_lots/$', views.parking_lots, name='parking_lots'),
    url(r'^test/$', views.test, name='test'),
    url(r'^get_incidents_rcrs_area/$', views.get_incidents_rcrs_area, name='get_incidents_rcrs_area'),
    url(r'^real_time_incidents_rcrs/$', views.real_time_incidents_rcrs, name='real_time_incidents_rcrs'),
    url(r'^real_time_tmc/$', views.real_time_tmc, name='real_time_tmc'),
    url(r'^real_time_tt/$', views.real_time_tt, name='real_time_tt'),
    url(r'^tmc_gis/$', views.TMC_GIS, name='TMC_GIS'),

    url(r'^devices/$', views.device_render, name='devices'),

#counts
    url(r'^sensors_counts/$', views.sensors_counts, name='sensors_counts'),

#SGYang
    url(r'^road_closure/$', views.closure, name='closure'),
    url(r'^get_road_closure_query/$', views.get_road_closure_query, name='get_road_closure_query'),

)
