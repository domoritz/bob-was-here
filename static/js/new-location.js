
$(document).bind("pageinit", init)

function init() {
	$('#new-location').on("click", new_location);
}

function new_location() {
	var slug = $('#slug').val();
	var name = $('#name').val();
	$.post("/new-location/" + slug, {name: name, slug: slug}, function() {
		window.location("/location/" + slug);
	});
	return false;
}

