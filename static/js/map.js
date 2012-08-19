$(function() {
	var map = L.map('map').setView([51.505, -0.09], 13);

	L.tileLayer('http://{s}.tile.cloudmade.com/ad132e106cd246ec961bbdfbe0228fe8/997/256/{z}/{x}/{y}.png', {
	    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
	    maxZoom: 18
	}).addTo(map);

	for(index in positions) {
		L.marker(positions[index]).addTo(map);
	}

	var polygon = L.polyline(positions, {fill: false}).addTo(map);

	map.fitBounds(polygon.getBounds());

	//map.locate({setView: true, maxZoom: 16});

	function onLocationFound(e) {
	    var radius = e.accuracy / 2;

	    L.marker(e.latlng).addTo(map)
	        .bindPopup("You are within " + radius + " meters from this point").openPopup();

	    L.circle(e.latlng, radius).addTo(map);
	}

	map.on('locationfound', onLocationFound);

	function onLocationError(e) {
	    alert(e.message);
	}

	map.on('locationerror', onLocationError);

});