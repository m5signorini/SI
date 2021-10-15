// Esperar a que todos los elementos del DOM estén cargados
$('document').ready(init);

function init() {
    $('.product_remove').on('click', remove_item);
    $('.copies_in_cart').on('input', update_number);
}

function update_number() {
    let updated = this;
    $.ajax({
        url: '/cart_update/' + $(this).val() + '/' + $(this).parent().parent().children('.product_id').text(),
        type: 'GET',
        success: function(response){
            aux=(response.split("/"));
            $(updated).parent().parent().children('.products_total_price').text(aux[0] + " $");
            $('.total_price_calculation').text(aux[1] + " $");
        },
        error: function(data) {
            console.log('Error al obtener numero de puntos');
            clearInterval(interv);
        }
    });
}

function remove_item(){
    $.ajax({
        url: '/cart_update/0/' + $(this).parent().children('.product_id').text(),
        type: 'GET',
        success: function(response){
            aux=(response.split("/"))
            $('.total_price_calculation').text(aux[1] + " $");
        },
        error: function(data) {
            console.log('Error al obtener numero de puntos');
            clearInterval(interv);
        }
    });
    $(this).parent().remove();
}