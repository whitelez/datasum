
  // create a map in the "map" div, set the view to a given place and zoom
	var map = L.map('map').setView([40.4407937, -80.0029874], 15);
	
	// add an OpenStreetMap tile layer
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
  
	var geoJSONLayer;

	function parkingMarkerStyle(occupancy){
		var c;
		if (occupancy>0.45){
			c='red';
		}else if(occupancy>0.3){
			c='yellow';
		}
		else{
			c='green';
		}
		return {
			radius: 8,
			fillColor: c,
			color: c,
			weight: 1,
			opacity: 1,
			fillOpacity: 0.8
		};
	}
	

function showOcp()
{
	var e = document.getElementById("weekdays").value;
    var f = document.getElementById("time").value;
	
	
	var radios = document.getElementsByName('ampm');


	for (var i = 0, length = radios.length; i < length; i++) {
		if (radios[i].checked) {
			// do whatever you want with the checked radio
			var g = 24*parseInt(e)+parseInt(f)+parseInt(radios[i].value);

			// only one radio can be logically checked, don't check the rest
			break;
		}
	}
	
	if(map.hasLayer(geoJSONLayer)){
		map.removeLayer(geoJSONLayer);
	}
	
	geoJSONLayer = L.geoJson(terminals,{
		pointToLayer:function(feature, latlng){
			return L.circleMarker(latlng, parkingMarkerStyle(feature.properties.occupancy[g]));
		},
		onEachFeature:function(feature, layer){
			if (feature.properties && feature.properties.terminalID && feature.properties.occupancy) {
				layer.bindPopup("Terminal : " + feature.properties.terminalID + "<br/>Occupancy : " + feature.properties.occupancy[g]);
			}
		}
		
	}).addTo(map);
	

}
