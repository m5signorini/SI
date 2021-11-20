/*Movie Page*/

$('document').ready(init);

function init() {
    const see_more_button = document.querySelector('.see_more');
    const text = document.querySelector('.text');

    see_more_button.addEventListener('click', (e) =>{
        text.classList.toggle('show-more');
        if(see_more_button.innerText === 'Ver más'){
            see_more_button.innerText = 'Ocultar';
        }else{
            see_more_button.innerText = 'Ver más';
        }
    });

    $('input[type="checkbox"]').on('change', function() {
       $('input[type="checkbox"]').not(this).prop('checked', false);
    });

    $('.purchase_button').on('click', add_to_cart);

}

function add_to_cart() {
    $.get('add_to_cart/' + $('input:checked').val());
}
