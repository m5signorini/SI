//Filtrado por todo, descricion
/*
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
*/

/* Visualizacion dinamica de la lista topactors */
var topactors_list = null;
var topactors_filt = null;

$('document').ready(function() {
    // Note that the selection may include more than one
    // useful for future improvements
    topactors_list = $('.topactors_list');
    topactors_filt = $('.topactors_filter').find('select');
    topactors_filt.on('change', update_topactors);
    // Initial call
    topactors_filt.change();
});

function update_topactors(e) {
    let target = $(e.target);
    let list = target.parent().next();
    let genre = target.val();
    let table = target.next().find('a');
    
    $.get(
        '/get_topactors',
        {genre: genre},
        function(response) {
            if(!response || response.length === undefined) {
                console.log('Error al obtener top actores');
                return;
            }
            table.attr('href', '/top_actors/'+genre);
            empty_topactors(list);
            populate_topactors(list, response);
        });
}


function populate_topactors(list, data) {
    // Expecting to receive as data a list of objects containing:
    // actor, numero, debut, pelicula, director.
    // List is the dom object jquery selection to append the data.
    let elems = []
    for(let datum of data) {
        elems.push(generate_topactor_element(datum))
    }
    list.append(elems);
}

function empty_topactors(list) {
    list.empty();
}

function generate_topactor_element(data) {

    let elem     = $('<div>', {class: 'topactors_elem'});
    let actor    = $('<p>', {html: 'Actor: '});
    let num      = $('<p>', {html: 'Numero: '});
    let debut    = $('<p>', {html: 'Debut: '});
    let film     = $('<p>', {html: 'Pelicula: '});
    let director = $('<p>', {html: 'Director: '});

    actor.append($('<strong>', {html: data['actor']}))
    num.append($('<strong>', {html: data['num']}))
    debut.append($('<strong>', {html: data['debut']}))
    director.append($('<strong>', {html: data['director']}))
    film.append($('<strong></strong>'))
            .append($('<a>', {html: data['film'], href: '/movie_page/'+data['movieid']}));

    elem.append([actor, num, debut, film, director]);
    return elem;
}