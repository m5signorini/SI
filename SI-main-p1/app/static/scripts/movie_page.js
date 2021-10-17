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
    })
}
