

$('document').ready(visitors_init);

var interv;

function visitors_init() {
    interv = setInterval(update_visitors, 3000);
    update_visitors();
}

function update_visitors() {
    $.ajax({
        url: '/num_visitors',
        type: 'GET',
        success: function(response){
            $('#num_visitors').text('Número de visitantes: ' + response);
        },
        error: function(data) {
            console.log('Error al obtener número de visitas, desactivando intervalo');
            clearInterval(interv);
        }
    });
}
