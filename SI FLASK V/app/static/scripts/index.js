//Filtrado por todo, descricion

var current_filters = new Set();

$('document').ready(function(){
    $("#mySearchBox").on("keyup", function() {
        var value = $(this).val().toLowerCase();
        $(".movies_container .movie_preview").filter(function() {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $("input:checkbox").on("change", function() {
        var value = $(this).val().toLowerCase();
        if($(this).is(':checked') == true) {
            current_filters.add(value);
        }
        else {
            current_filters.delete(value);
        }
        filter_all(current_filters);
    });

});

function filter_all(texts) {
    if(!texts) return;
    $(".movies_container .movie_preview").filter(function() {
        let show = true;
        for(let value of texts) {
            if($(this).text().toLowerCase().indexOf(value) < 0) {
                show = false;
                break;
            }
        }
        $(this).toggle(show);
    });
}
