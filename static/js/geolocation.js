$(document).bind("pageinit", init)

function init() {
	navigator.geolocation.getCurrentPosition (geolocation);
}

function geolocation(pos) {
	var tapin = $('#tapin').text();
	var latitude = pos.coords.latitude;
	var longitude = pos.coords.longitude;
	$("#latitude").text (latitude);
	$("#longitude").text (longitude);
	$.post("/geolocation", {latitude: latitude, longitude: longitude, tapin: tapin})
}

