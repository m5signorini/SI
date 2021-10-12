

$('document').ready(visitors_init);

function visitors_init() {
    setInterval(update_visitors, 3000);
}

function update_visitors() {
    $.get('/num_visitors', response => {
        // Success callback:
        $('#num_visitors').text('Número de visitantes: ' + response);
    })
}
