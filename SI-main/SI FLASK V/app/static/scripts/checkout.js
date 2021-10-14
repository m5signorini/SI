// Esperar a que todos los elementos del DOM estén cargados
$('document').ready(init);

function init() {
    $('#points').on('change', points_input);
}

function points_input() {
    $.ajax({
        url: '/num_points/' + $('#points').val(),
        type: 'GET',
        success: function(response){
            $('#points_balance').text(response);
        },
        error: function(data) {
            console.log('Error al obtener numero de puntos');
            clearInterval(interv);
        }
    });
}
