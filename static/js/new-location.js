
$(document).bind("pageinit", init)

function init() {
	$('#new-location').on("click", new_location);
}

function new_location() {
	var slug = $('#slug').val();
	var name = $('#name').val();
	window.location = "/new-location/" + slug + "/" + name;
	return false;
}

