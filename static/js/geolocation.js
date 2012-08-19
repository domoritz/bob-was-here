$(document).bind("pageinit", function() {
	var tapin = $('#tapin').text();
	
	if (tapin && tapin != '') {
		navigator.geolocation.getCurrentPosition (function(pos) {
			var latitude = pos.coords.latitude;
			var longitude = pos.coords.longitude;
			$("#latitude").text (latitude);
			$("#longitude").text (longitude);
			$.post("/geolocation", {latitude: latitude, longitude: longitude, tapin: tapin})
		});
	}
})