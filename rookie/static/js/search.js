var url;

function search_records(){
	url  = 'http://localhost:5000/rookie/search?q=';
	if ($("#search_terms").val() != ""){
        url = url + $("#search_terms").val();
    }
    console.log(url);
    window.location = url;
}

$("#search_button").on("click", function(){
   search_records();
});

$("body").keypress(function(e) {
  if(e.which == 13) {
    search_records();
  }
});